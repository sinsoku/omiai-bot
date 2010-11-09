#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import re
from models import *
from zipimport import zipimporter

tweepy_path = os.path.join('lib', 'tweepy-1.7.1-py2.5.egg')
tweepy = zipimporter(tweepy_path).load_module('tweepy')


class OmiaiBot(object):

    author = 'sinsoku_listy'
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
        tweets = self._filter_tweets(friends_tl)
        self._put_tweets(tweets)

    def reply_mentions(self):
        mentions = self.api.mentions()
        tweets = self._filter_tweets(mentions)
        self._put_tweets(tweets)

    def _filter_tweets(self, tweets):
        results = list()
        for tweet in tweets:
            if tweet.author.screen_name != 'omiai_bot':
                results.append(tweet)

        results = self.find_all(results, self.words)
        results = self.remove_all(results, self.exclude)

        return results

    def save_search(self):
        try:
            search_results = self.api.search(' OR '.join(self.words))
            self._add_userobject_info(search_result)
            tweets = [tweet for tweet in search_results
                            if tweet.author.screen_name != 'omiai_bot']
            tweets = self.remove_all(tweets, self.exclude)
            self._put_tweets(tweets)

            logging.info('save_search() is Success')
        except tweepy.TweepError, reason:
            logging.warning(reason)

    def _add_userobject_info(self, search_results):
        class UserObject(object):

            def __init__(self, id, screen_name):
                self.id = id
                self.screen_name = screen_name

        for tweet in search_results:
            tweet.author = UserObject(tweet.from_user_id, tweet.from_user)

    def forward_direct_messages(self):
        messages = self.api.direct_messages()

        for message in messages:
            if DirectMessagesModel.all().filter('id', message.id).count() == 0:
                status_data = (self.author, message.sender_screen_name,
                               message.text)
                status = u'd %s @%s: %s' % status_data
                self._update_status(status)

                db = DirectMessagesModel(id=message.id, text=message.text)
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
                db = FollowersModel(id=user.id, screen_name=user.screen_name)
                db.put()

    def update(self):
        tweets = StatusModel.all().filter('updated', False).fetch(3)

        for tweet in tweets:
            status = u'RT @%s: %s' % (tweet.author.screen_name, tweet.text)
            self._update_status(status)

            tweet.updated = True
            tweet.put()

    def _update_status(self, status):
        status = self._replace_screen_name(status)
        if len(status) < 140:
            self.api.update_status(status)
        else:
            self.api.update_status(status[0:137] + '...')

    def _replace_screen_name(self, status):
        status_list = status.split('@')
        regex = re.compile(r'(\w+)')

        for n in range(1, len(status_list)):
            tweet = status_list[n]
            screen_name = regex.search(tweet).group(0)
            query = FollowersModel.all()
            if query.filter('screen_name', screen_name).count() > 0:
                status_list[n] = '@' + tweet
            else:
                status_list[n] = '_' + tweet

        return ''.join(status_list)

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
            user = UserModel.all().filter('id', tweet.author.id).get()
            if user == None:
                user = UserModel(id=tweet.author.id,
                                 screen_name=tweet.author.screen_name)
                user.put()

            status = StatusModel.all().filter('id', tweet.id).get()
            if status == None:
                status = StatusModel(id=tweet.id, text=tweet.text,
                                     author=user.key(), updated=False)
                status.put()
