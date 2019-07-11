# -*- coding:utf-8 -*-

import json
from steem.scot import author as scot_author
from steem.settings import settings
from utils.logging.logger import logger

class Claimer:

    def __init__(self, author):
        self.steem = settings.get_steem_node()
        self.author = author
        self.scot_author_json = None

    def _get_scot_json(self):
        if self.scot_author_json is None:
            self.scot_author_json = scot_author(self.author)
        return self.scot_author_json

    def get_pending_scot_tokens(self):
        data = self._get_scot_json()
        tokens = []
        for token in data:
            amount = self.get_scot_token_pending_amount(token)
            if amount > 0:
                tokens.append(token)
        return tokens

    def get_scot_token_pending_amount(self, token):
        data = self._get_scot_json()
        if token in data and "pending_token" in data[token]:
            return data[token]["pending_token"]
        else:
            return 0

    def claim_all_scot_tokens(self):
        tokens = self.get_pending_scot_tokens()
        if tokens and len(tokens) > 0:
            for token in tokens:
                self.claim_scot_token(token)
        else:
            logger.info("@{} has no tokens to claim.".format(self.author))

    def claim_scot_token(self, token=None):
        amount = self.get_scot_token_pending_amount(token)
        if amount and amount > 0:
            body = {"symbol": token}
            self.steem.custom_json("scot_claim_token", json.dumps(body), required_posting_auths=[self.author])
            amount = float(amount) / 1000
            logger.info("@{} has claimed {} {} token successfully".format(self.author, amount, token))
        else:
            logger.info("@{} has no {} token to claim.".format(self.author, token))
