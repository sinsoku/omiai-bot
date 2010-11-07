#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
from google.appengine.ext import db
from zipimport import zipimporter

tweepy_path = os.path.join('lib', 'tweepy-1.7.1-py2.5.egg')
tweepy = zipimporter(tweepy_path).load_module('tweepy')


class UserModel(db.Model):
    id = db.IntegerProperty()
    screen_name = db.StringProperty()


class StatusModel(db.Model):
    id = db.IntegerProperty()
    text = db.TextProperty()
    author = db.ReferenceProperty(UserModel)
    updated = db.BooleanProperty()


class FollowersModel(db.Model):
    id = db.IntegerProperty()
    screen_name = db.StringProperty()


class DirectMessagesModel(db.Model):
    id = db.IntegerProperty()
    text = db.TextProperty()


class OmiaiBot(object):

    words = [u'彼女ほしい', u'彼女欲しい',
             u'彼氏ほしい', u'彼氏欲しい']
    exclude = [u'http://']

    def __init__(self, init_api=True):
        if init_api:
            config_file = open('oauth.txt', 'r')
            auth_info = self._parse_config(config_file)

            auth = tweepy.OAuthHandler(auth_info['consumer_key'],
                                       auth_info['consumer_secret'])
            auth.set_access_token(auth_info['access_key'],
                                  auth_info['access_secret'])
            self.api = tweepy.API(auth)

    def _parse_config(self, config_file):
        auth_info = dict()
        for line in config_file.readlines():
            key, value = line.split('=')
            auth_info[key.strip()] = value.strip()

        return auth_info

    def save_timeline(self):
        friends_tl = self.api.friends_timeline()
        tweets = [tweet for tweet in friends_tl
                  if tweet.author.screen_name != 'omiai_bot']
        tweets = self.find_all(tweets, self.words)
        tweets = self.remove_all(tweets, self.exclude)
        self._put_tweets(tweets)

    def save_search(self):
        search_result = self.api.search(' OR '.join(self.words))
        for tweet in search_result:
            # ユーザオブジェクトの代用に無理やりlambdaを使用
            author = lambda x: x
            author.id = tweet.from_user_id
            author.screen_name = tweet.from_user
            tweet.author = author

        tweets = [tweet for tweet in search_result
                  if tweet.author.screen_name != 'omiai_bot']
        tweets = self.remove_all(tweets, self.exclude)
        self._put_tweets(tweets)

    def reply_mentions(self):
        mentions = self.api.mentions()
        tweets = [tweet for tweet in mentions
                  if tweet.author.screen_name != 'omiai_bot']
        tweets = self.find_all(tweets, self.words)
        tweets = self.remove_all(tweets, self.exclude)
        self._put_tweets(tweets)

    def forward_direct_messages(self):
        messages = self.api.direct_messages()

        for message in messages:
            if DirectMessagesModel.all().filter('id', message.id).count() == 0:
                status_data = {'forward_user': 'sinsoku_listy',
                               'user': message.sender_screen_name,
                               'text': message.text}
                status = 'd %(forward_user)s @%(user)s: %(text)s' % status_data
                if len(status) < 140:
                    self.api.update_status(status)
                else:
                    self.api.update_status(status[0:137] + '...')

                db = DirectMessagesModel()
                db.id = message.id
                db.text = message.text
                db.put()

    def auto_refollow(self):
        friends_ids = self.api.friends_ids()
        followers = self.api.followers()

        for user in followers:
            if not user.protected and not user.id in friends_ids:
                self.api.create_friendship(user.screen_name)

    def update_followers(self):
        followers = self.api.followers()

        for user in followers:
            if FollowersModel.all().filter('id', user.id).count() == 0:
                db = FollowersModel()
                db.id = user.id
                db.screen_name = user.screen_name
                db.put()

    def update(self):
        tweets = StatusModel.all().filter('updated', False).fetch(3)

        for tweet in tweets:
            status = 'RT @%s: %s' % (tweet.author.screen_name, tweet.text)
            status = re.sub('@', '_', status)
            if len(status) < 140:
                self.api.update_status(status)
            else:
                self.api.update_status(status[0:137] + '...')

            tweet.updated = True
            tweet.put()

    def find_all(self, tweets, words):
        results = list()
        for tweet in tweets:
            for word in words:
                if tweet.text.find(word) != -1:
                    results.append(tweet)
                    break

        return results

    def remove_all(self, tweets, exclude):
        results = list()
        for tweet in tweets:
            for word in exclude:
                if tweet.text.find(word) == -1:
                    results.append(tweet)
                    break

        return results

    def _put_tweets(self, tweets):
        for tweet in tweets:
            query = UserModel.all()
            query = query.filter('id', tweet.author.id)
            user = query.get()
            if user == None:
                user = UserModel()
                user.id = tweet.author.id
                user.screen_name = tweet.author.screen_name
                user.put()

            query = StatusModel.all().filter('id', tweet.id)
            status = query.get()
            if status == None:
                status = StatusModel()
                status.id = tweet.id
                status.text = tweet.text
                status.author = user.key()
                status.updated = False
                status.put()
