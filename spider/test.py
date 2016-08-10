import threading
import time
from sqlalchemy.orm import session

from spider import config
from spider import download
from spider import resolver
from persistence import user_dao

lock = threading.Lock()
c = 0


def count_star():
    global c
    with lock :
        c += 1
        print c


for i in range(1, 10):
    threading.Thread(target=count_star).start()
