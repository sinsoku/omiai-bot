#!/usr/bin/env python
# -*- coding:utf-8 -*-

from main import application
from nose.tools import *
from webtest import TestApp


class TestMain(object):

    def test_application(self):
        app = TestApp(application())
        response = app.get('/')

        eq_('200 OK', response.status)
        ok_('Hello world!' in str(response))
