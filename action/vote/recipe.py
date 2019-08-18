# -*- coding:utf-8 -*-

from beem.comment import Comment
from action.vote.bot import VoteBot
from steem.comment import SteemComment
from steem.operation import SteemOperation
from utils.logging.logger import logger

class VoteRecipe:

    def __init__(self):
        self.author = self.by()
        self.bot = VoteBot(author=self.author, mode=self.mode(), config=self.config())
        self.voter = self.bot.voter
        self.ops = None
        self.ctx = {}
        for k, v in self.vp_limit().items():
            logger.info ("set VP limit of {} to {}%".format(k, v))
            self.voter.set_vp_limit(k, v)

    def mode(self):
        return "stream.comment"

    def by(self):
        return None

    def config(self):
        return {}

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
        return True # self.voter.has_vp()

    def after_success(self):
        return True

    def context(self, ops):
        if isinstance(ops, Comment):
            self.ops = SteemComment(comment=ops)
        else:
            self.ops = SteemOperation(ops=ops)
        logger.debug("watch operation: {}; tags: {}".format(self.ops.get_url(), self.ops.get_tags()))

    def run(self):
        self.bot.context(self.context).what(self.what_to_vote).who(self.who_to_vote).ready(self.is_ready).when(self.when_to_vote).how(self.how_to_vote).done(self.after_success).run()
