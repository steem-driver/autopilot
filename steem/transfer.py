# -*- coding:utf-8 -*-

import requests
from utils.logging.logger import logger

URL = "https://api.steem-engine.com/accounts/history?account={account}&limit={limit}&offset={offset}&type=user&symbol={symbol}"

class SteemTransfer:

    def __init__(self, account):
        self.account = account
        self.transfers = None

    def get_token_transfers(self, token, offset=0, limit=100):
        if self.transfers is None:
            url = URL.format(account=self.account, symbol=token, offset=offset, limit=limit)
            r = requests.get(url)
            if r.ok:
                self.transfers = r.json()
            else:
                logger.error("Failed when retrieving transfer info")
        return self.transfers
