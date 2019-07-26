# -*- coding:utf-8 -*-

import re
import html
import json

from bs4 import BeautifulSoup
from markdown import markdown

from beem import Steem
from beem.comment import Comment
from beem.exceptions import ContentDoesNotExistsException
from beem.utils import construct_authorperm

from steem.settings import STEEM_HOST
from utils.logging.logger import logger


REGEX_IMAGE_URL = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)\.(jpg|jpeg|png|gif|svg)"


class SteemOperation:

    def __init__(self, ops=None):
        self.ops = ops
        self.author_perm = None
        self.url = None
        self.comment = None

    def get_author_perm(self):
        if self.author_perm is None:
            return construct_authorperm(self.ops)
        return self.author_perm

    def get_comment(self):
        if self.comment is None:
            self.comment = Comment(self.get_author_perm())
        return self.comment

    def is_comment(self):
        return 'parent_author' in self.ops and len(self.ops['parent_author']) > 0

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
        if 'json_metadata' in self.ops and len(self.ops['json_metadata']) > 0:
            metadata = json.loads(self.ops['json_metadata'])
            if 'tags' in metadata:
                tags = metadata['tags']
                if isinstance(tags, list):
                    return tags
                else:
                    return [tags]
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

    def log(self):
        pass

