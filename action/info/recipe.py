# -*- coding:utf-8 -*-

from action.info.bot import InfoBot
from utils.logging.logger import logger

class InfoRecipe:

    def __init__(self):
        self.author = self.by()
        self.bot = InfoBot(author=self.author, mode=self.mode(), config=self.config())
        self.ops = None
        self.ctx = {}

    def mode(self):
        return "query.vote.downvote"

    def by(self):
        return None

    def config(self):
        return {}

    def vp_limit(self):
        return {}

    def data(self):
        return None

    def title(self, data):
        return None

    def body(self, data):
        return None

    def tags(self, data):
        return None

    # def when_to_post(self, post):
    #     return 0

    # def context(self, ops):
    #     if isinstance(ops, Comment):
    #         self.ops = SteemComment(comment=ops)
    #     else:
    #         self.ops = SteemOperation(ops=ops)
    #     logger.debug("watch operation: {}; tags: {}".format(self.ops.get_url(), self.ops.get_tags()))

    def run(self):
        self.bot.get_data(self.data).get_title(self.title).get_body(self.body).get_tags(self.tags).run()
