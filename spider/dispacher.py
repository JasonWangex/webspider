# coding=utf-8
import time
from Queue import Full, Empty

from multiprocessing.managers import BaseManager

from mysql.connector import Error

import config
import resolver
import download
import user_dao
import failed_dao
import threading
from Domain import Failed
from multiprocessing import Process


try:
    import cPickle as pickle
except ImportError:
    import pickle

failedCount = 0


def download_process(uid_queue, operator, localShutdown):
    global failedCount
    while not localShutdown.value:
        if failedCount > 5:
            print '/////////下载被封禁！/////////'
            time.sleep(1)
            print '>>>>>> 正在尝试重启....'

            while failedCount > 5:
                if operator:
                    print '>>>>>> 正在尝试重启...'
                    if not download.restart():
                        print '/////////重启失败！/////////'
                        localShutdown.value = True
                        break
                    else:
                        print '>>>>>> 重启成功....'
                        time.sleep(5)
                        failedCount = 0
                else:
                    print '>>>>>> 正在等待主线程重启...'
                    time.sleep(1)
                    continue
        try:
            uid = uid_queue.get(timeout=5)
        except Empty:
            continue
        url = resolver.get_url_by_uid(uid)
        content = download.get_content(url)
        threading.Thread(target=resolve_thread, args=(content,)).start()


def resolve_thread(content):
    global failedCount
    try:
        user = resolver.resolve_for_user(content)
        print '解析>>>>>>', user.uid
        user_dao.save_or_update(user)
        failedCount = 0
    except AttributeError:
        print '///////////解析失败////////////'
        failed = Failed()
        failed.content = content
        failed_dao.save(failed)
        failedCount += 1


def followee_url_process(uid_with_trash_queue, user_waiting_resolve_url_queue, operator, localShutdown):
    global failedCount
    while not localShutdown.value:
        user_id = user_waiting_resolve_url_queue.get()
        try:
            current_user = user_dao.get_user_for_followees(user_id=user_id)
        except Error:
            print "mysql connector error !!!"
            time.sleep(5)
            continue

        if current_user is None:
            continue

        max_followee_page = 0 if current_user.followees == 0 else current_user.followees / 20 + 1
        while current_user.getFollowees < max_followee_page and not localShutdown.value:
            if failedCount > 5:
                print '///////URL 疑似被封禁///////'
                print failedCount
                time.sleep(0.5)
                while failedCount > 10:
                    print '///////URL 被封禁///////'
                    if operator:
                        print '>>>>>> 正在尝试重启...'
                        if not download.restart():
                            print '/////////重启失败！/////////'
                            localShutdown.value = True
                            return
                        else:
                            failedCount = 0
                            time.sleep(10)
                    else:
                        print '>>>>>> 正在等待主线程重启...'
                        time.sleep(1)
                        continue

            msg = download.get_followees(hash_id=current_user.hashId, page=current_user.getFollowees)
            current_user.getFollowees += 1
            print ">>>>> URL下载成功 - Followee ", current_user.getFollowees
            uids = resolver.resolve_for_uids(msg)
            user_dao.save_or_update(current_user)
            if len(uids) == 0:
                failedCount += 1
                continue
            else:
                failedCount = 0
            try:
                uid_with_trash_queue.put(uids, timeout=10)
            except Full:
                if localShutdown.value:
                    user_dao.save_or_update(current_user)
                    return
                else:
                    print ">>>>> one uid lis is lost!", time.time()
                    continue
        current_user.needGetFollowees = False
        current_user.getFollowees = max_followee_page
        user_dao.save_or_update(current_user)


def local_shutdown_listener(localShutdown):
    while not localShutdown.value and raw_input() != 'exit':
        continue
    localShutdown.value = True


def start_process(procs):
    for proc in procs:
        proc.start()


class QueueManager(BaseManager):
    pass


def start_download(address, port, localShutdown):
    print '/////// 系统启动 - 下载节点 ///////'
    QueueManager.register('get_uid_queue')

    manager = QueueManager(address=(address, port), authkey=config.auth_key)
    manager.connect()

    uid_queue = manager.get_uid_queue()

    process = []
    download.start_download()
    process.append(Process(target=download_process, args=(uid_queue, True, localShutdown,)))
    start_process(process)
    local_shutdown_listener(localShutdown)
    download.shut_down()


class UserQueueManager(BaseManager):
    pass


def start_url_resolver(address, port, localShutdown):
    print '/////// 系统启动 - RUL节点 ///////'

    QueueManager.register('get_uid_with_trash_queue')

    manager = QueueManager(address=(address, port), authkey=config.auth_key)
    manager.connect()

    UserQueueManager.register('get_user_waiting_resolve_url_queue')
    user_manager = UserQueueManager(address=('139.196.32.66', 9901), authkey=config.auth_key)
    user_manager.connect()

    download.start_download()

    uid_with_trash_queue = manager.get_uid_with_trash_queue()
    user_waiting_resolve_url_queue = user_manager.get_user_waiting_resolve_url_queue()

    process = [
        Process(target=followee_url_process,
                args=(uid_with_trash_queue, user_waiting_resolve_url_queue, True, localShutdown,))]
    start_process(process)
    local_shutdown_listener(localShutdown)
    download.shut_down()
