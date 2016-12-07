# -*- coding: utf-8 -*-

import os

from requests_oauthlib import OAuth1Session
import neovim


@neovim.plugin
class TweetNvim(object):
    def __init__(self, nvim):
        keys = ['CONSUMER', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
        self.keys = {}
        for key in keys:
            if os.getenv('TWEET_NVIM_' + key) is None:
                exit(1)
            else:
                self.keys[key] = os.getenv('TWEET_NVIM_' + key)

        self.nvim = nvim

    @neovim.command('Tweet', nargs='*')
    def tweet(self, lines):
        url = 'https://api.twitter.com/1.1/statuses/update.json'

        content = ''
        for line in lines:
            content += line + '\n'

        twitter = OAuth1Session(
                    self.keys[0],
                    self.keys[1],
                    self.keys[2],
                    self.keys[3]
                )

        params = {'status': content}

        r = twitter.post(url, params=params)
