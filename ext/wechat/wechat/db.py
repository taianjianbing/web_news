# from item import Item
from pymongo import MongoClient


class DB(object):
    def find(self, item):
        raise NotImplemented

    def update(self, item):
        raise NotImplemented


class PyDB(DB):
    def __init__(self):
        self.db = set()

    def find(self, item):
        if not isinstance(item, Item):
            raise Exception('item must be Item')
        for e in self.db:
            assert isinstance(e, item)
            if e.get('url') == item.get('url'):
                return True
        return False

    def update(self, item):
        if not isinstance(item, Item):
            raise Exception('item must be Item')
        self.db.add(item)


class MongoDb(DB):
    def __init__(self, mongo_db, mongo_username, mongo_password, mongo_ip, mongo_port, mongo_collection):
        self.mongo_db = mongo_db
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password
        self.mongo_ip = mongo_ip
        self.mongo_port = mongo_port
        self.mongo_collection = mongo_collection
        self.client = MongoClient(host=self.mongo_ip, port=self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.db.authenticate(mongo_username,mongo_password)
    def find(self, item):
        return self.db[self.mongo_collection].count({'md5': item['md5'], 'date': item['date']}) > 0

    def update(self, item):
        return \
        self.db[self.mongo_collection].update({'md5': item['md5'], 'date': item['date']}, {'$set': dict(item)}, True,
                                              True)['nModified'] > 0

