#!/usr/bin/env python
# -*- coding:utf-8 -*-


class MockUser(object):

    def __init__(self, id, screen_name):
        self.id = id
        self.screen_name = screen_name


class MockStatus(object):

    def __init__(self, id, user_id, screen_name, text):
        self.id = id
        self.author = MockUser(user_id, screen_name)
        self.text = text
