# import threading
# import time
# from sqlalchemy.orm import session
#
# from spider import config
# from spider import download
# from spider import resolver
# from persistence import user_dao
# # content = download.get_content(url=resolver.get_url_by_uid(config.first_uid))
# import spider.User
#
# # f = open('temp', 'r')
# # # f.write(content)
# # user_dao.start_session()
# #
# # user = resolver.resolve_for_user(f.read())
# # user_dao.save_or_update(user)
# # user = user_dao.get_user_for_followees()
# # print user
# shut_down = False
#
#
# def listener(thrs):
#     for thr in thrs:
#         thr.start()
#     while True:
#         for thr in thrs:
#             if not thr.isAlive():
#                 print thr.name, "is shutdown"
#         break
#         time.sleep(1)
#
#
# def t(jjj):
#     while True:
#         print "i'm alive>>>>", jjj
#         time.sleep(1)
#         if shut_down:
#             break
#
#
# def t11():
#     global shut_down
#     while True:
#         time.sleep(1)
#         if raw_input() is not None:
#             shut_down = True
#
#
# threads = []
# for i in range(1, 5):
#     thr = threading.Thread(target=t, args=(i,))
#     threads.append(thr)
#
# # t2 = threading.Thread(target=t, kwargs=11)
# # t3 = threading.Thread(target=t(12))
# # t4 = threading.Thread(target=t(13))
# # t6 = threading.Thread(target=t(14))
# # threads.append(t2)
# # threads.append(t3)
# # threads.append(t4)
# # threads.append(t6)
# # t2.start()
# # t3.start()
# # t4.start()
# # t6.start()
# th = threading.Thread(target=t11)
# threads.append(th)
# threading.Thread(target=listener(threads)).start()
