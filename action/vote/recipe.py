# -*- coding:utf-8 -*-

from action.vote.bot import VoteBot
from steem.operation import SteemOperation
from utils.logging.logger import logger

class VoteRecipe:

    def __init__(self):
        self.bot = VoteBot(author=self.by())
        self.ops = None
        self.ctx = {}

    def by(self):
        return None

    def what_to_vote(self, ops):
        return None

    def who_to_vote(self, author):
        return True

    def when_to_vote(self, post):
        return 15

    def how_to_vote(self, post):
        return 50

    def context(self, ops):
        self.ops = SteemOperation(ops=ops)
        logger.info("watch comment: {}; tags: {}".format(self.ops.get_url(), self.ops.get_tags()))

    def run(self):
        self.bot.context(self.context).what(self.what_to_vote).who(self.who_to_vote).when(self.when_to_vote).how(self.how_to_vote).run()
