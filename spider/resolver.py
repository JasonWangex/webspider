# coding=utf8
from bs4 import BeautifulSoup
from Domain import User
import json


def get_or_null(f, *args):
    try:
        return f(args) or u""
    except AttributeError:
        return u""


def get_all_text(collections):
    rtn = u""
    for i in collections[1:]:
        if i.get("class") is None or u"zg-gray" in (i.get("class") or []):
            rtn = rtn + i.get_text().replace("\n", "").replace(".", "") + u", "
    return rtn[:len(rtn) - 2]


def resolve_for_user(response):
    soup = BeautifulSoup(response, "html.parser")
    soup.prettify("utf-8")
    follow = soup.find("div", class_='zm-profile-side-following zg-clear').find_all('strong')
    followees = follow[0].get_text()
    followers = follow[1].get_text()

    head_body = soup.find("div", class_="body clearfix")

    name = head_body.find("a", class_="name").get_text()
    uid = head_body.find("a", class_="name").get('href').replace('/people/', '')
    try:
        avatar = head_body.find("img", class_="Avatar--l").get('src')
    except AttributeError:
        avatar = u""

    try:
        introduction = head_body.find("div", "bio ellipsis").get('title')
    except AttributeError:
        introduction = u""

    try:
        description = head_body.find("span", "unfold-item").find('span', class_='content').get_text()
    except AttributeError:
        description = u""

    details = soup.find("div", class_="zm-profile-section-list zm-profile-details").find_all("div",
                                                                                             class_="zm-profile-module")
    temp = details[0]("strong")
    approval = temp[0].get_text()
    thanks = temp[1].get_text()
    collected = temp[2].get_text()
    share = temp[3].get_text()

    career = get_all_text(details[1](["span", "a"]))
    location = get_all_text(details[2](["span", "a"]))
    education = get_all_text(details[3](["span", "a"]))
    hash_id = soup.find("button", "zg-btn zg-btn-follow zm-rich-follow-btn").get("data-id")

    try:
        gender = 1 if u"icon-profile-male" in head_body.find("span", class_="item gender").find("i").get(
            'class') else 2
    except AttributeError:
        gender = 0

    user = User()
    # dic = {
    #     "name": name,
    #     "avatar": avatar,
    #     "gender": gender,
    #     "introduction": introduction,
    #     "description": description,
    #     "location": location,
    #     "education": education,
    #     "approval": approval,
    #     "thanks": thanks,
    #     "collected": collected,
    #     "share": share,
    #     "career": career,
    #     "hashId": hash_id
    # }
    user.name = name
    user.uid = uid
    user.avatar = avatar
    user.gender = int(gender)
    user.introduction = introduction
    user.description = description
    user.location = location
    user.education = education
    user.approval = int(approval)
    user.thanks = int(thanks)
    user.collected = int(collected)
    user.share = int(share)
    user.career = career
    user.hashId = hash_id
    user.followees = int(followees)
    user.followers = int(followers)
    return user


def resolve_for_uids(response):
    urls = []
    try:
        response = json.JSONDecoder().decode(response)
        msg = response['msg']
        for item in msg:
            url = resolve_for_uid(item)
            if url is not None:
                urls.append(url)
    except ValueError:
        pass
    return urls


def resolve_for_uid(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        uid = soup.find('a', class_='zm-item-link-avatar').get('href').replace('/people/', '')
    except AttributeError:
        uid = None
    return uid


def get_url_by_uid(uid):
    return "https://www.zhihu.com/people/" + uid + "/about"
