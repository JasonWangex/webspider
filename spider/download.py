# coding=utf8
import requests
from requests.exceptions import SSLError
import config
import json
from Domain import Cookies
from persistence import cookies_dao


class Download(object):
    cookie = Cookies()

    def __init__(self):
        self.cookie = cookies_dao.get_one_with_lock()
        pass

    def get_content(self, url):
        try:
            header = config.header
            header['Cookie'] = self.cookie.cookie
            header['X-Xsrftoken'] = self.cookie.xsrf
            resp = requests.get(url, headers=config.header, verify=False)
        except SSLError:
            return u""
        return resp.content

    def get_followers(self, hash_id, page, url='ProfileFollowersListV2'):
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
            header['Cookie'] = self.cookie.cookie
            header['X-Xsrftoken'] = self.cookie.xsrf
            resp = requests.post("https://www.zhihu.com/node/" + url, data=data, headers=header, verify=False)
            return resp.content
        except SSLError:
            return u""

    def get_followees(self, hash_id, page):
        return self.get_followers(hash_id=hash_id, page=page, url='ProfileFolloweesListV2')

    def shut_down(self):
        cookies_dao.release_lock(self.cookie)

    def restart(self):
        self.cookie = cookies_dao.get_one_with_lock()
        if self.cookie is not None:
            return True
        else:
            return False

