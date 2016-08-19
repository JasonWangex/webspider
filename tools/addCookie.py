# coding=utf-8
from spider import cookies_dao
from spider.Domain import Cookies

while True:
    print "请输入Cookie:"
    cookie_ = raw_input(">")
    print "请输入Xsrf-Token:"
    xsrf = raw_input(">")
    cookie = Cookies()
    cookie.cookie = cookie_
    cookie.xsrf = xsrf
    cookies_dao.insert_cookie(cookie)
    print "是否继续？"
    if raw_input(">") == "exit":
        break
