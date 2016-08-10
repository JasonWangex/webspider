import threading
import time
from sqlalchemy.orm import session
import persistence
from spider import config
from spider import download
from spider import resolver
from persistence import user_dao
from persistence import failed_dao
from Domain import Failed
from multiprocessing import Process
from multiprocessing import Queue
import os

#
# print 'Process (%s) start...' % os.getpid()
# pid = os.fork()
# if pid == 0:
#     print 'I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid())
# else:
#     print 'I (%s) just created a child process (%s).' % (os.getpid(), pid)
# un = u'\U0001f60c'
# st = un.encode('utf-8')
# print st
#
# persistence.start_session()
# failed = Failed()
# failed.content = un
# failed_dao.save(failed)
# t1 = time.time()
# all_l = range(0, 44003153)
# t2 = time.time()
#
# t3 = time.time()
# a = 1 in all_l
# t4 = time.time()
# b = 654556 in all_l
# t5 = time.time()
# c = 240031529 in all_l
# t6 = time.time()
#
# print t2 - t1, t3 - t2, t4 - t3, t5 - t4, t6 - t5
# content = download.get_content("https://www.zhihu.com/people/tian-zai-yang/about")
# user = resolver.resolve_for_user(content)
# print user
#
# for i in range(9, 0, -1):
#     print i

i = 1

que = Queue()
que.put(i)


def count_star(x):
    for j in range(1, 10):
        x += 1
        print x


# Process(target=count_star, args=(i,)).start()
# Process(target=count_star, args=(i,)).start()
count_star(i)
print i