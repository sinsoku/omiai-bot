#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from omiaibot import OmiaiBot
import os

_script_dir = os.path.dirname(__file__)
template_dir = os.path.join(_script_dir, 'template')


class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(template_dir, 'index.html')
        self.response.out.write(template.render(path, None))


class SearchHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(template_dir, 'search.html')
        self.response.out.write(template.render(path, None))


class TaskHandler(webapp.RequestHandler):

    def get(self, kind):
        bot = OmiaiBot(oauth_yamlname='oauth.txt')

        if kind == 'save_timeline':
            bot.save_timeline()
        elif kind == 'save_search':
            bot.save_search()
        elif kind == 'reply_mentions':
            bot.reply_mentions()
        elif kind == 'forward_direct_messages':
            bot.forward_direct_messages()
        elif kind == 'auto_refollow':
            bot.auto_refollow()
        elif kind == 'update_followers':
            bot.update_followers()
        elif kind == 'update':
            bot.update()
        else:
            self.response.out.write('no task')


def application():
    handlers = [('/', MainHandler),
                ('/search', SearchHandler),
                ('/task/?(.*)', TaskHandler)]

    return webapp.WSGIApplication(handlers, debug=True)


def main():
    util.run_wsgi_app(application())

if __name__ == '__main__':
    main()
