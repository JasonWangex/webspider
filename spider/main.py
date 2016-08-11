# coding=utf-8
import sys
from Queue import Full
from multiprocessing import Process

from spider import config
from spider import dispacher
from spider.dispacher import after_shut_down, master_process, download_process, daemon_process, followee_url_process, \
    follower_url_process
from multiprocessing import Queue
from multiprocessing import Value
from multiprocessing.managers import BaseManager

try:
    import cPickle as pickle
except ImportError:
    import pickle


class QueueManager(BaseManager):
    pass


all_uid_list = []


def start_master():
    global all_uid_list
    uid_queue = Queue(200)
    uid_with_trash_queue = Queue(500)
    shutdown = Value('b', False)

    QueueManager.register('get_uid_queue', callable=lambda: uid_queue)
    QueueManager.register('get_uid_with_trash_queue', callable=lambda: uid_with_trash_queue)
    QueueManager.register('get_shutdown', callable=lambda: shutdown)

    manager = QueueManager(address=('', 5000), authkey=config.auth_key)
    manager.start()

    master = Process(target=master_process, args=(uid_queue, uid_with_trash_queue, all_uid_list, shutdown,))
    master.start()

    print '/////// 系统启动 - 主节点 ///////'

    with open('all_uid_list', 'rb') as f_all_uid:
        if f_all_uid.readline() != "":
            f_all_uid.seek(0)
            all_uid_list = pickle.load(f_all_uid)
    print '>>>>>>> 初始化 总解析uid列表 完毕'

    with open('uid_queue', 'rb') as f_uid_queue:
        if f_uid_queue.readline() != "":
            f_uid_queue.seek(0)
            uid_queue.get(timeout=15)
            uid_list = pickle.load(f_uid_queue)
            for uid in uid_list:
                try:
                    uid_queue.put(uid, timeout=60)
                except Full:
                    pass
    print '>>>>>>> 初始化 待解析uid列表 完毕'

    with open('uid_with_trash', 'rb') as f_uid_with_trash:
        if f_uid_with_trash.readline() != "":
            f_uid_with_trash.seek(0)
            uid_list = pickle.load(f_uid_with_trash)
            for uid in uid_list:
                try:
                    uid_with_trash_queue.put(uid, timeout=60)
                except Full:
                    pass
    print '>>>>>>> 初始化 待清洗uid列表 完毕'

    master.join()
    # 关闭服务
    manager.shutdown()
    after_shut_down(all_uid_list, uid_queue, uid_with_trash_queue)


def start_download():
    QueueManager.register('get_uid_queue')
    QueueManager.register('get_shutdown')

    manager = QueueManager(address=('127.0.0.1', 5000), authkey=config.auth_key)
    manager.start()

    uid_queue = manager.get_uid_queue()
    shutdown = manager.get_shutdown()

    process = []
    for i in range(3):
        process.append(Process(target=download_process, args=(uid_queue, shutdown,)))
    dispacher.start_process(process)
    daemon_proc = Process(target=daemon_process, args=(process, shutdown,))
    daemon_proc.start()
    daemon_proc.join()
    print '/////// 系统关闭 - 下载节点 ///////'


def start_url_resolver():
    print '/////// 系统启动 - 下载节点 ///////'

    QueueManager.register('get_uid_with_trash_queue')
    QueueManager.register('get_shutdown')

    manager = QueueManager(address=('127.0.0.1', 5000), authkey=config.auth_key)
    manager.start()

    uid_with_trash_queue = manager.get_uid_with_trash_queue()
    shutdown = manager.get_shutdown()

    process = []
    process.append(Process(target=followee_url_process, args=(uid_with_trash_queue, shutdown,)))
    process.append(Process(target=follower_url_process, args=(uid_with_trash_queue, shutdown,)))

    dispacher.start_process(process)
    daemon_proc = Process(target=daemon_process, args=(process, shutdown,))
    daemon_proc.start()
    daemon_proc.join()

    print '/////// 系统关闭 - 下载节点 ///////'


# spider begin
# command is
#         type(m master,d only download,u only url resolver)
#         port(integer)
if __name__ == '__main__':
    commands = sys.argv

    command_type = commands[1]
    port = commands[2]

    if command_type == 'm':
        start_master()

    elif command_type == 'd':
        start_master()

    elif command_type == 'u':
        start_master()

    else:
        print 'can\'t start without command type'

    try:
        port = int(port)
    except ValueError:
        print 'invalid port value'
