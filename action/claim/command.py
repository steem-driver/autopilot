# -*- coding:utf-8 -*-

from invoke import task

from steem.settings import settings
from utils.logging.logger import logger

from action.claim.bot import ClaimBot


@task(help={
      'account': 'the account to claim the rewards',
      'token': 'the token symbol to do the claim',
      'debug': 'enable the debug mode'
      })
def token(ctx, account, token=None, debug=False):
    """ claim a specific token"""

    # if debug:
        # settings.set_debug_mode()

    settings.set_steem_node()

    bot = ClaimBot()
    if not token:
        bot.claim_all_scot_tokens(account)
    else:
        bot.claim_scot_token(account, token)


@task(help={
      'account': 'the account to claim the rewards',
      'debug': 'enable the debug mode'
      })
def all_tokens(ctx, account, debug=False):
    """ claim all the tokens of an account"""

    settings.set_steem_node()

    bot = ClaimBot()
    bot.claim_all_scot_tokens(account)


@task(help={
      'debug': 'enable the debug mode'
      })
def all_users(ctx, debug=False):
    """ claim all the tokens of all accounts"""

    settings.set_steem_node()

    bot = ClaimBot()
    bot.claim_all_accounts()

