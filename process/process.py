from multiprocessing import Process, Value
import random, time, Queue
from multiprocessing.managers import BaseManager

task_queue = Queue.Queue()
result_queue = Queue.Queue()
a_value = Value('b', False)


class QueueManager(BaseManager):
    pass


QueueManager.register('get_task_queue', callable=lambda: task_queue)
QueueManager.register('get_result_queue', callable=lambda: result_queue)
QueueManager.register('get_value', callable=lambda: a_value)

manager = QueueManager(address=('', 5000), authkey="123456aaa")

manager.start()

task = manager.get_task_queue()
result = manager.get_result_queue()

for i in range(10):
    n = random.randint(0, 100000)
    print "put task %d" % n
    task.put(n)

for j in range(10):
    r = result.get(timeout=300)
    print 'result: %r' % r

manager.shutdown()
