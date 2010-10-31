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
