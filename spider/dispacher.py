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
uid_queue = Queue(200)
user_queue = Queue(200)
content_queue = Queue(200)
all_uid_list = []
user_dao.start_session()

content = download.get_content(config.first_url)


#
# user = download.get_content(resolver.get_url_by_uid(url_queue.get()))


def download_thread():
    global uid_queue
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        if not uid_queue.empty():
            uid = uid_queue.get()
            url = resolver.get_url_by_uid(uid)
            all_uid_list.append(uid)
            content = download.get_content(url)
            while user_queue.full():
                content_queue.put(content)
                time.sleep(0.5)
        else:
            time.sleep(0.5)


def resolve_thread():
    global uid_queue
    global content_queue
    global shut_down
    global all_uid_list
    while not shut_down:
        while content_queue.empty():
            time.sleep(0.5)
        user = resolver.resolve_for_user(content_queue.get())
        user_dao.save_or_update(user)


def followee_url_thread():
    global all_uid_list
    global uid_queue
    user = user_dao.get_user_for_followees()
    max_followee_page = 0 if user.followees == 0 else user.followees % 20 + 1
    while user.getFollowees < max_followee_page:
        msg = download.get_followers(hash_id=user.hashId, page=user.getFollowees)
        uids = resolver.resolve_for_uid(msg)
        for uid in filter(lambda x: x not in all_uid_list, uids):
            while uid_queue.full():
                time.sleep(0.5)
            uid_queue.put(uid)


def follower_url_thread():
    global all_uid_list
    global uid_queue
    user = user_dao.get_user_for_followees()
    max_follower_page = 0 if user.followers == 0 else user.followers % 20 + 1
    while user.getFollowers < max_follower_page:
        msg = download.get_followers(hash_id=user.hashId, page=user.getFollowers)
        uids = resolver.resolve_for_uid(msg)
        for uid in filter(lambda x: x not in all_uid_list, uids):
            while uid_queue.full():
                time.sleep(0.5)
            uid_queue.put(uid)


t1 = threading.Thread(download_thread)
t5 = threading.Thread(download_thread)
t2 = threading.Thread(resolve_thread)
t3 = threading.Thread(followee_url_thread)
t4 = threading.Thread(follower_url_thread)
