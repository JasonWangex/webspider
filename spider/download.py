# coding=utf8
import requests
from requests.exceptions import RequestException
import config
import json
import cookies_dao

cookie = None


def start_download():
    global cookie
    cookie = cookies_dao.get_one_with_lock()
    cookies_dao.lock_cookie(cookie)


def get_content(url):
    global cookie
    try:
        header = config.header
        header['Cookie'] = cookie.cookie
        header['X-Xsrftoken'] = cookie.xsrf
        resp = requests.get(url, headers=header, verify=False)
    except RequestException:
        print "/////////RequestException!/////////"
        return u""
    return resp.content


def get_followers(hash_id, page, url='ProfileFollowersListV2'):
    global cookie
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
        header['Cookie'] = cookie.cookie
        header['X-Xsrftoken'] = cookie.xsrf
        resp = requests.post("https://www.zhihu.com/node/" + url, data=data, headers=header, verify=False)
        return resp.content
    except RequestException:
        print "/////////RequestException!/////////"
        return u""


def get_followees(hash_id, page):
    return get_followers(hash_id=hash_id, page=page, url='ProfileFolloweesListV2')


def shut_down():
    global cookie
    cookies_dao.release_lock(cookie)


def restart():
    global cookie
    cookie = cookies_dao.get_one_with_lock()
    cookies_dao.lock_cookie(cookie)
    if cookie is not None:
        return True
    else:
        return False
