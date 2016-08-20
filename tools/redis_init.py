# coding=utf-8
import pickle
import redis

redis_client = redis.StrictRedis(host='1daf5146eb844741.m.cnsha.kvstore.aliyuncs.com', port=6379, password='')


with open('uid_queue', 'rb') as f_uid_queue:
    if f_uid_queue.readline() != "":
        f_uid_queue.seek(0)
        uid_list = pickle.load(f_uid_queue)
        for uid in uid_list:
            redis_client.lpush("cleaned_uid", uid)
print '>>>>>>> 初始化 待解析uid列表 完毕'

with open('uid_with_trash', 'rb') as f_uid_with_trash:
    if f_uid_with_trash.readline() != "":
        f_uid_with_trash.seek(0)
        uid_list = pickle.load(f_uid_with_trash)
        for uid in uid_list:
            redis_client.lpush('uid_with_trash', uid)
print '>>>>>>> 初始化 待清洗uid列表 完毕'
