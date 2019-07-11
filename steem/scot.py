# -*- coding:utf-8 -*-

import requests
# from steem.settings import settings
# from utils.logging.logger import logger

SCOT_API_URL = "https://scot-api.steem-engine.com/{}"


def _http_api(path):
    r = requests.get(SCOT_API_URL.format(path))
    if r.ok:
        return r.json()
    else:
        return None

def author(author):
    return _http_api("@"+author)

def comment(author, permlink):
    return _http_api("@"+author+"/"+permlink)
