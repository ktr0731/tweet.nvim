# -*- coding: utf-8 -*-

import os
import threading

import neovim

from .twitter_api import TwitterAPI


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

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    def prependTweet(self, tweet):
        self.nvim.command("setlocal modifiable")
        self.nvim.current.buffer.append([tweet])
        self.nvim.command("setlocal nomodifiable")

    @neovim.command('Tweet', nargs='*', sync=True)
    def tweet(self, lines):
        if len(lines) == 0:
            self.echo('Usage: Tweet [line...]')

        content = ''
        for line in lines:
            content += line + '\n'

        self.api.tweet(content)

        self.echo('Tweeted')

    @neovim.command('TwitterTimeline')
    def timeline(self):
        self.nvim.command("setlocal splitright")
        self.nvim.command("vnew")
        self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")

        self.prependTweet("hoge")
        win_id = self.nvim.command_output('echo win_getid()')
        stop_event = threading.Event()
        self.echo('Buf: {name} opened'.format(name=win_id))
        self.streams[win_id] = stop_event

        thread = threading.Thread(target=self.api.timeline_stream, args=(stop_event, self.prependTweet))
        thread.start()

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_stream(self):
        if len(self.streams) == 0:
            return

        win_id = self.nvim.command_output('echo win_getid()')
        self.echo('Buf: {name} closed'.format(name=win_id))
        if self.streams[win_id] is not None:
            self.streams[win_id].set()
