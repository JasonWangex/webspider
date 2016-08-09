import User
import config
import download
import resolver
import persistence
from Queue import Queue

shut_down = False

# while not shut_down:
# def init_spider():
url_queue = Queue(50)
all_uid_list = {}
content = download.get_content(config.first_url)
user = resolver.resolve_for_user(content)
# get followers
msg = download.get_followers(hash_id=user.hashId, page=1)
uids = resolver.resolve_for_uid(msg)
for uid in filter(lambda x: x not in all_uid_list, uids):
    url_queue.put(uids)

user = download.get_content(resolver.get_url_by_uid(url_queue.get()))
