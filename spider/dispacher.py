# coding=utf-8
import time
import config
import download
import resolver
import threading
import persistence
from Domain import Failed
from persistence import user_dao
from persistence import failed_dao
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value
from multiprocessing import Pool

try:
    import cPickle as pickle
except ImportError:
    import pickle


def init_spider():
    shutdown = Value('b', False)
    all_uid_list = []
    uid_with_trash = Queue(500)
    uid_queue = Queue(500)
    uid_queue.put(config.first_uid)

    print '///////////系统初始化///////////'
    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)
    print '>>>>>>> 初始化 总解析uid列表 完毕'

    with open('uid_with_trash', 'rb') as f_uid_with_trash:
        if f_uid_with_trash.readline() != "":
            f_uid_with_trash.seek(0)
            uid_list = pickle.load(f_uid_with_trash)
            for uid in uid_list:
                uid_with_trash.put(uid)
    print '>>>>>>> 初始化 待清洗uid列表 完毕'

    with open('uid_queue', 'rb') as f_uid_queue:
        if f_uid_queue.readline() != "":
            f_uid_queue.seek(0)
            uid_queue.get(timeout=15)
            uid_list = pickle.load(f_uid_queue)
            for uid in uid_list:
                uid_queue.put(uid)
    print '>>>>>>> 初始化 待解析uid列表 完毕'
    print '///////////初始化完毕///////////\n'
    return [
        all_uid_list,
        uid_queue,
        uid_with_trash,
        shutdown,
    ]


def download_process(uid_queue, shutdown):
    while not shutdown.value:
        uid = uid_queue.get(timeout=15)
        url = resolver.get_url_by_uid(uid)
        content = download.get_content(url)
        threading.Thread(target=resolve_thread, args=(content,)).start()


def resolve_thread(content):
    try:
        user = resolver.resolve_for_user(content)
        print '解析>>>>>>', user.uid
        user_dao.save_or_update(user)
    except AttributeError:
        print '///////////解析失败////////////'
        failed = Failed()
        failed.content = content
        failed_dao.save(failed)


def followee_url_process(uid_with_trash_queue, shutdown):
    while not shutdown.value:
        current_user = user_dao.get_user_for_followees()
        if current_user is None:
            continue

        max_followee_page = 0 if current_user.followees == 0 else current_user.followees % 20 + 1
        while current_user.getFollowees < max_followee_page:
            msg = download.get_followees(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uids(msg)
            for uid in uids:
                uid_with_trash_queue.put(uid)
            user_dao.save_or_update(current_user)
        current_user.needGetFollowees = False
        current_user.getFollowees = max_followee_page
        user_dao.save_or_update(current_user)


def follower_url_process(uid_with_trash_queue, shutdown):
    while not shutdown.value:
        current_user = user_dao.get_user_for_followers()
        if current_user is None:
            continue

        max_follower_page = 0 if current_user.followers == 0 else current_user.followers % 20 + 1
        while current_user.getFollowers < max_follower_page:
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowers)
            current_user.getFollowers += 1
            uids = resolver.resolve_for_uids(msg)

            for uid in uids:
                uid_with_trash_queue.put(uid)
            user_dao.save_or_update(current_user)

        current_user.needGetFollowers = False
        current_user.getFollowers = max_follower_page
        user_dao.save_or_update(current_user)


def report(uid_queue, uid_with_trash_queue, all_uid_list, shutdown):
    while not shutdown.value:
        time.sleep(10)
        if shutdown.value:
            return
        print "\n////////////数据报告////////////"
        print ">>>> 待解析 uid 列表: ", uid_queue.qsize()
        print ">>>> 待清洗 uid 列表: ", uid_with_trash_queue.qsize()
        print ">>>> 总解析 uid 列表: ", len(all_uid_list)
        print "////////////数据报告////////////\n"


def listener(procs, shutdown):
    for proc in procs:
        proc.start()
    while raw_input() != 'exit':
        continue
    shutdown.value = True
    for proc in procs:
        proc.join()

    for proc in procs:
        if proc.is_alive():
            print proc.name, 'is not shutdown'
            print '\n/////////系统关闭失败！/////////'


def clean_uid(uid_queue, uid_with_trash_queue, all_uid_list, shutdown):
    while not shutdown.value:
        waiting_clean_uid = uid_with_trash_queue.get(timeout=15)
        if waiting_clean_uid not in all_uid_list:
            uid_queue.put(waiting_clean_uid)
            all_uid_list.append(waiting_clean_uid)


def start_process(all_uid_list, uid_queue, uid_with_trash_queue, shutdown):
    process = []
    for i in range(1, 3):
        process.append(Process(target=download_process, args=(uid_queue, shutdown,)))

    process.append(Process(target=followee_url_process, args=(uid_with_trash_queue, shutdown,)))
    process.append(Process(target=follower_url_process, args=(uid_with_trash_queue, shutdown,)))
    clean_thread = threading.Thread(target=clean_uid, args=(uid_queue, uid_with_trash_queue, all_uid_list, shutdown))
    main_thread = threading.Thread(target=listener, args=(process, shutdown,))
    report_thread = threading.Thread(target=report, args=(uid_queue, uid_with_trash_queue, all_uid_list, shutdown))
    clean_thread.start()
    report_thread.start()
    main_thread.start()
    main_thread.join()
    after_shut_down(all_uid_list, uid_queue, uid_with_trash_queue)


def after_shut_down(all_uid_list, uid_queue, uid_with_trash_queue):
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

    with open('uid_queue', 'wb') as f_uid_with_trash_queue:
        uid_list = []
        while not uid_with_trash_queue.empty():
            uid = uid_with_trash_queue.get(timeout=15)
            uid_list.append(uid)
        pickle.dump(uid_list, file=f_uid_with_trash_queue)
    print '>>>>>> 待清洗uid列表 存储完毕'
    print '\n/////////系统关闭！/////////'


# spider begin
# command is
#         type(m master,d only download,c only control, dc down and control)
#         port(integer)
if __name__ == '__main__':
    # commands = sys.argv
    persistence.start_session()
    init_param = init_spider()
    start_process(all_uid_list=init_param[0],
                  uid_queue=init_param[1],
                  uid_with_trash_queue=init_param[2],
                  shutdown=init_param[3])
