# -*- coding:utf-8 -*-

from steem.collector import query
from action.info.bot import InfoBot
from utils.logging.logger import logger

class InfoRecipe:

    def __init__(self):
        self.author = self.by()
        self.bot = InfoBot(author=self.author, mode=self.mode(), config=self.config())
        self.ops = None
        self.ctx = {}

    def mode(self):
        return "query.comment.post"

    def by(self):
        return None

    def config(self):
        return {}

    def vp_limit(self):
        return {}

    def data(self):
        mode = self.mode()
        config = self.config()
        if mode.startswith("query."):
            if mode == "query.comment.post":
                config['mode'] = "post"
            elif mode == "query.comment.comment":
                config['mode'] = "comment"
            elif mode == "query.comment.all":
                config['mode'] = "post+comment"
            return query(config)
        return []

    def title(self, data):
        return None

    def body(self, data):
        return None

    def tags(self, data):
        return None

    def ready(self, data):
        return True

    # def when_to_post(self, post):
    #     return 0

    # def context(self, ops):
    #     if isinstance(ops, Comment):
    #         self.ops = SteemComment(comment=ops)
    #     else:
    #         self.ops = SteemOperation(ops=ops)
    #     logger.debug("watch operation: {}; tags: {}".format(self.ops.get_url(), self.ops.get_tags()))

    def run(self):
        self.bot.get_data(self.data).get_title(self.title).get_body(self.body).get_tags(self.tags).is_ready(self.ready).run()
