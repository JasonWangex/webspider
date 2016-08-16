# coding=utf8
import requests
import urllib2
import time
import config
import json


def get_content2(url):
    request = urllib2.Request(url, None, config.header)
    request.add_header("Origin", "https://www.zhihu.com")
    request.add_header("Refer", url)
    request.add_header("User-Agent", "Mozilla")
    rtn = urllib2.urlopen(request)
    return rtn.read()


def get_content(url):
    time.sleep(0.2)
    resp = requests.get(url, headers=config.header)
    return resp.content


def get_followers(hash_id, page, url='ProfileFollowersListV2'):
    params = {
        'offset': page * 20,
        'hash_id': hash_id,
        'order_by': 'created'
    }

    data = {
        "method": "next",
        "params": json.dumps(params)
    }
    resp = requests.post("https://www.zhihu.com/node/" + url, data=data, headers=config.header)
    return resp.content


def get_followees(hash_id, page):
    return get_followers(hash_id=hash_id, page=page, url='ProfileFolloweesListV2')

