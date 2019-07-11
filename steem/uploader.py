# -*- coding:utf-8 -*-

import traceback
from beem.imageuploader import ImageUploader

from utils.logging.logger import logger


class Uploader:

    def __init__(self, author):
        self.author = author
        self.uploader = ImageUploader()

    def upload(self, path):
        if path:
            try:
                res = self.uploader.upload(path, self.author)
                if res and 'url' in res:
                    url = res['url']
                    if url and len(url) > 0:
                        logger.info("Image [{}] uploaded to [{}] successfully".format(path, url))
                        return url
            except:
                logger.error("Failed when uploading image {}.\nError: {}".format(path, traceback.format_exc()))
        return None
