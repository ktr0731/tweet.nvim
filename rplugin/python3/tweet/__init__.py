# -*- coding: utf-8 -*-

import os

from requests_oauthlib import OAuth1Session
import neovim


@neovim.plugin
class TweetNvim(object):
    def __init__(self, nvim):
        keys = {
                'CONSUMER': '',
                'CONSUMER_SECRET': '',
                'ACCESS_TOKEN': '',
                'ACCESS_TOKEN_SECRET': ''
                }

        for key in keys.keys():
            # TODO: Vim 変数も確認する
            if os.getenv('TWEET_NVIM_{}'.format(key)) is None:
                raise Exception('Required environment variables are missing!')
            else:
                keys[key] = os.getenv('TWEET_NVIM_{}'.format(key))

        self.twitter = OAuth1Session(
                    keys['CONSUMER'],
                    keys['CONSUMER_SECRET'],
                    keys['ACCESS_TOKEN'],
                    keys['ACCESS_TOKEN_SECRET'])

        self.nvim = nvim

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    @neovim.command('Tweet', nargs='*', sync=True)
    def tweet(self, lines):
        if len(lines) == 0:
            self.echo('Usage: Tweet [line...]')

        url = 'https://api.twitter.com/1.1/statuses/update.json'

        content = ''
        for line in lines:
            content += line + '\n'

        params = {'status': content}

        r = self.twitter.post(url, params=params)
        self.echo('Tweeted')

    @neovim.command('TwitterTimeline')
    def timeline(self):
        self.nvim.command("setlocal splitright")
        self.nvim.command("vnew")
        self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")
