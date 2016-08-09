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
uid_queue.put(config.first_uid)
user_queue = Queue(200)
content_queue = Queue(200)
all_uid_list = []
user_dao.start_session()


# content = download.get_content(config.first_url)
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
    current_user = None
    while not shut_down:
        current_user = user_dao.get_user_for_followees()
        max_followee_page = 0 if current_user.followees == 0 else current_user.followees % 20 + 1
        while current_user.getFollowees < max_followee_page:
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uid(msg)
            for uid in filter(lambda x: x not in all_uid_list, uids):
                while uid_queue.full():
                    time.sleep(0.5)
                uid_queue.put(uid)
            current_user.needGetFollowees = False
            current_user.getFollowees = max_followee_page
            user_dao.save_or_update(current_user)
    user_dao.save_or_update(current_user)


def follower_url_thread():
    global all_uid_list
    global uid_queue
    current_user = None
    while not shut_down:
        current_user = user_dao.get_user_for_followees()
        max_follower_page = 0 if current_user.followers == 0 else current_user.followers % 20 + 1
        while current_user.getFollowers < max_follower_page:
            msg = download.get_followers(hash_id=current_user.hashId, page=current_user.getFollowers)
            current_user.getFollowees += 1
            uids = resolver.resolve_for_uid(msg)
            for uid in filter(lambda x: x not in all_uid_list, uids):
                while uid_queue.full():
                    time.sleep(0.5)
                uid_queue.put(uid)
            current_user.needGetFollowers = False
            current_user.getFollowers = max_follower_page
            user_dao.save_or_update(current_user)
    user_dao.save_or_update(current_user)


t1 = threading.Thread(download_thread)
t5 = threading.Thread(download_thread)
t2 = threading.Thread(resolve_thread)
t3 = threading.Thread(followee_url_thread)
t4 = threading.Thread(follower_url_thread)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()