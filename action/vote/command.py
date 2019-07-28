# -*- coding:utf-8 -*-

from invoke import task

from steem.voter import Voter
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


@task(help={
      'account': 'the name of the user to estimate vote value',
      'token': 'the token to esimate the vote value',
      'weight': 'the weight to vote',
      'debug': 'enable debug mode'
      })
def estimate_value(ctx, account, token, weight=100, debug=False):
    """ estimate the vote value of account """

    if debug:
        settings.set_debug_mode()
    settings.set_steem_node()

    print (Voter(account).estimate_vote_value_for_token(token, weight))


@task(help={
      'account': 'the name of the user to estimate vote value',
      'token': 'the token to esimate the vote value',
      'value': 'the target value to vote',
      'debug': 'enable debug mode'
      })
def estimate_weight(ctx, account, token, value, debug=False):
    """ estimate the needed weight to reach the vote value """

    if debug:
        settings.set_debug_mode()
    settings.set_steem_node()

    weight = Voter(account).estimate_vote_pct_for_token(token, float(value))
    print ("{}%".format(round(weight, 2)))



