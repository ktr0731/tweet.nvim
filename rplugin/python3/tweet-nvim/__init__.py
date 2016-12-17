# -*- coding: utf-8 -*-

import neovim
from requests_oauthlib import OAuth1Session
from functools import wraps

from .twitter_api import TwitterAPI
from .timeline import Timeline


def timelineRequired(func):
    @wraps(func)
    def checkTimeline(*args, **kwargs):
        self = args[0]

        if len(self.timeline) == 0:
            self.echo("Please load Timeline")
            return

        win_id = self.nvim.current.window.number
        win_ids = [timeline.win_id for timeline in self.timeline.values()]
        if win_id not in win_ids:
            self.echo("Move the cursor to the tweet you want to RT, Like or Reply")
            return

        return func(*args)
    return checkTimeline

@neovim.plugin
class TweetNvim(object):
    def __init__(self, nvim):
        self.nvim = nvim

        self.timeline = {}
        self.lists = {}
        for list in TwitterAPI().lists():
            self.lists[list['name']] = list['id_str']

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    def prependTweet(self, tweets):
        self.nvim.command('setlocal modifiable')

        for line in tweets.split('\n')[::-1]:
            self.nvim.current.buffer.append(line, 0)

        self.nvim.current.window.cursor = (1, 1)
        self.nvim.command('setlocal nomodifiable')

    def selectedTimeline(self):
        win_id = self.nvim.current.window.number
        for name, timeline in self.timeline.items():
            if win_id == timeline.win_id:
                return (name, timeline)
        return (None, None)

    @neovim.command('HomeTimeline')
    def home_timeline(self):
        if 'home' not in self.timeline:
            self.nvim.command("setlocal splitright")
            self.nvim.command("vnew")
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nolist nonumber nomodifiable wrap")
            self.timeline['_home'] = Timeline(self.nvim.current.window.number, home_timeline=True)

        self.prependTweet(self.timeline['_home'].generate(self.nvim.current.window.width))
        self.echo('Open home timeline')

    @neovim.command('MentionsTimeline')
    def mentions_timeline(self):
        if 'mentions' not in self.timeline:
            self.nvim.command("setlocal splitright")
            self.nvim.command("vnew")
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nolist nonumber nomodifiable wrap")
            self.timeline['_mentions'] = Timeline(self.nvim.current.window.number, mentions_timeline=True)

        self.prependTweet(self.timeline['_mentions'].generate(self.nvim.current.window.width))
        self.echo('Open mentions timeline')

    @neovim.command('Tweet', nargs='+')
    def tweet(self, lines):
        content = ''
        for line in lines:
            content += line + '\n'

        if len(content) > TwitterAPI.MAX_CHARS:
            self.echo('Tweet must be less than {}'.format(TwitterAPI.MAX_CHARS))
            return

        TwitterAPI().tweet(content)
        self.echo('Tweeted')

    @timelineRequired
    @neovim.command('Retweet')
    def retweet(self):
        end = self.nvim.current.window.cursor[0]
        tweet = self.selectedTimeline()[1].retweet(self.nvim.current.window.buffer[:end])

        self.echo('Retweeted: {}'.format(tweet['text']))

    @timelineRequired
    @neovim.command('Like')
    def like(self):
        end = self.nvim.current.window.cursor[0]
        tweet = self.selectedTimeline()[1].like(self.nvim.current.window.buffer[:end])

        self.echo('Liked: {}'.format(tweet['text']))

    @timelineRequired
    @neovim.command('Reply', nargs='+')
    def reply(self, lines):
        content = ''
        for line in lines:
            content += line + '\n'

        if len(content) > TwitterAPI.MAX_CHARS:
            self.echo('Tweet must be less than {}'.format(TwitterAPI.MAX_CHARS))
            return

        end = self.nvim.current.window.cursor[0]
        tweet = self.selectedTimeline()[1].reply(self.nvim.current.window.buffer[:end], content)
        self.echo('Replied: {}'.format(tweet['text']))

    @neovim.command('ShowLists')
    def list(self):
        if len(self.lists) == 0:
            for list in TwitterAPI().lists():
                self.lists[list['name']] = list['id_str']

        self.echo('lists:\n' + '\n'.join([name for name in self.lists.keys()]))

    @neovim.command('Timeline', nargs=1)
    def list_timeline(self, name):
        self.echo(name[0])
        if name[0] not in self.lists:
            self.echo('No such list')
            return

        if name[0] not in self.timeline:
            self.nvim.command("setlocal splitright")
            self.nvim.command("vnew")
            self.nvim.command("setlocal buftype=nofile bufhidden=hide nolist nonumber nomodifiable wrap")
            self.timeline[name[0]] = Timeline(self.nvim.current.window.number, list_id=self.lists[name[0]])

        self.prependTweet(self.timeline[name[0]].generate(self.nvim.current.window.width))
        self.echo('Opened timeline: {}'.format(name[0]))

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        name = self.selectedTimeline()[0]
        if name is None:
            return

        del self.timeline[name]
        self.echo("Closed timeline: {}".format(name))
