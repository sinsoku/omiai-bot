#!/usr/bin/env python
# -*- coding:utf-8 -*-

from nose.tools import *
from omiaibot import OmiaiBot
from StringIO import StringIO


def ng_(expr, msg=None):
    return ok_(not expr, msg)


class TestOmiaiBot(object):

    def test_parse_config(self):
        bot = OmiaiBot()
        config_data = '\n'.join(['ConsumerKey', 'ConsumerSecret',
                                 'AccessKey', 'AccessSecret'])
        config_file = StringIO(config_data)

        bot.parse_config(config_file)

        eq_(bot.consumer_key, 'ConsumerKey')
        eq_(bot.consumer_secret, 'ConsumerSecret')
        eq_(bot.access_key, 'AccessKey')
        eq_(bot.access_secret, 'AccessSecret')

    def test_get_man_tweets(self):
        bot = OmiaiBot()
        tweets = [u'彼女ほしい', u'彼氏ほしい',
                  u'彼女欲しい', u'彼氏欲しい']

        man_tweets = bot.get_man_tweets(tweets)

        ok_(u'彼女ほしい' in man_tweets)
        ng_(u'彼氏ほしい' in man_tweets)
        ok_(u'彼女欲しい' in man_tweets)
        ng_(u'彼氏欲しい' in man_tweets)

    def test_get_woman_tweets(self):
        bot = OmiaiBot()
        tweets = [u'彼女ほしい', u'彼氏ほしい',
                  u'彼女欲しい', u'彼氏欲しい']

        woman_tweets = bot.get_woman_tweets(tweets)

        ng_(u'彼女ほしい' in woman_tweets)
        ok_(u'彼氏ほしい' in woman_tweets)
        ng_(u'彼女欲しい' in woman_tweets)
        ok_(u'彼氏欲しい' in woman_tweets)
