from spider import config
from spider import download
from spider import resolver
from persistence import user_dao
# content = download.get_content(url=resolver.get_url_by_uid(config.first_uid))
f = open('temp', 'r')
# f.write(content)
user_dao.start_session()

user = resolver.resolve_for_user(f.read())
user_dao.save_or_update(user)

