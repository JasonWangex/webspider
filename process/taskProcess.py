import time, sys, Queue
from multiprocessing.managers import BaseManager


class QueueManager(BaseManager):
    pass


QueueManager.register('get_task_queue')
QueueManager.register('get_result_queue')
QueueManager.register('get_value')

server_addr = '127.0.0.1'

print 'connect to server......'

m = QueueManager(address=(server_addr, 5000), authkey='123456aaa')

m.connect()
task = m.get_task_queue()
result = m.get_result_queue()
val = m.get_value()

for i in range(10):
    try:
        n = task.get(timeout=1)
        r = '%d ^ %d = %d' % (n, n, n * n)
        time.sleep(0.5)
        result.put(r)
        th = val
    except Queue.Empty:
        print 'task is empty', val

print 'exit!'


