# coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from sqlalchemy import func

from spider import config
import time

from spider.Domain import Cookies

mail_host = 'smtp.exmail.qq.com'
mail_user = "wangjz@dxy.cn"
mail_pass = ""

sender = 'wangjz@dxy.cn'
receivers = ['wangjz@dxy.cn']

last_cookie_count = 0
while True:
    session = config.DBSession()
    cookie_count = session.query(func.count('*')).filter(Cookies.available == True).scalar()
    session.close()
    if cookie_count == last_cookie_count:
        time.sleep(10)
        continue
    else:
        last_cookie_count = cookie_count

    try:
        message = MIMEText('可用cookie更改，当前可用：' + str(cookie_count), 'plain', 'utf-8')
        message['From'] = Header('Monitor', 'utf-8')
        message['To'] = Header('Monitor', 'utf-8')
        subject = '[监控] - 爬虫cookie监控'
        message['Subject'] = Header(subject, 'utf-8')
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 发送邮件失败"

