# -*- coding:utf-8 -*-

from invoke import task

from steem.settings import settings
from utils.logging.logger import logger

from action.info.bot import InfoBot


@task(help={
      'author': 'the author who has voted',
      'debug': 'enable the debug mode'
      })
def votes(ctx, author=None, debug=False):
    """ vote a specific comment"""

    # if debug:
        # settings.set_debug_mode()

    settings.set_steem_node()

    bot = InfoBot("null")
    print(bot.get_votes([author]))
