# coding=utf-8
from Queue import Empty, Full, Queue
from multiprocessing import Process
from multiprocessing.managers import BaseManager, Value
from dispacher import local_shutdown_listener
from Domain import User

import redis
import time
import threading
import user_dao
import config


class QueueManager(BaseManager):
    pass


def start_clean(port):
    localShutdown = Value('i', False)

    redis_client = redis.StrictRedis(host='1daf5146eb844741.m.cnsha.kvstore.aliyuncs.com', port=6379,
                                     password=config.password)

    print '/////// 系统启动 - 主节点 ///////'

    # 清洗uid
    clean_thread = threading.Thread(target=clean_uid, args=(redis_client, localShutdown))
    clean_thread.start()

    # 数据报告
    report_thread = threading.Thread(target=report, args=(redis_client, localShutdown,))
    report_thread.start()

    local_shutdown_listener(localShutdown)
    report_thread.join()

    print '>>>>>>> 系统将在  5  秒后关闭<<<<<<<'
    for i in range(4, 0, -1):
        time.sleep(1)
        print ">>>>>>> 系统将在 ", i, " 秒后关闭<<<<<<<"


# 仅仅将trash uid存入redis
def start_trash_queue_manager(port, localShutdown):
    print '/////// 系统启动 - 转发节点 ///////'
    user_waiting_resolve_url_queue = Queue(20)
    uid_with_trash_queue = Queue(500)
    uid_queue = Queue(50)

    QueueManager.register('get_user_waiting_resolve_url_queue', callable=lambda: user_waiting_resolve_url_queue)
    QueueManager.register('get_uid_with_trash_queue', callable=lambda: uid_with_trash_queue)
    QueueManager.register('get_uid_queue', callable=lambda: uid_queue)

    # 在网络注册redis client 与 manager
    redis_client = redis.StrictRedis(host='1daf5146eb844741.m.cnsha.kvstore.aliyuncs.com', port=6379,
                                     password=config.password)
    manager = QueueManager(address=('', port), authkey=config.auth_key)
    manager.start()

    user_waiting_resolve_url_queue = manager.get_user_waiting_resolve_url_queue()
    uid_with_trash_queue = manager.get_uid_with_trash_queue()
    uid_queue = manager.get_uid_queue()

    Process(target=translate_trash_uid,
            args=(uid_with_trash_queue, redis_client, localShutdown,)).start()
    Process(target=translate_uid,
            args=(uid_queue, redis_client, localShutdown,)).start()
    Process(target=fill_user_queue_process,
            args=(user_waiting_resolve_url_queue, localShutdown,)).start()
    Process(target=queue_report,
            args=(uid_queue, localShutdown,)).start()
    while not localShutdown.value and raw_input() != 'exit':
        continue
    localShutdown.value = True
    time.sleep(10)
    while not uid_queue.empty():
        uid = uid_queue.get()
        redis_client.lpush('cleaned_uid', uid)
    while not uid_with_trash_queue.empty():
        uid = uid_with_trash_queue.get()
        redis_client.lpush('uid_with_trash', uid)


def translate_trash_uid(uid_with_trash_queue, redis_client, localShutdown):
    while not localShutdown.value:
        try:
            uids = uid_with_trash_queue.get(timeout=5)
            for uid in uids:
                redis_client.lpush("uid_with_trash", uid)
        except Empty:
            continue


def translate_uid(uid_queue, redis_client, localShutdown,):
    while not localShutdown.value:
        try:
            uid = redis_client.brpop("cleaned_uid", timeout=30)
            if uid[1].find("[u'") != -1:
                continue
            uid_queue.put(uid[1], timeout=60)
        except Full:
            print uid[1], "is lost"
            continue


def fill_user_queue_process(user_waiting_resolve_url_queue, localShutdown):
    current_user = User()
    while not localShutdown.value:
        current_user = user_dao.get_next_user(current_user)
        time.sleep(0.01)
        try:
            if current_user is not None:
                user_waiting_resolve_url_queue.put(current_user.id, timeout=5)
        except Full:
            current_user.id -= 1
            continue


def report(redis_client, localShutdown):
    last_length = 0
    while not localShutdown.value:
        time.sleep(10)
        if localShutdown.value:
            break
        current_length = redis_client.scard('all_uid_list')
        print "\n////////////数据报告////////////"
        print ">>>> 待解析 uid 列表: ", redis_client.llen("cleaned_uid")
        print ">>>> 待清洗 uid 列表: ", redis_client.llen("uid_with_trash")
        print ">>>> 总解析 uid 列表: ", current_length
        print ">>>> 总解析 uid 速率: ", (current_length - last_length) / 10.0, "个/秒"
        print "////////////数据报告////////////\n"
        last_length = current_length


def queue_report(uid_queue, localShutdown):
    while not localShutdown.value:
        time.sleep(10)
        if localShutdown.value:
            break
        print "\n////////////数据报告////////////"
        print ">>>> 待解析 uid 列表: ", uid_queue.qsize()
        print "////////////数据报告////////////\n"


def clean_uid(redis_client, localShutdown):
    while not localShutdown.value:
        uid_with_trash = redis_client.brpop("uid_with_trash", timeout=5)
        if uid_with_trash is None or uid_with_trash[1].find("[u'") != -1:
            continue
        if not redis_client.sismember('all_uid_list', uid_with_trash[1]):
            redis_client.sadd("all_uid_list", uid_with_trash[1])
            redis_client.lpush("cleaned_uid", uid_with_trash[1])

