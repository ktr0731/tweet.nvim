# -*- coding: utf-8 -*-

import os
import re
import threading
import queue
import json

import neovim
from requests_oauthlib import OAuth1Session
from functools import wraps

from .twitter_api import TwitterAPI
from .timeline import Timeline


def homeTimelineRequired(func):
    @wraps(func)
    def checkHomeTimeline(*args, **kwargs):
        self = args[0]
        if 'home' not in self.timeline:
            self.echo("Please load Home Timeline!")
            return
        return func(*args)
    return checkHomeTimeline

@neovim.plugin
class TweetNvim(object):
    def __init__(self, nvim):
        self.nvim = nvim

        # ストリームを開いているウインドウ
        self.streams = {}
        self.queues = {}
        self.timeline = {}

        self.separater = re.compile('^-*$')

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
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable wrap")
            self.timeline['home'] = Timeline(self.nvim.command_output('echo win_getid()').strip())

        self.timeline['home'].fetch()
        content = ''
        for tweet in self.timeline['home'].tweets:
            if 'user' not in 'text' not in tweet:
                continue

            text = tweet['text'].replace('\n', '\n  ')
            text.rstrip()

            content += '{name} @{id}\n\n  {tweet}\n'.format(
                    name=tweet['user']['name'],
                    id=tweet['user']['screen_name'],
                    tweet=text,
                    created_at=tweet['created_at']
                    )

            window_width = self.nvim.current.window.width

            content += "-" * window_width + "\n"

        self.prependTweet(content)

    @homeTimelineRequired
    @neovim.command('Retweet')
    def retweet(self):
        end = self.nvim.current.window.cursor[0]

        cnt = 0
        for line in self.nvim.current.window.buffer[:end]:
            if self.separater.match(line) and line != "":
                cnt += 1

        id = self.timeline['home'].tweets[cnt]['id_str']
        self.timeline['home'].retweet(id)

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if 'home' in self.timeline:
            self.echo("Close timeline")
            del self.timeline['home']
