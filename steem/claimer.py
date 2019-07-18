# -*- coding:utf-8 -*-

import json
import traceback
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
            body = []
            for token in tokens:
                amount = self.get_scot_token_pending_amount(token)
                if amount and amount > 0:
                    body.append({"symbol": token})
                    amount = float(amount) / 1000
                    logger.info("@{} will claim {} {} token".format(self.author, amount, token))
            try:
                self.steem.custom_json("scot_claim_token", json.dumps(body), required_posting_auths=[self.author])
                logger.info("@{} has claimed all tokens successfully".format(self.author))
            except:
                logger.error("Failed when @{} was claiming all token.\nError: {}".format(self.author, traceback.format_exc()))
        else:
            logger.info("@{} has no tokens to claim.".format(self.author))

    def claim_scot_token(self, token=None):
        amount = self.get_scot_token_pending_amount(token)
        if amount and amount > 0:
            body = {"symbol": token}
            amount = float(amount) / 1000
            try:
                self.steem.custom_json("scot_claim_token", json.dumps(body), required_posting_auths=[self.author])
                logger.info("@{} has claimed {} {} token successfully".format(self.author, amount, token))
            except:
                logger.error("Failed when @{} was claiming {} {} token.\nError: {}".format(self.author, amount, token, traceback.format_exc()))
        else:
            logger.info("@{} has no {} token to claim.".format(self.author, token))
