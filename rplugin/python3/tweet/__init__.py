# -*- coding: utf-8 -*-

import os
import threading
import queue
import json

import neovim
from requests_oauthlib import OAuth1Session

from .twitter_api import TwitterAPI

def hoge():
    raise Exception


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

        self.nvim = nvim
        self.api = TwitterAPI(keys)

        # ストリームを開いているウインドウ
        self.streams = {}
        self.queues = {}
        self.home_timeline = {'opened': False}

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    def prependTweet(self, tweets):
        self.nvim.command('setlocal modifiable')
        for line in tweets.split('\n')[::-1]:
            self.nvim.current.buffer.append(line, 0)
        self.nvim.command('setlocal nomodifiable')

    @neovim.command('Tweet', nargs='*', sync=True)
    def tweet(self, lines):
        if len(lines) == 0:
            self.echo('Usage: Tweet [line...]')

        content = ''
        for line in lines:
            content += line + '\n'

        self.api.tweet(content)

        self.echo('Tweeted')

    @neovim.command('Timeline')
    def timeline(self):
        if not self.home_timeline['opened']:
            self.nvim.command("setlocal splitright")
            self.nvim.command("vnew")
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")
            self.home_timeline['opened'] = True

        if 'since_id' in self.home_timeline:
            tweets = self.api.timeline(self.home_timeline['since_id'])
        else:
            tweets = self.api.timeline()

        if len(tweets) == 0:
            return

        content = ''
        for tweet in tweets:
            if 'user' not in 'text' not in 'created_at' not in tweet:
                continue

            content += '{name} @{id}\n\n{tweet}\n\n{created_at}\n'.format(
                    name=tweet['user']['name'],
                    id=tweet['user']['screen_name'],
                    tweet=tweet['text'],
                    created_at=tweet['created_at']
                    )
            content += "\n--------------------\n\n"

        self.home_timeline['since_id'] = tweets[0]['id_str']

        if 'window_id' not in self.home_timeline:
            self.home_timeline['window_id'] = self.nvim.command_output('echo win_getid()').strip()

        self.prependTweet(content)

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if self.home_timeline['opened']:
            self.echo("Close timeline")
            self.home_timeline['opened'] = False
            del self.home_timeline['since_id']
            del self.home_timeline['window_id']
