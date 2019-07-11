# -*- coding:utf-8 -*-

import os

from steem.comment import SteemComment
from steem.account import SteemAccount
from steem.settings import settings
from utils.logging.logger import logger
from utils.system.date import in_recent_days


class AuthorsCollection:

    list_name = "base"

    def __init__(self):
        self.db = settings.get_db()

    def _contains(self, author):
        return self.db.has_account(self.list_name, author)

    def _is_recent(self, account, days):
        return in_recent_days(account.birthday(), days)

    def verify(self, author):
        if self._contains(author):
            return True
        else:
            return False

    def _add(self, account):
        if self._contains(account.name()):
            return False

        account_data = {
            'name': account.name(),
            'reputation': account.reputation(),
            'steem_power': account.steem_power(),
            'follower_count': account.follower_count(),
            'post_count': account.post_count(),
            'created': account.birthday()
        }
        self.db.insert_account(self.list_name, account_data)
        logger.info(u'{} has been added to {}'.format(account.name(), self.list_name))
        return True

