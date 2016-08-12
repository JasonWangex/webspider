import cookielib

import requests

cookie = '''d_c0="AICAnJ15QAqPTneEtEdhldjWjlZhnM4Kxik=|1468905539"; _zap=1229d98e-1321-464d-b2fb-dc87188fd19c; q_c1=0bc4dbcebfbb411c84be380a5432c3f0|1470623621000|1470623621000; _ga=GA1.2.1903322304.1470368671; cap_id="OTJjOTg1NzI0OWY3NDZkOWE1Y2MzYzUyMzE0NWQ5ODA=|1470728445|37ee421f9aa35958be0b68faf0283f465089c2f3"; l_cap_id="NjE3OWRjNjU1ODYxNDU4YmI1ZTVkMDY0MmIyN2IxY2E=|1470728445|8b280bc84c07373c2012a2889060a343945ce54a"; login="ODRkMzkzNjVjMjk2NDk4NDhiMWU4ZTI2ZGRjYTA3NjI=|1470728457|3b452b3cc6706a730bc39528e15a5a55fffcd204"; _xsrf=dfc53894182c9598883cc5574e97738b; imhuman_cap_id="NmIwYjVkOGRiNTNkNDEwZWI1ZGM2MTZjNzM3YjFkZDA=|1470880912|9b20627737c1662c26f47361f20c33e4ee6e12a1"; __utmt=1; _za=d43324c4-013d-46bd-b9b9-316e16379c77; __utma=51854390.1903322304.1470368671.1470383960.1470880923.4; __utmb=51854390.12.8.1470880925173; __utmc=51854390; __utmz=51854390.1470880923.4.4.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/imhuman; __utmv=51854390.100--|2=registration_date=20150905=1^3=entry_date=20150905=1; a_t="2.0ABAM6wTEpggXAAAACGrTVwAQDOsExKYIAICAnJ15QAoXAAAAYQJVTQkW0VcAB5jx8vtrEWH9JwFNumNKRQwhfweqIHWYapZ5aIriqM0LmRIquU3Slg=="; z_c0=Mi4wQUJBTTZ3VEVwZ2dBZ0lDY25YbEFDaGNBQUFCaEFsVk5DUmJSVndBSG1QSHktMnNSWWYwbkFVMjZZMHBGRENGX0J3|1470881032|121f96fbde48302163b6dfbdc191d446fce504bf'''
header = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.zhihu.com",
    "Origin": "https://www.zhihu.com",
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "X-Xsrftoken": "dfc53894182c9598883cc5574e97738b",
}
first_uid = "boxun"
auth_key = "asdfasldfhaskn45576asd5fas6df43as6as7f6as4"


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
