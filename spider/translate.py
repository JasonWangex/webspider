# coding=utf-8
from Queue import Empty, Full, Queue
from multiprocessing import Process
from multiprocessing.managers import BaseManager, Value
from dispacher import local_shutdown_listener, shutdown_listener
from Domain import User

import pickle
import redis
import time
import threading
import user_dao
import config


class QueueManager(BaseManager):
    pass


def start_master(port):
    all_uid_list = []
    shutdown = Value('i', False)

    redis_client = redis.StrictRedis(host='1daf5146eb844741.m.cnsha.kvstore.aliyuncs.com', port=6379,
                                     password=config.password)

    QueueManager.register('get_shutdown', callable=lambda: shutdown)

    manager = QueueManager(address=('', port), authkey=config.auth_key)
    manager.start()

    shutdown = manager.get_shutdown()

    print '/////// 系统启动 - 主节点 ///////'

    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)
    print '>>>>>>> 初始化 总解析uid列表 完毕'

    # 清洗uid
    clean_thread = threading.Thread(target=clean_uid, args=(all_uid_list, shutdown))
    clean_thread.start()

    # 数据报告
    report_thread = threading.Thread(target=report, args=(all_uid_list, redis_client, shutdown,))
    report_thread.start()

    shutdown_listener_thread = threading.Thread(target=shutdown_listener, args=(shutdown,))
    shutdown_listener_thread.start()
    shutdown_listener_thread.join()
    report_thread.join()
    # 关闭服务
    before_shut_down(all_uid_list)
    print '>>>>>>> 系统将在 20 秒后关闭<<<<<<<'
    for i in range(19, 0, -1):
        print ">>>>>>> 系统将在 ", i, " 秒后关闭<<<<<<<"
        time.sleep(1)
    manager.shutdown()


# 仅仅将trash uid存入redis
def start_trash_queue_manager(port, localShutdown):
    print '/////// 系统启动 - RUL节点 ///////'
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
    Process(target=translate_uid,
            args=(uid_queue, redis_client, localShutdown,)).start()

    local_shutdown_listener(localShutdown)


def translate_trash_uid(uid_with_trash_queue, redis_client, localShutdown):
    while not localShutdown.value:
        try:
            uid = uid_with_trash_queue.get(timeout=5)
            redis_client.lpush("uid_with_trash", uid)
        except Empty:
            continue


def translate_uid(uid_queue, redis_client, localShutdown, ):
    while not localShutdown.value:
        try:
            uid = redis_client.blpop("cleaned_uid", timeout=30)
            uid_queue.put(uid, timeout=15)
        except Full:
            continue


def fill_user_queue_process(user_waiting_resolve_url_queue, shutdown):
    current_user = User()
    while not shutdown.get():
        current_user = user_dao.get_next_user(current_user)
        time.sleep(0.01)
        try:
            if current_user is not None:
                user_waiting_resolve_url_queue.put(current_user.id, timeout=5)
        except Full:
            current_user.id -= 1
            continue


def report(all_uid_list, redis_client, shutdown):
    last_length = 0
    while not shutdown.get():
        time.sleep(10)
        if shutdown.get():
            break
        current_length = len(all_uid_list)
        print "\n////////////数据报告////////////"
        print ">>>> 待解析 uid 列表: ", redis_client.llen("cleaned_uid")
        print ">>>> 待清洗 uid 列表: ", redis_client.llen("cleaned_uid")
        print ">>>> 总解析 uid 列表: ", current_length
        print ">>>> 总解析 uid 速率: ", (current_length - last_length) / 10, "个/秒"
        print "////////////数据报告////////////\n"
        last_length = current_length


def clean_uid(all_uid_list, redis_client, shutdown):
    while not shutdown.get():
        try:
            uid_with_trash = redis_client.blpop(timeout=15)
        except redis.TimeoutError:
            continue
        if uid_with_trash not in all_uid_list:
            redis_client.lpush(uid_with_trash)
            all_uid_list.append(uid_with_trash)


def before_shut_down(all_uid_list):
    print '>>>>>> 信息存储中'
    with open('all_uid_list', 'wb') as f_all_uid:
        pickle.dump(all_uid_list, file=f_all_uid)
    print '>>>>>> 总解析uid列表 存储完毕'
    print '\n/////////系统关闭！/////////'
