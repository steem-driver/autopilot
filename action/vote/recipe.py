# -*- coding:utf-8 -*-

from action.vote.bot import VoteBot
from steem.operation import SteemOperation
from utils.logging.logger import logger

class VoteRecipe:

    def __init__(self):
        self.author = self.by()
        self.bot = VoteBot(author=self.author)
        self.voter = self.bot.voter
        self.ops = None
        self.ctx = {}
        for k, v in self.vp_limit().items():
            logger.info ("set VP limit of {} to {}%".format(k, v))
            self.voter.set_vp_limit(k, v)

    def by(self):
        return None

    def vp_limit(self):
        return {}

    def what_to_vote(self, ops):
        return None

    def who_to_vote(self, author):
        return True

    def when_to_vote(self, post):
        return 15

    def how_to_vote(self, post):
        return 50

    def is_ready(self):
        return self.voter.has_vp()

    def context(self, ops):
        self.ops = SteemOperation(ops=ops)
        logger.debug("watch comment: {}; tags: {}".format(self.ops.get_url(), self.ops.get_tags()))

    def run(self):
        self.bot.context(self.context).what(self.what_to_vote).who(self.who_to_vote).ready(self.is_ready).when(self.when_to_vote).how(self.how_to_vote).run()
