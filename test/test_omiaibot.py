#!/usr/bin/env python
# -*- coding:utf-8 -*-

import mock
from nose.tools import *
from models import UserModel, StatusModel, FollowersModel
from omiaibot import OmiaiBot
from StringIO import StringIO


class TestOmiaiBot(object):

    def test_init_when_no_auth_api(self):
        bot = OmiaiBot(oauth_yamlname=None)

        eq_(bot.api.auth, None)

    def test_init_when_auth_api(self):
        bot = OmiaiBot(oauth_yamlname='oauth.txt')

        ok_(bot.api.auth)

    def test_find_all(self):
        bot = OmiaiBot()
        tweets = [mock.Status(31, 30, u'find_all_user', u'hoge text'),
                  mock.Status(32, 30, u'find_all_user', u'foo text'),
                  mock.Status(33, 30, u'find_all_user', u'test bar text')]
        words = [u'foo', u'bar']

        tweets = bot.find_all(tweets, words)

        eq_(len(tweets), 2)
        eq_(tweets[0].text, u'foo text')
        eq_(tweets[1].text, u'test bar text')

    def test_remove_all(self):
        bot = OmiaiBot()
        tweets = [mock.Status(31, 30, u'find_all_user', u'hoge text'),
                  mock.Status(32, 30, u'find_all_user', u'foo text'),
                  mock.Status(33, 30, u'find_all_user', u'test bar text')]
        exclude = [u'test']

        tweets = bot.remove_all(tweets, exclude)

        eq_(len(tweets), 2)
        eq_(tweets[0].text, u'hoge text')
        eq_(tweets[1].text, u'foo text')

    def test_put_tweets_when_data_is_simple(self):
        data = [mock.Status(1, 1, u'user_name', u'text')]

        bot = OmiaiBot()
        bot._put_tweets(data)

        query = StatusModel.all()
        tweet = query.filter('id >', 0L).filter('id <', 10L).get()

        eq_(tweet.id, 1L)
        eq_(tweet.text, u'text')
        eq_(tweet.author.screen_name, u'user_name')
        eq_(tweet.updated, False)

    def test_put_tweets_when_data_is_multiple(self):
        data = [mock.Status(11, 11, u'user1', u'text1'),
                mock.Status(12, 12, u'user2', u'text2')]

        bot = OmiaiBot()
        bot._put_tweets(data)

        query = StatusModel.all()
        tweets = query.filter('id >', 10L).filter('id <', 20L).fetch(2)

        eq_(tweets[0].id, 11L)
        eq_(tweets[0].text, u'text1')
        eq_(tweets[0].author.screen_name, u'user1')
        eq_(tweets[0].updated, False)

        eq_(tweets[1].id, 12L)
        eq_(tweets[1].text, u'text2')
        eq_(tweets[1].author.screen_name, u'user2')
        eq_(tweets[1].updated, False)

    def test_put_tweets_when_exist_same_user(self):
        data = [mock.Status(21, 20, u'same_user', u'text1'),
                mock.Status(22, 20, u'same_user', u'text2')]

        bot = OmiaiBot()
        bot._put_tweets(data)

        query = UserModel.all()
        users = query.filter('screen_name', u'same_user').fetch(2)

        eq_(len(users), 1)

    def test_put_tweets_when_exist_same_tweet(self):
        data = [mock.Status(41, 40, u'same_tweet', u'text1'),
                mock.Status(41, 40, u'same_tweet', u'text1')]

        bot = OmiaiBot()
        bot._put_tweets(data)

        query = StatusModel.all()
        users = query.filter('id', 41L).fetch(2)

        eq_(len(users), 1)

    def test_replace_screen_name(self):
        bot = OmiaiBot()
        status = u'RT @sinsoku_listy: @no_db_user'
        user = FollowersModel(id=0, screen_name='sinsoku_listy')
        user.put()

        status = bot._replace_screen_name(status)

        eq_(status, u'RT @sinsoku_listy: _no_db_user')
