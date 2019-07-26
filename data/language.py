# -*- coding:utf-8 -*-

import traceback
from langdetect import detect, detect_langs

from utils.logging.logger import logger


TIMES = 5


class PageLanguage:

    def __init__(self, text):
        self.text = text

    def detect(self, strict=True):
        try:
            summary = {}
            for i in range(0, TIMES):
                results = detect_langs(self.text)
                for res in results:
                    lang = res.lang
                    prob = float(res.prob) #float
                    if not lang in summary:
                        summary[lang] = prob
                    else:
                        summary[lang] += prob
            languages = sorted(summary, key=summary.get, reverse=True)
            language = languages[0]
            logger.info ("language detection: lang = {} ; summary = {}".format(language, summary))
            if strict:
                return language
            else:
                return languages
        except:
            logger.info("failed when detecting language for text: {}\nError: {}".format(self.text, traceback.format_exc()))
            return None
