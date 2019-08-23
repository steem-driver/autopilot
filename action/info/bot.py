# -*- coding:utf-8 -*-

from utils.logging.logger import logger

import os
import time
import random
import traceback
from threading import Timer
from beem.comment import Comment

from steem.settings import settings, STEEM_HOST, STEEMD_HOST
from steem.comment import SteemComment
from steem.account import SteemAccount
from steem.writer import Writer
from steem.voter import Voter
from steem.uploader import Uploader
from steem.stream import SteemStream
from steem.collector import query, get_comments, get_posts
from utils.system.date import get_utc_date_str


class InfoBot:

    def __init__(self, author, mode="stream.comment", config={}):
        self.author = author
        self.writer = Writer(author=self.author)
        self.uploader = Uploader(author=self.author)
        self.mode = mode
        self.config = config

        # the configuration functions for a info bot
        self.data = lambda : []
        self.title = lambda : None
        self.body = lambda : None
        self.tags = lambda: None
        self.ready = lambda: True

    def _has_reply_comment(self, receiver, message_id):
        comments = self._read_comments()
        for c in comments:
            # check the receiver and the message_id fingerprint
            if c.parent_author == receiver and verify_message(message_id, c.body):
                logger.info("I found I replied to @{} with message [{}] by searching comment history".format(receiver, message_id))
                return (True, c)
        return (False, None)

    def _has_replied(self, receiver, message_id):
        # has reply records in DB, or has replied by checking steem APIs
        if self._has_reply_record(receiver, message_id):
            return True
        (replied, comment) = self._has_reply_comment(receiver, message_id)
        if replied:
            c = SteemComment(comment=comment.get_parent())
            # cache the record into database since not found
            self._add_reply_record(receiver, message_id, c, comment["created"])
            return True
        return False

    def _get_reply_body(self, message_id, author):
        account = SteemAccount(author)
        comments_num = account.remaining_comments() or ''
        daily_comments_num = round(account.daily_recovery_comments(), 1) or ''
        return get_message(message_id).format(name=author, comments_num=comments_num, daily_comments_num=daily_comments_num)

    def reply(self, message_id=None, post=None, url=None):
        """ reply to the' post """
        c = SteemComment(comment=post, url=url)
        receiver = c.get_comment().author
        if not self._has_replied(receiver, message_id):
            title = c.get_comment().title
            message = self._get_reply_body(message_id, receiver)
            self.writer.reply(c.get_comment(), message)
            self._add_reply_record(receiver, message_id, c)
            logger.info("Replied to @{}'s post [{}] with [{}] message".format(receiver, title, message_id))
            return True
        else:
            logger.info("Skip reply account @{} with [{}] message, because we already reliped before".format(receiver, message_id))
            return False

    def _has_published(self, title):
        posts = get_posts(account=self.author, limit=50)
        if len(posts) > 0:
            for post in posts:
                if post.title == title:
                    return True
        return False

    def _get_time_str(self):
        return get_utc_date_str()

    def _get_accessible_url(self, url):
        if url and len(url) > 0:
            return url.replace(STEEM_HOST, ACCESSIBLE_STEEM_HOST)
        return ""

    def publish(self, title, body, tags):
        """ publish the post """
        if not self._has_published(title):
            self.writer.post(title, body, tags)
            logger.info("I have published the post [{}] successfully".format(title))
            return True
        else:
            logger.info("Skip this post [{}], because I already published the post with the same title".format(title))
            return False

    def get_votes(self, authors, up=None):
        votes = []
        for author in authors:
            acc = SteemAccount(author=author)
            my_votes = acc.get_votes(up)
            for v in my_votes:
                v['voter'] = author
            votes += my_votes
        return votes

    def get_data(self, data):
        self.data = data
        return self

    def get_title(self, title):
        self.title = title
        return self

    def get_body(self, body):
        self.body = body
        return self

    def get_tags(self, tags):
        self.tags = tags
        return self

    def is_ready(self, ready):
        self.ready = ready
        return self

    def run(self):
        data = self.data()
        title = self.title(data)
        body = self.body(data)
        tags = self.tags(data)
        if self.ready(data):
            self.publish(title, body, tags)
