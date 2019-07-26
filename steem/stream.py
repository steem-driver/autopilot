# -*- coding:utf-8 -*-

from beem.blockchain import Blockchain
from steem.comment import SteemComment

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

    def run(self, callback=default_callback, lookback=0):
        if lookback > 0:
            if self.last_streamed_block == 0:
                start_block = self.blockchain.get_current_block_num() - int(lookback) #200000
            else:
                start_block = self.last_streamed_block + 1
            stop_block = self.blockchain.get_current_block_num()

            logger.info("Streaming for operations {} has started for {} to {}".format(self.operations, start_block, stop_block))
            for ops in self.blockchain.stream(opNames=self.operations,
                        start=start_block, stop=stop_block,
                        max_batch_size=self.max_batch_size, threading=self.threading, thread_num=8):
                callback(ops)
        else:
            logger.info("Streaming for operations {} has started the latest blocks".format(self.operations))
            for ops in self.blockchain.stream(opNames=self.operations,
                        max_batch_size=self.max_batch_size, threading=self.threading, thread_num=8):
                callback(ops)
