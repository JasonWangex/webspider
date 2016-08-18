# coding=utf-8
import time
from Queue import Full, Empty

from multiprocessing.managers import BaseManager, Value

import config
import resolver
import download
import threading
from Domain import Failed
from persistence import user_dao
from persistence import failed_dao
from multiprocessing import Process, Lock
from multiprocessing import Queue
import persistence
import cookies

try:
    import cPickle as pickle
except ImportError:
    import pickle

failedCount = 0
download_lock = Lock()


def download_process(uid_queue, operator, shutdown, localShutdown):
    global failedCount
    while not (shutdown.get() or localShutdown.value):
        if failedCount > 5:
            print '/////////下载被封禁！/////////'
            time.sleep(1)
            print '>>>>>> 正在尝试重启....'
            time.sleep(10)
            if operator:
                if not download.restart():
                    print '/////////重启失败！/////////'
                    localShutdown.value = True
                    break
            else:
                failedCount = 0
                time.sleep(10)

        try:
            uid = uid_queue.get(timeout=5)
        except Empty:
            continue
        url = resolver.get_url_by_uid(uid)
        content = download.get_content(url)
        threading.Thread(target=resolve_thread, args=(content,)).start()
    if operator:
        download.shut_down()


def resolve_thread(content):
    global failedCount
    try:
        user = resolver.resolve_for_user(content)
        print '解析>>>>>>', user.uid
        user_dao.save_or_update(user)
        failedCount = 0
    except AttributeError:
        print '///////////解析失败////////////'
        failed = Failed()
        failed.content = content
        failed_dao.save(failed)
        failedCount += 1


def followee_url_process(uid_with_trash_queue, operator, shutdown, localShutdown):
    global failedCount
    while not (shutdown.get() or localShutdown.value):
        current_user = user_dao.get_user_for_followees()
        if current_user is None:
            continue

        max_followee_page = 0 if current_user.followees == 0 else current_user.followees / 20 + 1
        while current_user.getFollowees < max_followee_page and not (shutdown.get() or localShutdown.value):
            if failedCount > 5 and operator:
                print '///////URL 被封禁///////'
                time.sleep(1)
                print '>>>>>> 正在尝试重启...'
                if not download.restart():
                    print '/////////重启失败！/////////'
                    localShutdown.value = True
                    current_user.needGetFollowees = True
                    user_dao.save_or_update(current_user)
                    break
                else:
                    failedCount = 0
                    time.sleep(10)

            msg = download.get_followees(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            current_user.needGetFollowees = False
            user_dao.save_or_update(current_user)
            print ">>>>> URL下载成功 - Followee ", current_user.getFollowees
            uids = resolver.resolve_for_uids(msg)
            if len(uids) == 0:
                failedCount += 1
            else:
                failedCount = 0

            for uid in uids:
                try:
                    uid_with_trash_queue.put(uid, timeout=10)
                except Full:
                    if shutdown.get() or localShutdown.value:
                        current_user.needGetFollowees = True
                        user_dao.save_or_update(current_user)
                        return
                    else:
                        print ">>>>>", uid, "is lost!"
                        continue
        current_user.needGetFollowees = False
        current_user.getFollowees = max_followee_page
        user_dao.save_or_update(current_user)
    if operator:
        download.shut_down()


def follower_url_process(uid_with_trash_queue, operator, follower_lock, shutdown, localShutdown):
    global failedCount
    while not (shutdown.get() or localShutdown.value):
        current_user = user_dao.get_user_for_followers()
        if current_user is None:
            continue

        max_follower_page = 0 if current_user.followers == 0 else current_user.followers / 20 + 1
        while current_user.getFollowers < max_follower_page and not (shutdown.get() or localShutdown.value):
            if failedCount > 5 and operator:
                print '///////URL 被封禁///////'
                time.sleep(1)
                print '>>>>>> 正在尝试重启...'
                if not download.restart():
                    print '/////////重启失败！/////////'
                    localShutdown.value = True
                    break
                else:
                    failedCount = 0
                    time.sleep(10)

            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowers)

            current_user.getFollowers += 1
            user_dao.save_or_update(current_user)

            print ">>>>> URL下载成功 - Follower ", current_user.getFollowers
            uids = resolver.resolve_for_uids(msg)
            for uid in uids:
                try:
                    uid_with_trash_queue.put(uid, timeout=10)
                except Full:
                    if shutdown.get() or localShutdown.value:
                        return
                    else:
                        print ">>>>>", uid, "is lost!"
                        continue
        current_user.needGetFollowers = False
        current_user.getFollowers = max_follower_page
        user_dao.save_or_update(current_user)
    if operator:
        download.shut_down()


