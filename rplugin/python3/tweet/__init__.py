# -*- coding: utf-8 -*-

import neovim
from requests_oauthlib import OAuth1Session
from functools import wraps

from .twitter_api import TwitterAPI
from .timeline import Timeline


def timelineRequired(func):
    @wraps(func)
    def checkHomeTimeline(*args, **kwargs):
        self = args[0]

        if len(self.timeline) == 0:
            self.echo("Please load Timeline")
            return

        win_id = self.nvim.command_output('echo win_getid()').strip()
        win_ids = [timeline.win_id for timeline in self.timeline.values()]
        if win_id not in win_ids:
            self.echo("Move the cursor to the tweet you want to RT")
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
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nolist nonumber nomodifiable wrap")
            self.timeline['home'] = Timeline(self.nvim.command_output('echo win_getid()').strip())

        self.prependTweet(self.timeline['home'].generate(self.nvim.current.window.width))

    @timelineRequired
    @neovim.command('Retweet')
    def retweet(self):
        end = self.nvim.current.window.cursor[0]
        tweet = self.timeline['home'].retweet(self.nvim.current.window.buffer[:end])

        self.echo('Retweeted: {}'.format(tweet['text']))

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if 'home' in self.timeline:
            self.echo("Close timeline")
            del self.timeline['home']
