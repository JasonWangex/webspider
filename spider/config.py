import cookielib

import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

cookie = '''l_n_c=1; q_c1=8c449cf0c5804eeda361f2bf2a3c4183|1471329318000|1471329318000; _xsrf=386885c8a22ceaf13cba4b26e3d9d7ab; d_c0="AJBA75iXZAqPTmNvWCrOcoKXhBI-4OE46RM=|1471329318"; _zap=f731ec93-df61-4f11-b01e-9c14b10b75a0; _za=5b9b539e-57cf-4d8b-89e8-9c2d1f862617; l_cap_id="NDMwMjIyNThlYWEwNGFmMzgzZWMxMTMxODJiZTViYjA=|1471330005|668b92ac15463965017b2ce0b2b4f344575ec066"; cap_id="NjcyM2MxMmU1Nzg1NGU3MGE0MTM5NmUxMjJjMjY5NTk=|1471330005|8a07947e8de5c329fa377010d9cbb4b1f67feff2"; auth_type=cXFjb25u|1471330069|f4d9866c492e63ef822da82acec13878e6dfe23a; token="REY3QkRBNDk4QjY4MTdDMDdCQjhGMDRFRTJGMjE1MEI=|1471330069|e71148df1397dc27806ab194009a9b54b61085ef"; client_id="MEI4N0FDN0NFRkFENTgxMTQwNzQ4RkYzQTlENEUzNDA=|1471330069|7e4f519cf138bcb862857c778638d722f908debb"; __utmt=1; a_t="2.0AFCAlYSaZAoXAAAAX0TaVwBQgJWEmmQKAJBA75iXZAoXAAAAYQJVTV1E2lcAOCVshfD48sD40NBVwoVCAWCkmJFQD1weuYUoy4SpzbNOW0Gxt3Lt-g=="; z_c0=Mi4wQUZDQWxZU2FaQW9Ba0VEdm1KZGtDaGNBQUFCaEFsVk5YVVRhVndBNEpXeUY4UGp5d1BqUTBGWENoVUlCWUtTWWtR|1471330143|6eb840c7b80e28d5087af9b2ace9d1e65ab51f91; __utma=51854390.2026910372.1471329320.1471329320.1471329320.1; __utmb=51854390.8.10.1471329320; __utmc=51854390; __utmz=51854390.1471329320.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100--|2=registration_date=20160816=1^3=entry_date=20160816=1'''

header = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.zhihu.com",
    "Origin": "https://www.zhihu.com",
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "X-Xsrftoken": "386885c8a22ceaf13cba4b26e3d9d7ab",
}
first_uid = "boxun"
auth_key = "asdfasldfhaskn45576asd5fas6df43as6as7f6as4"

engine = create_engine(
    'mysql+mysqlconnector://cdb_outerroot:cdb_outerroot@57b17a81a1ef5.sh.cdb.myqcloud.com:6065/zhihu_users?charset=utf8mb4'
)
DBSession = sessionmaker(bind=engine)
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
