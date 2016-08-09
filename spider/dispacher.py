# coding=utf-8
import User
import config
import download
import resolver
from persistence import user_dao
import time
import threading
from Queue import Queue

shut_down = False

# while not shut_down:
# def init_spider():
uid_set = set()

uid_set.add(config.first_uid)
user_queue = Queue(200)
content_queue = Queue(200)
all_uid_list = []
user_dao.start_session()


# content = download.get_content(config.first_url)
# user = download.get_content(resolver.get_url_by_uid(url_queue.get()))


def is_uid_set_full():
    return len(uid_set) >= 100


def is_uid_set_empty():
    return len(uid_set) == 0


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
            while content_queue.full():
                time.sleep(0.5)
            content_queue.put(content)


def resolve_thread():
    global uid_set
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        while content_queue.empty():
            time.sleep(0.5)
        content = content_queue.get()
        try:
            user = resolver.resolve_for_user(content)
            print '开始解析', user.uid
            user_dao.save_or_update(user)
        except AttributeError:
            pass


def followee_url_thread():
    global all_uid_list
    global uid_set
    current_user = None
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
                while is_uid_set_full():
                    time.sleep(0.5)
                print '将 ', uid, ' 加入对列'
                uid_set.add(uid)
        current_user.needGetFollowees = False
        current_user.getFollowees = max_followee_page
        user_dao.save_or_update(current_user)
    user_dao.save_or_update(current_user)


def follower_url_thread():
    global all_uid_list
    global uid_set
    current_user = None
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
            for uid in filter(lambda x: lambda x: x is not None and x not in all_uid_list, uids):
                while is_uid_set_full():
                    time.sleep(0.5)
                print '将 ', uid, ' 加入对列'
                uid_set.add(uid)
        current_user.needGetFollowers = False
        current_user.getFollowers = max_follower_page
        user_dao.save_or_update(current_user)
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
    while True:
        for thr in thrs:
            if not thr.isAlive():
                thr.start()
    time.sleep(5)


threads = []
for i in range(1, 5):
    threads.append(threading.Thread(target=download_thread))

t2 = threading.Thread(target=resolve_thread)
t3 = threading.Thread(target=followee_url_thread)
t4 = threading.Thread(target=follower_url_thread)
t6 = threading.Thread(target=report)
threads.append(t2)
threads.append(t3)
threads.append(t4)
threads.append(t6)
# t2.start()
# t3.start()
# t4.start()
# t6.start()
threading.Thread(target=listener(threads)).start()
