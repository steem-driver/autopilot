# -*- coding:utf-8 -*-

import requests
import time
# from steem.settings import settings
# from utils.logging.logger import logger

SCOT_API_URL = "https://scot-api.steem-engine.com/{}"

cached = {
    "token_info": {},
    "token_config": {}
}

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

def token_data(key, symbol):
    if symbol is not None:
        cached_key = 'token_{}'.format(key)
        if symbol in cached[cached_key]:
            info = cached[cached_key][symbol]
            if time.time() < info['expiration']:
                return info['data']
        info = {}
        info['data'] = _http_api("{}?token={}".format(key, symbol))
        info['expiration'] = time.time() + 60 * 5 # minutes
        cached[cached_key][symbol] = info
        return info['data']
    return None

def token_item(key, symbol, item):
    data = token_data(key, symbol)
    if data is not None:
        if item is not None:
            if item in data:
                return data[item]
        else:
            return data
    return None

def token_info(symbol, item=None):
    return token_item("info", symbol, item)

def token_config(symbol, item=None):
    return token_item("config", symbol, item)
