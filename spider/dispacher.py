# coding=utf-8
import time
import config
import download
import resolver
import threading
import persistence
from Queue import Queue
from Domain import Failed
from persistence import user_dao
from persistence import failed_dao

try:
    import cPickle as pickle
except ImportError:
    import pickle

shut_down = False

uid_set = set()
uid_set.add(config.first_uid)
content_queue = Queue(200)
all_uid_list = []
persistence.start_session()
uid_in_lock = threading.Lock()
uid_out_lock = threading.Lock()


def is_uid_set_full():
    return len(uid_set) >= 100


def is_uid_set_empty():
    return len(uid_set) == 0


def init_spider():
    global uid_set
    global content_queue
    global all_uid_list

    print '///////////系统初始化///////////'
    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)
    print '>>>>>>> 初始化 all_uid_list 完毕'

    with open('content_queue', 'rb') as f_content_queue:
        if f_content_queue.readline() != "":
            f_content_queue.seek(0)
            content_list = pickle.load(f_content_queue)
            for content in content_list:
                content_queue.put(content, block=True)
    print '>>>>>>> 初始化 content_queue 完毕'

    with open('uid_set', 'rb') as f_uid_set:
        if f_uid_set.readline() != "":
            f_uid_set.seek(0)
            uid_set = pickle.load(f_uid_set)
    print '>>>>>>> 初始化 uid_set 完毕'
    print '///////////初始化完毕///////////\n'


def download_thread():
    global uid_set
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        time.sleep(0.5)
        if not is_uid_set_empty():
            with uid_out_lock:
                uid = uid_set.pop()
            url = resolver.get_url_by_uid(uid)
            all_uid_list.append(uid)
            content = download.get_content(url)
            content_queue.put(content, block=True)


def resolve_thread():
    global uid_set
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        content = content_queue.get(block=True)
        try:
            user = resolver.resolve_for_user(content)
            print '解析>>>>>>', user.uid
            user_dao.save_or_update(user)
        except AttributeError:
            print '///////////解析失败////////////'
            failed = Failed()
            failed.content = content
            failed_dao.save(failed)


def followee_url_thread():
    global all_uid_list
    global uid_set
    while not shut_down:
        time.sleep(0.5)
        current_user = user_dao.get_user_for_followees()
        if current_user is None:
            continue

        max_followee_page = 0 if current_user.followees == 0 else current_user.followees % 20 + 1
        while current_user.getFollowees < max_followee_page:
            msg = download.get_followees(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uids(msg)
            for uid in filter(lambda x: x is not None, uids):
                while is_uid_set_full() and not shut_down:
                    time.sleep(0.5)
                if uid in all_uid_list:
                    continue
                with uid_in_lock:
                    uid_set.add(uid)
            if shut_down:
                user_dao.save_or_update(current_user)
                return
        current_user.needGetFollowees = False
        current_user.getFollowees = max_followee_page
        user_dao.save_or_update(current_user)


def follower_url_thread():
    global all_uid_list
    global uid_set
    while not shut_down:
        time.sleep(0.5)
        current_user = user_dao.get_user_for_followers()
        if current_user is None:
            continue
        max_follower_page = 0 if current_user.followers == 0 else current_user.followers % 20 + 1
        while current_user.getFollowers < max_follower_page:
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowers)
            current_user.getFollowers += 1
            uids = resolver.resolve_for_uids(msg)
            for uid in filter(lambda x: x is not None, uids):
                while is_uid_set_full() and not shut_down:
                    time.sleep(0.5)
                if uid in all_uid_list:
                    continue
                with uid_in_lock:
                    uid_set.add(uid)
            if shut_down:
                user_dao.save_or_update(current_user)
                return
        current_user.needGetFollowers = False
        current_user.getFollowers = max_follower_page
        user_dao.save_or_update(current_user)


def report():
    global uid_set
    global content_queue
    global all_uid_list
    while not shut_down:
        time.sleep(10)
        if shut_down:
            return
        print "\n////////////数据报告////////////"
        print ">>>> uid_queue: ", len(uid_set)
        print ">>>> content_queue: ", content_queue.qsize()
        print ">>>> all_uid_list: ", len(all_uid_list)
        print "////////////数据报告////////////\n"


def listener(thrs):
    global shut_down
    for thr in thrs:
        thr.start()
    while raw_input() != 'exit':
        continue
    shut_down = True
    time.sleep(1)
    print '系统将在 10 秒之后进入关闭流程！'
    for i in range(9, 0, -1):
        time.sleep(1)
        print i

    for thr in thrs:
        if thr.isAlive():
            print thr.name, 'is not shutdown'
    after_shut_down()
    print '\n/////////系统关闭！/////////'


def start_thread():
    threads = []
    for i in range(1, 5):
        threads.append(threading.Thread(target=download_thread))

    t2 = threading.Thread(target=resolve_thread, name='resolve_thread')
    t3 = threading.Thread(target=followee_url_thread, name='followee_url_thread')
    t4 = threading.Thread(target=follower_url_thread, name='follower_url_thread')
    t6 = threading.Thread(target=report, name='report')
    threads.append(t2)
    threads.append(t3)
    threads.append(t4)
    threads.append(t6)
    threading.Thread(target=listener, args=(threads,)).start()


def after_shut_down():
    print '>>>>>> 信息存储中'
    with open('all_uid_list', 'wb') as f_all_uid:
        pickle.dump(all_uid_list, file=f_all_uid)
    print '>>>>>> all_uid_list 存储完毕'

    with open('content_queue', 'wb') as f_content_queue:
        # queue 无法序列化, 只能转成list
        content_list = []
        while not content_queue.empty():
            content = content_queue.get(block=True)
            content_list.append(content)
        pickle.dump(content_list, file=f_content_queue)
    print '>>>>>> content_queue 存储完毕'

    with open('uid_set', 'wb') as f_uid_set:
        pickle.dump(uid_set, file=f_uid_set)
    print '>>>>>> uid_set 存储完毕'


# spider begin
if __name__ == '__main__':
    init_spider()
    start_thread()
