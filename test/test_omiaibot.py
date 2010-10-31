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
