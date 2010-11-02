#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from zipimport import zipimporter

tweepy_path = os.path.join('lib', 'tweepy-1.7.1-py2.5.egg')
tweepy = zipimporter(tweepy_path).load_module('tweepy')


class OmiaiBot(object):

    def __init__(self):
        pass

    def parse_config(self, config_file):
        configs = config_file.readlines()

        self.consumer_key = configs[0].strip()
        self.consumer_secret = configs[1].strip()
        self.access_key = configs[2].strip()
        self.access_secret = configs[3].strip()

    def save(self):
        pass

    def update(self):
        pass

    def get_man_tweets(self, tweets):
        man_words = [u'彼女']
        return self._get_tweet_include_word(tweets, man_words)

    def get_woman_tweets(self, tweets):
        woman_words = [u'彼氏']
        return self._get_tweet_include_word(tweets, woman_words)

    def _get_tweet_include_word(self, tweets, words):
        result = list()
        for tweet in tweets:
            for word in words:
                if tweet.find(word) != -1:
                    result.append(tweet)
                    break

        return result
