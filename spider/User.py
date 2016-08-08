class User(object):
    id = None
    name = None
    uid = None
    hashId = None
    gender = None
    avatar = None
    introduction = None
    description = None
    career = None
    location = None
    education = None
    approval = None
    thanks = None
    collected = None
    share = None

    def __init__(self):
        pass

    def equal(self, other):
        return self.hashId == other.hashId
