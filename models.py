#!/usr/bin/env python
# -*- coding:utf-8 -*-

from google.appengine.ext import db


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
