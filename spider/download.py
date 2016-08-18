# coding=utf8
import requests
import time
from mysql.connector import Error
from requests.exceptions import RequestException
import config
import json
import cookies_dao


class CookieValue(object):
    pass

cookieWrapper = CookieValue()


def start_download():
    global cookieWrapper
    cookieWrapper.value = cookies_dao.get_one()
    cookies_dao.lock_cookie(cookieWrapper.value)


def get_content(url):
    global cookieWrapper
    try:
        header = config.header
        header['Cookie'] = cookieWrapper.value.cookie
        header['X-Xsrftoken'] = cookieWrapper.value.xsrf
        resp = requests.get(url, headers=header, verify=False)
    except RequestException:
        print "/////////RequestException!/////////"
        return u""
    return resp.content


def get_followers(hash_id, page, url='ProfileFollowersListV2'):
    global cookieWrapper
    params = {
        'offset': page * 20,
        'hash_id': hash_id,
        'order_by': 'created'
    }

    data = {
        "method": "next",
        "params": json.dumps(params)
    }
    try:
        header = config.header
        header['Cookie'] = cookieWrapper.value.cookie
        header['X-Xsrftoken'] = cookieWrapper.value.xsrf
        resp = requests.post("https://www.zhihu.com/node/" + url, data=data, headers=header, verify=False)
        return resp.content
    except RequestException:
        print "/////////RequestException!/////////"
        return u""


def get_followees(hash_id, page):
    return get_followers(hash_id=hash_id, page=page, url='ProfileFolloweesListV2')


def shut_down():
    global cookieWrapper
    cookies_dao.release_lock(cookieWrapper.value)


def restart():
    global cookieWrapper
    failed = 0
    while failed < 3:
        try:
            cookieWrapper.value = cookies_dao.get_one()
            cookies_dao.lock_cookie(cookieWrapper.value)
            if cookieWrapper.value is not None:
                return True
            else:
                return False
        except Error:
            failed += 1
            time.sleep(5)
            continue
    else:
        return False

