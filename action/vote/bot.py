# -*- coding:utf-8 -*-

from utils.logging.logger import logger

import os
import time
import random
import traceback
from threading import Thread, Timer
from beem.comment import Comment

from steem.settings import settings
from steem.comment import SteemComment
from steem.account import SteemAccount
from steem.writer import Writer
from steem.voter import Voter
from steem.uploader import Uploader
from steem.stream import SteemStream
from steem.collector import query

MINIMUM_VOTE_INTERVAL = 3 # seconds
VOTE_RETRIES = 5

class VoteBot:

    def __init__(self, author, mode="stream.comment", config={}):
        self.author = author
        self.writer = Writer(author=self.author)
        self.voter = Voter(author=self.author)
        self.uploader = Uploader(author=self.author)
        self.mode = mode
        self.config = config

        # the configuration functions for a vote bot
        self.what_to_vote = None
        self.who_to_vote = lambda : True
        self.when_to_vote = lambda : 15
        self.how_to_vote = lambda : 50
        self.is_ready = lambda: True
        self.after_success = lambda : True

        self.last_vote_timestamp = -1
        self._vote_queue = []

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

    def reply(self, message_id, post=None, url=None):
        """ reply to the newbies' post """
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

    def vote(self, post=None, url=None, weight=None, retries=VOTE_RETRIES):
        c = SteemComment(comment=post, url=url)
        if retries <= 0:
            logger.error("Vote {} failed after retries for {} times".format(c.get_url(), VOTE_RETRIES))
            return False

        while time.time() - self.last_vote_timestamp < MINIMUM_VOTE_INTERVAL:
            wait_time = round(MINIMUM_VOTE_INTERVAL + random.random() * MINIMUM_VOTE_INTERVAL * 0.2, 2)
            logger.info("Sleep {} seconds to avoid voting too frequently.".format(wait_time))
            time.sleep(wait_time)
            if time.time() - self.last_vote_timestamp >= MINIMUM_VOTE_INTERVAL:
                return self.vote(post, url, weight, retries-1)

        success = False
        try:
            weight = weight or self.weight(c)
            success = self.voter.vote(c.get_comment(), weight=weight)
            self.last_vote_timestamp = time.time()
        except:
            logger.error("Failed when voting {} with error: {} . {} retry times left.".format(c.get_url(), traceback.format_exc(), retries-1))
            return self.vote(post, url, weight, retries-1)

        self.after_success(success)
        return success

    def start_vote_queue(self):
        logger.info("Start Vote Queue...")

        def wait_for_vote():
            while True:
                while(len(self._vote_queue) > 0):
                    post = self._vote_queue.pop(0)
                    self.vote(post)
                time.sleep(1)
            logger.info("Vote Queue Stopped.")

        Thread(target=wait_for_vote).start()

    def append_to_vote_queue(self, post):
        self._vote_queue.append(post)

    def what(self, what_to_vote):
        """ define the condition of vote for a post """
        self.what_to_vote = what_to_vote
        return self

    def when(self, when_to_vote):
        """ define the timing of vote for a post """
        self.when_to_vote = when_to_vote
        return self

    def who(self, who_to_vote):
        """ define when to vote the post """
        self.who_to_vote = who_to_vote
        return self

    def how(self, how_to_vote):
        """ define the weight of vote the post """
        self.how_to_vote = how_to_vote
        return self

    def ready(self, is_ready):
        """ define voter has met energy or other requirements """
        self.is_ready = is_ready
        return self

    def done(self, after_success):
        """ define the callback after vote is completed successfully """
        self.after_success = after_success
        return self

    def context(self, ctx):
        self.ctx = ctx
        return self

    def weight(self, post):
        return self.how_to_vote(post)

    def watch(self, ops):
        author = ops['author']

        def perform_vote():
            if isinstance(ops, Comment):
                c = SteemComment(comment=ops)
            else:
                c = SteemComment(ops=ops)
            self.append_to_vote_queue(post=c.get_comment())

        self.ctx(ops)
        if self.what_to_vote(ops) and self.who_to_vote(author) and self.is_ready():
            delay = self.when_to_vote(ops) # mins
            if delay is not None and delay > 0:
                secs = 60.0 * delay
                logger.info("I'll vote after {} seconds".format(secs))
                t = Timer(secs, perform_vote)
                t.start()
            else:
                logger.info("I'll vote immediately")
                perform_vote()

    def run(self):
        self.start_vote_queue()
        if self.mode.startswith("stream."):
            if self.mode == "stream.comment":
                stream = SteemStream(operations=["comment"])
            elif self.mode == "stream.vote":
                stream = SteemStream(operations=["vote"])
            stream.run(callback=self.watch)
        elif self.mode.startswith("query."):
            if self.mode == "query.comment.post":
                self.config['mode'] = "post"
            elif self.mode == "query.comment.comment":
                self.config['mode'] = "comment"
            elif self.mode == "query.comment.all":
                self.config['mode'] = "post+comment"
            for c in query(self.config):
                self.watch(c)
