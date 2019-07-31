# -*- coding:utf-8 -*-

from invoke import task

from steem.settings import settings
from utils.logging.logger import logger

from action.transfer.bot import TransferBot


@task(help={
      'url': 'the post url',
      'debug': 'enable the debug mode'
      })
def get_payout(ctx, url, debug=False):
    """ get the payout value of a post """

    settings.set_steem_node()

    bot = TransferBot()
    payout = bot.get_post_payout(url=url)
    for token in payout:
        print (token, ":")
        reward = payout[token]
        for k, v in reward.items():
            print (k, ":", v)

@task(help={
      'author': 'the actual author of this post',
      'url': 'the post url',
      'percentage': 'the percentage of author reward to sent',
      'memo': 'the memo to include in the transfer',
      'debug': 'enable the debug mode'
      })
def reward_author(ctx, author, url, percentage=50, memo="", debug=False):
    """ claim all the tokens of an account"""

    settings.set_steem_node()

    bot = TransferBot()
    bot.send_author_rewards(author, url, percentage, memo)

