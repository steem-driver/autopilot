# -*- coding:utf-8 -*-

from steem.account import SteemAccount
from steem.comment import SteemComment
from utils.logging.logger import logger
from steem.scot import token_info as scot_token_info, token_config as scot_token_config


class Voter:

    def __init__(self, author):
        self.author = author
        self.account = SteemAccount(self.author)
        self.vp_limit = {}

    def vote(self, post, weight=100):
        if post:
            if weight and weight >= -100 and weight <= 100:
                if weight > 0:
                    if self.has_vp(up=True):
                        return self._upvote(post, weight)
                    else:
                        logger.error("{} has no enough VP for upvote".format(self.author))
                else:
                    if self.has_vp(up=False):
                        return self._downvote(post, weight)
                    else:
                        logger.error("{} has no enough VP for downvote".format(self.author))
            else:
                logger.error("Failed: the vote weight {} exceeds the range [-100, 100]".format(weight))
        return False

    def _upvote(self, post, weight):
        c = SteemComment(comment=post)
        if not c.is_upvoted_by(self.author):
            post.upvote(weight=weight, voter=self.author)
            logger.info("Upvoted to [{}] [{}] with weight [{:.2f}] successfully".format(post.title, c.get_url(), weight))
            return True
        else:
            logger.info("Skip upvote because I already upvoted this post [{}]  [{}]".format(post.title, c.get_url()))
            return False

    def _downvote(self, post, weight):
        c = SteemComment(comment=post)
        if not c.is_downvoted_by(self.author):
            post.downvote(weight=weight, voter=self.author)
            logger.info("Downvoted to [{}] [{}] with weight [{:.2f}] successfully".format(post.title, c.get_url(), weight))
            return True
        else:
            logger.info("Skip downvote because I already downvoted this post [{}] [{}]".format(post.title, c.get_url()))
            return False

    def estimate_vote_value_for_token(self, symbol, weight=100, up=True):
        token_voting_power = self.account.get_scot_voting_power(symbol, up)
        scot_staked = self.account.get_scot_staked(symbol)
        multiplier = self.account.get_vote_multiplier(symbol, up)

        pending_rshares = scot_token_info(symbol, "pending_rshares")
        reward_pool = scot_token_info(symbol, "reward_pool")
        precision = scot_token_info(symbol, "precision")
        author_curve_exponent = scot_token_config(symbol, "author_curve_exponent")

        # print ("estimate_vote_value", token_voting_power, scot_staked, pending_rshares, reward_pool, author_curve_exponent, multiplier)

        def apply_reward_curve(rshares):
            return pow(max(0, rshares), author_curve_exponent) * reward_pool / pending_rshares

        direction = 1 if up else - 1
        rshares = float(up) * float(scot_staked) * min(abs(multiplier * weight), 100) * float(token_voting_power) / (10000 * 100);
        # newValue = apply_reward_curve(voteRshares + rshares);
        # print ("reshares", rshares)
        value = apply_reward_curve(rshares)
        return round(value / pow(10, precision), precision)

    def estimate_vote_pct_for_token(self, symbol, value):
        up = True if value >= 0 else False
        token_voting_power = self.account.get_scot_voting_power(symbol, up)
        scot_staked = self.account.get_scot_staked(symbol)
        multiplier = self.account.get_vote_multiplier(symbol, up)

        pending_rshares = scot_token_info(symbol, "pending_rshares")
        reward_pool = scot_token_info(symbol, "reward_pool")
        precision = scot_token_info(symbol, "precision")
        author_curve_exponent = scot_token_config(symbol, "author_curve_exponent")

        # print ("get_vote_pct_for_token", token_voting_power, scot_staked, pending_rshares, reward_pool, author_curve_exponent, multiplier)

        def get_rshares_from_reward(reward):
            return pow(pending_rshares * reward / reward_pool, 1.0 / author_curve_exponent)

        if token_voting_power and scot_staked and pending_rshares and reward_pool and author_curve_exponent and multiplier:
            # calculation method
            # vote_value = vote_weight / 100 * voting_power / 100 * rshares / pending_rshares * reward_pool
            # reference: https://busy.org/@holger80/palnet-how-to-check-your-voting-power-and-your-pal-vote-value
            value = value * pow(10, precision)
            rshares = get_rshares_from_reward(value)
            # print ("reshares", rshares)
            vote_weight = 10000.0 * rshares / float(token_voting_power) / float(scot_staked / 100.0) / multiplier
            return vote_weight
        else:
            return None

    def set_vp_limit(self, token, limit):
        if token and limit:
            self.vp_limit[token] = limit

    def get_vp_limit(self, token):
        if token and token in self.vp_limit:
            return self.vp_limit[token]
        else:
            return 0

    def has_vp(self, token=None, up=True):
        if token:
            vp = self.account.get_scot_voting_power(token, up)
            if vp:
                if float(vp) / 100 >= self.get_vp_limit(token):
                    return True
            return False
        else:
            for k, v in self.vp_limit.items():
                vp = self.account.get_scot_voting_power(k, up)
                if not vp or float(vp) / 100 < float(v):
                    return False
            return True

    def estimate_vote_pct_for_n_votes(self, days, n):
        total_SBD = self.account.account.steem.sp_to_sbd(sp=self.account.steem_power()) * 10 * float(days)
        return float(self.account.account.get_vote_pct_for_SBD(total_SBD / n)) / 100
