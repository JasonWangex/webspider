# coding=utf8
import requests
import urllib2
import urllib
import time
import config
import User

firstUrl = "https://www.zhihu.com/people/boxun/about"

# header = '''Accept:*/*
# Accept-Encoding:gzip, deflate, br
# Accept-Language:zh-CN,zh;q=0.8,en;q=0.6
# Cache-Control:no-cache
# Connection:keep-alive
# Content-Length:132
# Content-Type:application/x-www-form-urlencoded; charset=UTF-8
# Cookie:d_c0="AICAnJ15QAqPTneEtEdhldjWjlZhnM4Kxik=|1468905539"; _za=0bc0cdaf-312b-43d3-a8fa-6004e939aa25; q_c1=7da8045e9cec4b56a12cba9a1a358003|1468987160000|1468987160000; _zap=1229d98e-1321-464d-b2fb-dc87188fd19c; login="OTc1MjBjMDExY2UyNDNmOTg2NDUzNDUzOTUxYWFlMGE=|1470215180|729511f331977a6336c0d8c9c44de275f950c595"; l_cap_id="YmQwNDBhYzc5ZGJkNDYwMWEwOWUyNDBlNjU1ZDgyZDE=|1470215180|a3e387f567253b3ff16877b6dbfe3a3efa8b79df"; cap_id="Njk2NGUxN2Q2NTU4NGNlMWIwYWY2OTVhYzY3MmVkNDE=|1470215180|51f4796d8a835d42d7d6188e3b1536a207149017"; z_c0=Mi4wQUpCQVZJT2FTZ29BZ0lDY25YbEFDaGNBQUFCaEFsVk5RVUhKVndCaXpkZG90U201M2V4aWFWd1puSlFXclFUTXpn|1470215233|036904ed8447626677db24b69935fc89c0a48cb0; a_t="2.0AJBAVIOaSgoXAAAAsJbKVwCQQFSDmkoKAICAnJ15QAoXAAAAYQJVTUFByVcAYs3XaLUpud3sYmlcGZyUFq0EzM6DO_X5dX5N_sLuaRo4YX8QfU3Hvw=="; _xsrf=b3a1598baa13098adbda17030bb030fc; s-q=d; s-i=6; sid=c4p1ckvo; s-t=autocomplete; __utmt=1; __utma=51854390.1903322304.1470368671.1470379237.1470383960.3; __utmb=51854390.8.10.1470383960; __utmc=51854390; __utmz=51854390.1470383960.3.3.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/ren-shu-zheng/about; __utmv=51854390.100--|2=registration_date=20160727=1^3=entry_date=20160720=1; d_c0="AICAnJ15QAqPTneEtEdhldjWjlZhnM4Kxik=|1468905539"; _za=0bc0cdaf-312b-43d3-a8fa-6004e939aa25; q_c1=7da8045e9cec4b56a12cba9a1a358003|1468987160000|1468987160000; _zap=1229d98e-1321-464d-b2fb-dc87188fd19c; login="OTc1MjBjMDExY2UyNDNmOTg2NDUzNDUzOTUxYWFlMGE=|1470215180|729511f331977a6336c0d8c9c44de275f950c595"; l_cap_id="YmQwNDBhYzc5ZGJkNDYwMWEwOWUyNDBlNjU1ZDgyZDE=|1470215180|a3e387f567253b3ff16877b6dbfe3a3efa8b79df"; cap_id="Njk2NGUxN2Q2NTU4NGNlMWIwYWY2OTVhYzY3MmVkNDE=|1470215180|51f4796d8a835d42d7d6188e3b1536a207149017"; z_c0=Mi4wQUpCQVZJT2FTZ29BZ0lDY25YbEFDaGNBQUFCaEFsVk5RVUhKVndCaXpkZG90U201M2V4aWFWd1puSlFXclFUTXpn|1470215233|036904ed8447626677db24b69935fc89c0a48cb0; _xsrf=b3a1598baa13098adbda17030bb030fc; s-q=d; s-i=6; sid=c4p1ckvo; s-t=autocomplete; __utma=51854390.1903322304.1470368671.1470379237.1470383960.3; __utmb=51854390.8.10.1470383960; __utmc=51854390; __utmz=51854390.1470383960.3.3.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/ren-shu-zheng/about; __utmv=51854390.100--|2=registration_date=20160727=1^3=entry_date=20160720=1; a_t="2.0AJBAVIOaSgoXAAAAXt_LVwCQQFSDmkoKAICAnJ15QAoXAAAAYQJVTUFByVcAYs3XaLUpud3sYmlcGZyUFq0EzM5ZB5YfuzMgqe7hrKHECGJACZW2Sw=="
# Host:www.zhihu.com
# Origin:https://www.zhihu.com
# Pragma:no-cache
# Referer:https://www.zhihu.com/people/ren-shu-zheng/followers
# User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36
# X-Requested-With:XMLHttpRequest
# X-Xsrftoken:b3a1598baa13098adbda17030bb030fc'''

header = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.zhihu.com",
    "Origin": "https://www.zhihu.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "X-Xsrftoken": "b3a1598baa13098adbda17030bb030fc",
}


def get_content2(url):
    request = urllib2.Request(url, None, header)
    request.add_header("Origin", "https://www.zhihu.com")
    request.add_header("Refer", url)
    request.add_header("User-Agent", "Mozilla")
    rtn = urllib2.urlopen(request)
    return rtn.read()


def get_content(url):
    data = {
        "method": "next",
        "params": '{"offset":90,"order_by":"created","hash_id":"7797883359c3a2b072b7195e8b317bf8"}'
    }
    r = requests.post("https://www.zhihu.com/node/ProfileFollowersListV2", data=data, headers=header,
                      cookies=config.cookies)
    return r.content


def get_followers(hash_id, page):
    r = open('temp', 'r')
    li = json.JSONDecoder().decode(r.read())

start = time.time()
print get_followers("3484f433b6b2ab66ad012910ae6ae48a", 1)
mid = time.time()

print mid - start
