# -*- coding:utf-8 -*-

from steem.settings import settings
from steem.transfer import SteemTransfer
from steem.comment import SteemComment
from utils.logging.logger import logger


class TransferBot:

    def __init__(self):
        self.sender = settings.get_env_var("TRANSFER_SENDER")
        self.wallet = SteemTransfer(account=self.sender)

    def get_post_payout(self, post=None, url=None):
        c = SteemComment(comment=post, url=url)
        return c.get_payout()

    def transfer(self, to, token, amount, memo):
        self.wallet.transfer(to, token, amount, memo)

    def send_author_rewards(self, receiver, url, percentage=50, memo=""):
        logger.info("Sending author reward to {} for post {} with percentage {}".format(receiver, url, percentage))
        payout = self.get_post_payout(url=url)
        for token, reward in payout.items():
            # send author reward to receivers
            paid_author_reward = float(reward['author']) * percentage / 100
            self.transfer(receiver, token, paid_author_reward, memo)