def report(uid_queue, uid_with_trash_queue, all_uid_list, shutdown):
    while not shutdown.get():
        time.sleep(10)
        if shutdown.get():
            break
        print "\n////////////数据报告////////////"
        print ">>>> 待解析 uid 列表: ", uid_queue.qsize()
        print ">>>> 待清洗 uid 列表: ", uid_with_trash_queue.qsize()
        print ">>>> 总解析 uid 列表: ", len(all_uid_list)
        print "////////////数据报告////////////\n"


def shutdown_listener(shutdown):
    while raw_input() != 'exit':
        continue
    shutdown.set(True)


def local_shutdown_listener(localShutdown):
    while not localShutdown.value and raw_input() != 'exit':
        continue
    localShutdown.value = True


def start_process(procs):
    for proc in procs:
        proc.start()


def clean_uid(uid_queue, uid_with_trash_queue, all_uid_list, shutdown):
    while not shutdown.get():
        try:
            waiting_clean_uid = uid_with_trash_queue.get(timeout=5)
        except Empty:
            continue
        if waiting_clean_uid not in all_uid_list:
            uid_queue.put(waiting_clean_uid)
            all_uid_list.append(waiting_clean_uid)


def before_shut_down(all_uid_list, uid_queue, uid_with_trash_queue):
    print '>>>>>> 信息存储中'
    with open('all_uid_list', 'wb') as f_all_uid:
        pickle.dump(all_uid_list, file=f_all_uid)
    print '>>>>>> 总解析uid列表 存储完毕'

    with open('uid_queue', 'wb') as f_uid_queue:
        # queue 无法序列化, 只能转成list
        uid_list = []
        while not uid_queue.empty():
            uid = uid_queue.get(timeout=15)
            uid_list.append(uid)
        pickle.dump(uid_list, file=f_uid_queue)
    print '>>>>>> 待解析uid列表 存储完毕'

    with open('uid_with_trash', 'wb') as f_uid_with_trash_queue:
        uid_list = []
        while not uid_with_trash_queue.empty():
            try:
                uid = uid_with_trash_queue.get(timeout=5)
            except Empty:
                continue
            uid_list.append(uid)
        pickle.dump(uid_list, file=f_uid_with_trash_queue)
    print '>>>>>> 待清洗uid列表 存储完毕'
    print '\n/////////系统关闭！/////////'


class QueueManager(BaseManager):
    pass


