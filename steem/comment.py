# -*- coding:utf-8 -*-

import re
import html

from bs4 import BeautifulSoup
from markdown import markdown

from beem import Steem
from beem.comment import Comment
from beem.exceptions import ContentDoesNotExistsException
from beem.utils import construct_authorperm

from steem.settings import STEEM_HOST
from steem.scot import comment as scot_comment, token_info
from utils.logging.logger import logger


REGEX_IMAGE_URL = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)\.(jpg|jpeg|png|gif|svg)"


class SteemComment:

    def __init__(self, comment=None, author_perm=None, url=None, ops=None):
        self.comment = comment
        self.author_perm = author_perm
        self.url = url
        self.ops = ops

    def get_author_perm(self):
        if self.author_perm is None:
            if self.url is not None:
                self.author_perm = "/".join(self.url.split("/")[-2:])
            elif self.ops is not None:
                self.author_perm = construct_authorperm(self.ops)
        return self.author_perm

    def get_comment(self):
        if self.comment is None:
            self.comment = Comment(self.get_author_perm())
        return self.comment

    def get_url(self):
        if self.url is None:
            if self.author_perm:
                self.url = u"{}/{}".format(STEEM_HOST, self.author_perm)
            else:
                c = self.get_comment()
                if c.authorperm:
                    self.url = u"{}/{}".format(STEEM_HOST, c.authorperm)
                else:
                    self.url = u"{}/@{}/{}".format(STEEM_HOST, c.author, c.permlink)

        return self.url

    def get_text_body(self):
        """ Converts a markdown string to plaintext """

        # md -> html -> text since BeautifulSoup can extract text cleanly
        html = markdown(self.get_comment().body)

        # remove code snippets
        html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
        html = re.sub(r'<code>(.*?)</code >', ' ', html)

        # extract text
        soup = BeautifulSoup(html, "html.parser")
        text = ''.join(soup.findAll(text=True))

        text = re.sub(REGEX_IMAGE_URL, '', text)

        return text

    def get_tags(self):
        c = self.get_comment()
        if c.json_metadata and 'tags' in c.json_metadata:
            return c.json_metadata['tags']
        else:
            self.refresh()
            c = self.get_comment()
            if c.json_metadata and 'tags' in c.json_metadata:
                return c.json_metadata['tags']
        return []

    def has_tag(self, tag):
        return tag in self.get_tags()

    def has_tags(self, tags):
        if not tags or len(tags) == 0:
            return False
        for tag in tags:
            if self.has_tag(tag):
                return True
        return False

    def refresh(self):
        c = self.get_comment()
        try:
            c.refresh()
        except ContentDoesNotExistsException:
            logger.info("failed when refresh {}".format(self.get_url()))
            return None

        return c

    def log(self):
        c = self.get_comment()
        logger.info("@%s | %s | %s | %s" % (c.author, c.title, self.get_url(), c['created']))

    def is_commented_by(self, account):
        commented_by = [reply['author'] for reply in self.get_comment().get_replies()]
        return account in commented_by

    def _is_upvoted_by(self, account):
        voters = self.get_comment().get_curation_rewards()['active_votes'].keys()
        return account in voters

    def is_upvoted_by(self, account):
        has_upvoted = False
        for vote in self.get_comment().get_votes():
            if vote.voter == account and vote.percent > 0:
                has_upvoted = True
        return has_upvoted

    def is_downvoted_by(self, account):
        has_downvoted = False
        for vote in self.get_comment().get_votes():
            if vote.voter == account and vote.percent < 0:
                has_downvoted = True
        return has_downvoted

    def get_scot_value(self, token, item):
        data = scot_comment(self.get_comment().author, self.get_comment().permlink)
        if data:
            return data[token][item]
        else:
            return None

    def _get_payout_with_precision(self, token, payout, precision=None):
        precision = precision or token_info(token, "precision")
        if payout is not None and precision is not None:
            return float(payout) / pow(10, precision)
        else:
            return None

    def get_scot_pending_payout(self, token):
        pending_payout = self.get_scot_value(token, "pending_token")
        return _get_payout_with_precision(token, pending_payout)

    def get_scot_payout(self, token):
        total_payout = self.get_scot_value(token, "total_payout_value") or 0
        curator_payout = self.get_scot_value(token, "curator_payout_value") or 0
        beneficiaries_payout = self.get_scot_value(token, "beneficiaries_payout_value") or 0
        author_payout = total_payout - curator_payout
        precision = self.get_scot_value(token, "precision")
        return {
            "total": self._get_payout_with_precision(token, total_payout, precision),
            "curator": self._get_payout_with_precision(token, curator_payout, precision),
            "beneficiaries": self._get_payout_with_precision(token, beneficiaries_payout, precision),
            "author": self._get_payout_with_precision(token, author_payout, precision),
        }

    def get_steem_payout(self):
        payout = self.get_comment().get_rewards()
        steem_payout = {}
        if payout:
            for k, v in payout.items():
                symbol = v['symbol'].upper()
                if not symbol in steem_payout:
                    steem_payout[symbol] = {}
                key = k.replace("_payout", "")
                steem_payout[symbol][key] = float(v['amount'])
            return steem_payout
        else:
            return {}

    def get_payout(self):
        # steem payout
        steem_payout = self.get_steem_payout()
        payout = steem_payout or {}
        # scot payout
        tokens = self.get_relevant_tokens()
        for t in tokens:
            payout[t] = self.get_scot_payout(t)
        return payout

    def get_relevant_tokens(self):
        data = scot_comment(self.get_comment().author, self.get_comment().permlink)
        if data:
            return data.keys()
        else:
            return None

    def is_comment(self):
        return self.get_comment().is_comment()

    def author(self):
        return self.get_comment().author

    def body(self):
        return self.get_comment().body

    def parent_author(self):
        return self.get_comment().parent_author

    def parent_permlink(self):
        return self.get_comment().parent_permlink

    def get_parent_author_perm(self):
        return "@{}/{}".format(self.parent_author(), self.parent_permlink())

    def get_beneficiaries(self):
        return self.get_comment().get_beneficiaries_pct()
