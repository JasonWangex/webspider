# coding=utf-8
import config
import download
import resolver
from persistence import user_dao
import time
import threading
from Queue import Queue

try:
    import cPickle as pickle
except ImportError:
    import pickle

shut_down = False

uid_set = set()
uid_set.add(config.first_uid)
user_queue = Queue(200)
content_queue = Queue(200)
all_uid_list = []
user_dao.start_session()


def is_uid_set_full():
    return len(uid_set) >= 100


def is_uid_set_empty():
    return len(uid_set) == 0


def init_spider():
    global uid_set
    global content_queue
    global all_uid_list

    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)

    with open('content_queue', 'rb') as f_content_queue:
        if f_content_queue.readline() != "":
            f_content_queue.seek(0)
            content_list = pickle.load(f_content_queue)
            for content in content_list:
                content_queue.put(content, block=True)

    with open('uid_set', 'rb') as f_uid_set:
        if f_uid_set.readline() != "":
            f_uid_set.seek(0)
            uid_set = pickle.load(f_uid_set)


def download_thread():
    global uid_set
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        time.sleep(0.5)
        if not is_uid_set_empty():
            uid = uid_set.pop()
            url = resolver.get_url_by_uid(uid)
            all_uid_list.append(uid)
            print '开始获取 ', uid
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
            print '开始解析', user.uid
            user_dao.save_or_update(user)
        except AttributeError:
            pass


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
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uids(msg)
            for uid in filter(lambda x: x is not None and x not in all_uid_list, uids):
                while is_uid_set_full() and not shut_down:
                    time.sleep(0.5)
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
        current_user = user_dao.get_user_for_followees()
        if current_user is None:
            continue
        max_follower_page = 0 if current_user.followers == 0 else current_user.followers % 20 + 1
        while current_user.getFollowers < max_follower_page:
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowers)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uids(msg)
            for uid in filter(lambda x: x is not None and x not in all_uid_list, uids):
                while is_uid_set_full() and not shut_down:
                    time.sleep(0.5)
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
        print "\n=========================监====控============================"
        print "\nuid_queue: ", len(uid_set)
        print "\ncontent_queue: ", content_queue.qsize()
        print "\nall_uid_list: ", len(all_uid_list)
        print "\n============================================================"


def listener(thrs):
    global shut_down
    for thr in thrs:
        thr.start()
    while raw_input() != 'exit':
        continue
    shut_down = True
    time.sleep(10)
    for thr in thrs:
        if thr.isAlive():
            print thr.name, 'is not shutdown'
    with open('all_uid_list', 'wb') as f_all_uid:
        pickle.dump(all_uid_list, file=f_all_uid)

    with open('content_queue', 'wb') as f_content_queue:
        # queue 无法序列化, 只能转成list
        content_list = []
        while not content_queue.empty():
            content = content_queue.get(block=True)
            content_list.append(content)
        pickle.dump(content_list, file=f_content_queue)

    with open('uid_set', 'wb') as f_uid_set:
        pickle.dump(uid_set, file=f_uid_set)

# spider begin
init_spider()
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
