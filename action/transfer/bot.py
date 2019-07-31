# -*- coding:utf-8 -*-

from steem.settings import settings
from steem.transfer import SteemTransfer
from steem.comment import SteemComment
from utils.logging.logger import logger


class TransferBot:

    def __init__(self):
        self.sender = settings.get_env_var("TRANSFER_SENDER")
        self.wallet = SteemTransfer(account=self.sender)

    def send_author_rewards(self, receiver, url, percentage=50, memo=""):
        c = SteemComment(url=url)
        payout = self.get_post_payout(post=c.get_comment())

        for token in payout:
            reward = payout[token]
            paid_author_reward = float(reward['author']) * percentage / 100
            self.transfer(receiver, token, paid_author_reward, memo)

    def get_post_payout(self, post=None, url=None):
        c = SteemComment(comment=post, url=url)
        # steem payout
        steem_payout = c.get_steem_payout()
        payout = steem_payout or {}
        # scot payout
        tokens = c.get_relevant_tokens()
        for t in tokens:
            payout[t] = c.get_scot_payout(t)

        return payout

    def transfer(self, to, token, amount, memo):
        self.wallet.transfer(to, token, amount, memo)
