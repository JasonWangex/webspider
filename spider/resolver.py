# coding=utf8
from bs4 import BeautifulSoup
import User
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
    head_body = soup.find("div", class_="body clearfix")

    name = head_body.find("a", class_="name").get_text()
    avatar = get_or_null(head_body.find("img", class_="Avatar--l").get, 'src')
    introduction = get_or_null(head_body.find("div", "bio ellipsis").get, 'title')
    description = get_or_null(head_body.find("span", "fold-item").get_text)

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
    hash_id = soup.find("button", "zg-btn zg-btn-follow zm-rich-follow-btn")("data-id")

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
    user.avatar = avatar
    user.gender = gender
    user.introduction = introduction
    user.description = description
    user.location = location
    user.education = education
    user.approval = approval
    user.thanks = thanks
    user.collected = collected
    user.share = share
    user.career = career
    user.hashId = hash_id

    return user


def resolve_for_urls(response):
    response = json.JSONDecoder().decode(response)
    msg = response['msg']
    urls = []
    for item in msg:
        urls.append(resolve_for_uid(item))
    return urls


def resolve_for_uid(html):
    soup = BeautifulSoup(html, "html.parser")
    uid = soup.find('a', class_='zm-item-link-avatar').get('href').replace('/people/', '')
    return uid


def get_url_by_uid(uid):
    return "https://www.zhihu.com/people/" + uid
