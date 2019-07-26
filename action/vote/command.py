# -*- coding:utf-8 -*-

from invoke import task

from steem.settings import settings
from utils.logging.logger import logger

from action.vote.bot import VoteBot


@task(help={
      'url': 'the url of the comment to vote',
      'debug': 'enable the debug mode'
      })
def comment(ctx, url=None, debug=False):
    """ vote a specific comment"""

    # if debug:
        # settings.set_debug_mode()

    settings.set_steem_node()

    bot = VoteBot()
    bot.vote(url=url)

