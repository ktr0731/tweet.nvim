# -*- coding: utf-8 -*-

import os
import threading
import queue
import json

import neovim
from requests_oauthlib import OAuth1Session

from .twitter_api import TwitterAPI
from .timeline import Timeline

@neovim.plugin
class TweetNvim(object):
    def __init__(self, nvim):
        self.nvim = nvim

        # ストリームを開いているウインドウ
        self.streams = {}
        self.queues = {}
        self.timeline = {}

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    def prependTweet(self, tweets):
        self.nvim.command('setlocal modifiable')

        for line in tweets.split('\n')[::-1]:
            self.nvim.current.buffer.append(line, 0)

        self.nvim.current.window.cursor = (1, 1)
        self.nvim.command('setlocal nomodifiable')

    @neovim.command('Tweet', nargs='*', sync=True)
    def tweet(self, lines):
        if len(lines) == 0:
            self.echo('Usage: Tweet [line...]')

        content = ''
        for line in lines:
            content += line + '\n'

        # self.api.tweet(content)

        self.echo('Tweeted')

    @neovim.command('HomeTimeline')
    def home_timeline(self):
        if 'home' not in self.timeline:
            self.nvim.command("setlocal splitright")
            self.nvim.command("vnew")
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")
            self.timeline['home'] = Timeline(self.nvim.command_output('echo win_getid()').strip())

        content = ''
        for tweet in self.timeline['home'].tweets:
            if 'user' not in 'text' not in tweet:
                continue

            content += '{name} @{id}\n\n{tweet}\n'.format(
                    name=tweet['user']['name'],
                    id=tweet['user']['screen_name'],
                    tweet=tweet['text'],
                    created_at=tweet['created_at']
                    )

            window_width = self.nvim.current.window.width

            content += "-" * window_width + "\n"

        self.prependTweet(content)

    @neovim.command('Retweet')
    def retweet(self):
        # ツイート行と配列を対応させる
        # TODO: 明らかに効率悪そう, キャッシュ撮ったほうがよさ
        for i in self.nvim.current.window.buffer[:]:
            self.echo(i)

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if 'home' in self.timeline:
            self.echo("Close timeline")
            del self.timeline['home']