def start_master(port):
    all_uid_list = []
    uid_queue = Queue(800)
    uid_with_trash_queue = Queue(1500)
    shutdown = Value('i', False)
    followee_url_lock = Lock()
    follower_url_lock = Lock()

    QueueManager.register('get_uid_queue', callable=lambda: uid_queue)
    QueueManager.register('get_uid_with_trash_queue', callable=lambda: uid_with_trash_queue)
    QueueManager.register('get_shutdown', callable=lambda: shutdown)
    QueueManager.register('get_followee_url_lock', callable=lambda: followee_url_lock)
    QueueManager.register('get_follower_url_lock', callable=lambda: follower_url_lock)

    manager = QueueManager(address=('', port), authkey=config.auth_key)
    manager.start()

    uid_queue = manager.get_uid_queue()
    uid_with_trash_queue = manager.get_uid_with_trash_queue()
    shutdown = manager.get_shutdown()

    print '/////// 系统启动 - 主节点 ///////'

    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)
    print '>>>>>>> 初始化 总解析uid列表 完毕'

    clean_thread = threading.Thread(target=clean_uid, args=(uid_queue, uid_with_trash_queue, all_uid_list, shutdown))
    clean_thread.start()
    report_thread = threading.Thread(target=report, args=(uid_queue, uid_with_trash_queue, all_uid_list, shutdown))
    report_thread.start()

    with open('uid_queue', 'rb') as f_uid_queue:
        if f_uid_queue.readline() != "":
            f_uid_queue.seek(0)
            uid_list = pickle.load(f_uid_queue)
            if len(uid_list) == 0:
                uid_queue.put(config.first_uid)

            for uid in uid_list:
                try:
                    uid_queue.put(uid, timeout=60)
                except Full:
                    pass

    print '>>>>>>> 初始化 待解析uid列表 完毕'

    with open('uid_with_trash', 'rb') as f_uid_with_trash:
        if f_uid_with_trash.readline() != "":
            f_uid_with_trash.seek(0)
            uid_list = pickle.load(f_uid_with_trash)
            for uid in uid_list:
                try:
                    uid_with_trash_queue.put(uid, timeout=60)
                except Full:
                    pass
    print '>>>>>>> 初始化 待清洗uid列表 完毕'

    shutdown_listener_thread = threading.Thread(target=shutdown_listener, args=(shutdown,))
    shutdown_listener_thread.start()
    shutdown_listener_thread.join()
    report_thread.join()
    # 关闭服务
    before_shut_down(all_uid_list, uid_queue, uid_with_trash_queue)
    print '>>>>>>> 系统将在 20 秒后关闭<<<<<<<'
    for i in range(20, 1, -1):
        print ">>>>>>> 系统将在 ", i, " 秒后关闭<<<<<<<"
        time.sleep(1)
    manager.shutdown()


def start_download(address, port, localShutdown):
    print '/////// 系统启动 - 下载节点 ///////'
    persistence.start_session()
    cookies.start_session()
    QueueManager.register('get_uid_queue')
    QueueManager.register('get_shutdown')

    manager = QueueManager(address=(address, port), authkey=config.auth_key)
    manager.connect()

    uid_queue = manager.get_uid_queue()
    shutdown = manager.get_shutdown()

    process = []
    download.start_download()
    process.append(Process(target=download_process, args=(uid_queue, True, shutdown, localShutdown,)))
    for i in range(1):
        process.append(Process(target=download_process, args=(uid_queue, False, shutdown, localShutdown,)))
    start_process(process)
    local_shutdown_listener(localShutdown)


def start_url_resolver(address, port, localShutdown):
    persistence.start_session()
    cookies.start_session()
    print '/////// 系统启动 - RUL节点 ///////'

    QueueManager.register('get_uid_with_trash_queue')
    QueueManager.register('get_shutdown')
    QueueManager.register('get_followee_url_lock')
    QueueManager.register('get_follower_url_lock')

    manager = QueueManager(address=(address, port), authkey=config.auth_key)
    manager.connect()

    download.start_download()

    uid_with_trash_queue = manager.get_uid_with_trash_queue()
    shutdown = manager.get_shutdown()
    # follower_lock = manager.get_follower_url_lock()

    process = [
        # Process(target=followee_url_process, args=(uid_with_trash_queue, True, followee_lock, shutdown, localShutdown,)),
        # Process(target=follower_url_process, args=(uid_with_trash_queue, True, follower_lock, shutdown, localShutdown,)),
        Process(target=followee_url_process, args=(uid_with_trash_queue, True, shutdown, localShutdown,))]
    start_process(process)

    local_shutdown_listener(localShutdown)
