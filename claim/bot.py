# -*- coding:utf-8 -*-

from steem.settings import settings
from steem.claimer import Claimer

PILOT_ACCOUNT_KEY = "PILOT_ACCOUNT"
DEFAULT_PILOT_ACCOUNT = "self-driving"

class ClaimBot:

    def __init__(self):
        self.claimer_account = settings.get_env_var(PILOT_ACCOUNT_KEY) or DEFAULT_PILOT_ACCOUNT

    def get_authors(self):
        pass

    def claim_scot_token(self, author, token):
        claimer = Claimer(author)
        claimer.claim_scot_token(token)

    def claim_all_scot_tokens(self, author):
        claimer = Claimer(author)
        claimer.claim_all_scot_tokens()
