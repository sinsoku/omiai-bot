#!/usr/bin/env python
# -*- coding:utf-8 -*-

from main import application
from nose.tools import *
from webtest import TestApp


class TestMainHandler(object):

    def test_get(self):
        app = TestApp(application())
        response = app.get('/')

        eq_('200 OK', response.status)
        ok_('MainHandler', str(response))


class TestSearchHandler(object):

    def test_get(self):
        app = TestApp(application())
        response = app.get('/search')

        eq_('200 OK', response.status)
        #ok_(, str(response))


class TestTaskHandler(object):

    def test_get_when_task_is_none(self):
        app = TestApp(application())
        response = app.get('/task')

        eq_('200 OK', response.status)
        ok_('no task' in str(response))
