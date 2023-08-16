from pymongo import MongoClient, CursorType


class MongoDB:
    def __init__(self, host='localhost', port=27017, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        # MongoDB 연결
        if self.user is None or self.password is None:
            self.client = MongoClient(host=self.host, port=self.port)
        else:
            self.client = MongoClient(host=self.host, port=self.port, username=self.user, password=self.password)

    def insert_one(self, data=None, db_name=None, collection_name=None):
        if db_name is None:
            raise AttributeError("db_name is not allowed None")
        if collection_name is None:
            raise AttributeError("collection_name is not allowed None")

        collection = self.client[db_name][collection_name]
        result = collection.insert_one(data).inserted_id

        return result

    def insert_many(self, datas=None, db_name=None, collection_name=None):
        if db_name is None:
            raise AttributeError("db_name is not allowed None")
        if collection_name is None:
            raise AttributeError("collection_name is not allowed None")

        collection = self.client[db_name][collection_name]
        result = collection.insert_many(datas).inserted_ids

        return result

    def find_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find_one(condition, {"_id": False})
        return result

    def find_item(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True,
                                                            cursor_type=CursorType.EXHAUST)
        return result

    def close(self):
        if self.client is not None:
            self.client.close()

    def __del__(self):
        if self.client is not None:
            self.close()
