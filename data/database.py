# -*- coding:utf-8 -*-

import os
import pymongo

from utils.system.date import days_ago
from utils.network.internet import get_ip


PRODUCTION_DATABASE = "production"
TESTING_DATABASE = "test"

REPLIES_COLLECTION = "replies"


class SteemDatabase:

    def __init__(self, database):
        db_svr = os.environ['DB_SVR']
        db_usr = os.environ['DB_USR']
        db_pwd = os.environ['DB_SEC']
        self.database = database
        self.db = self._connect(db_svr, database, db_usr, db_pwd)

        self.comments = None
        self.reviews = None
        self.accounts = {}
        self.rewards = None
        self.replies = None

    def _connect(self, server, database, user, pwd):
        client = pymongo.MongoClient("mongodb+srv://{}:{}@{}/{}?retryWrites=true".format(user, pwd, server, database), ssl=True)
        print("connected to database [{}] from machine [{}]".format(database[:2], get_ip()))
        return client[database]

    def _accounts(self, collection_name):
        if not collection_name in self.accounts:
            self.accounts[collection_name] = self.db[collection_name]
        return self.accounts[collection_name]

    def insert_account(self, collection_name, account):
        self._accounts(collection_name).insert_one(account)

    def update_account(self, collection_name, name, account):
        self._accounts(collection_name).replace_one({"name": name}, account, True)

    def has_account(self, collection_name, name):
        return self._accounts(collection_name).find_one({"name": name}) is not None

    def has_account_authorship(self, collection_name, name, source):
        return self._accounts(collection_name).find_one({"name": name, "source": source}) is not None

    def get_account(self, collection_name, name):
        return self._accounts(collection_name).find_one({"name": name})

    def get_accounts(self, collection_name, name):
        return self._accounts(collection_name).find({"name": name})

    def _replies(self):
        if self.replies is None:
            self.replies = self.db[REPLIES_COLLECTION]
        return self.replies

    def insert_reply(self, reply):
        self._replies().insert_one(reply)

    def has_reply(self, receiver, message_id):
        return self._replies().find_one({"receiver": receiver, "message_id": message_id}) is not None

    def get_replies(self, message_id, days=None):
        if days is not None:
            return self._replies().find({"message_id": message_id, "updated": {"$gte": days_ago(days)}})
        else:
            return self._replies().find({"message_id": message_id})
