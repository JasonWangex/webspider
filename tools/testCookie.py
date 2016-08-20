# coding=utf-8
from spider import download

download.start_download()
while True:
    if raw_input("> ") == "no":
        break
    else:
        content = download.get_content("http://www.zhihu.com/people/boxun")
        f = open("testCookie.html", "w")
        f.write(content)
        f.close()
        print '是否失效? yes/no '
        if raw_input("> ") == "yes":
            download.lockCookie()
    print '是否继续? yes/no '
    download.getNextCookie()
