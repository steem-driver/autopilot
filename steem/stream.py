# -*- coding:utf-8 -*-

import traceback

from beem.blockchain import Blockchain
from steem.comment import SteemComment

from utils.system.date import days_ago
from utils.logging.logger import logger

def default_callback(ops):
    print (ops["block_num"], ops["type"], ops["author"], ops["body"])

def monitor_posts():
    def print_post(ops):
        c = SteemComment(ops=ops)
        if not c.get_comment().is_comment():
            c.log()
    stream = SteemStream(operations=["comment"])
    stream.run(callback=print_post)

class SteemStream:
    def __init__(self, operations=[]):
        self.blockchain = Blockchain(mode="head")
        self.operations = operations
        self.last_streamed_block = 0
        self.max_batch_size = 50
        self.threading = False

    def run(self, callback=default_callback, lookback=0, start=-1, days=-1):
        try:
            if lookback > 0 or start > 0 or days > 0:
                if self.last_streamed_block == 0:
                    if start > 0:
                        start_block = start
                    elif lookback > 0:
                        start_block = self.blockchain.get_current_block_num() - int(lookback) #200000
                    else:
                        start_date = days_ago(days)
                        start_block = self.blockchain.get_estimated_block_num(start_date)
                else:
                    start_block = self.last_streamed_block + 1
                stop_block = self.blockchain.get_current_block_num()

                logger.info("Streaming for operations {} has started from block {} to {}".format(self.operations, start_block, stop_block))
                for ops in self.blockchain.stream(opNames=self.operations,
                            start=start_block, stop=stop_block,
                            max_batch_size=self.max_batch_size, threading=self.threading, thread_num=8):
                    try:
                        callback(ops)
                    except:
                        logger.error("Failed when procssing operation {} with error: {}".format(ops, traceback.format_exc()))
            else:
                logger.info("Streaming for operations {} has started from the latest blocks".format(self.operations))
                for ops in self.blockchain.stream(opNames=self.operations,
                            max_batch_size=self.max_batch_size, threading=self.threading, thread_num=8):
                    try:
                        callback(ops)
                    except:
                        logger.error("Failed when procssing operation {} with error: {}".format(ops, traceback.format_exc()))
        except:
            logger.error("Failed when streaming operations {} with error: {}".format(self.operations, traceback.format_exc()))

