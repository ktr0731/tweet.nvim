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
                raise Exception('Required environment variables are missing!')
            else:
                self.keys[key] = os.getenv('TWEET_NVIM_' + key)

        self.nvim = nvim

    @neovim.command('Tweet', nargs='*', sync=True)
    def tweet(self, lines):
        if len(lines) == 0:
            raise Exception('Usage: Tweet [line...]')

        url = 'https://api.twitter.com/1.1/statuses/update.json'

        content = ''
        for line in lines:
            content += line + '\n'

        twitter = OAuth1Session(
                    self.keys['CONSUMER'],
                    self.keys['CONSUMER_SECRET'],
                    self.keys['ACCESS_TOKEN'],
                    self.keys['ACCESS_TOKEN_SECRET'])

        params = {'status': content}

        r = twitter.post(url, params=params)
