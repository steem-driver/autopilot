# -*- coding:utf-8 -*-

from steem.settings import settings
from steem.claimer import Claimer
from steem.account import SteemAccount
from utils.logging.logger import logger

PILOT_ACCOUNT_KEY = "PILOT_ACCOUNT"
DEFAULT_PILOT_ACCOUNT = "self-driving"
MINIMUM_SP_DELEGATION = 3500000000 # a bit less than 2 SP


class ClaimBot:

    def __init__(self):
        self.claimer_author = settings.get_env_var(PILOT_ACCOUNT_KEY) or DEFAULT_PILOT_ACCOUNT
        self.claimer_account = SteemAccount(author=self.claimer_author)

    def get_users(self):
        users = []
        delegations = self.claimer_account.incoming_delegations()
        for delegation in delegations:
            vesting_shares = float(delegation["vesting_shares"]["amount"])
            if vesting_shares > MINIMUM_SP_DELEGATION:
                users.append(delegation["delegator"])
        return users

    def claim_all_accounts(self):
        users = self.get_users()
        logger.info("The current users are : {}".format(users))
        for user in users:
            logger.info("Claim rewards for @{}".format(user))
            self.claim_all_scot_tokens(user)

    def claim_scot_token(self, author, token):
        claimer = Claimer(author)
        claimer.claim_scot_token(token)

    def claim_all_scot_tokens(self, author):
        claimer = Claimer(author)
        claimer.claim_all_scot_tokens()
