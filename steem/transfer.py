# -*- coding:utf-8 -*-

import requests
import traceback

from steemengine.wallet import Wallet
from steem.account import SteemAccount
from utils.logging.logger import logger

URL = "https://api.steem-engine.com/accounts/history?account={account}&limit={limit}&offset={offset}&type=user&symbol={symbol}"

class SteemTransfer:

    def __init__(self, account):
        self.account = SteemAccount(account)
        self.transfers = None
        self.se_wallet = Wallet(self.account.author)

    def get_token_transfers(self, token, offset=0, limit=100):
        if self.transfers is None:
            url = URL.format(account=self.account.author, symbol=token, offset=offset, limit=limit)
            try:
                r = requests.get(url)
                if r.ok:
                    self.transfers = r.json()
                else:
                    logger.error("Failed when retrieving transfer info")
            except:
                logger.error("Failed when retrieving transfer info. Error: {}".format(traceback.format_exc()))
        return self.transfers

    def transfer(self, to, token, amount, memo="", retries=5):
        if retries <= 0:
            logger.info("Transfer failed after maximum retires")
            return

        if to and token and amount and memo is not None:
            token = token.upper()
            try:
                if token in ["STEEM", "SBD"]:
                    self.account.account.transfer(to, amount, token, memo)
                else:
                    self.se_wallet.transfer(to, amount, token, memo=memo)
                logger.info("Transferred {} {} to {} with memo [{}]".format(amount, token, to, memo))
            except:
                logger.error("Failed when tranferring {} {} to {} with memo [{}].\nError: {}".format(amount, token, to, memo, traceback.format_exc()))
                self.transfer(to, token, amount, memo, retries-1)
