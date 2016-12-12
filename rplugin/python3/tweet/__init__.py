# -*- coding: utf-8 -*-

import os

import neovim

from .api import Api


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
        self.api = Api(keys)

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

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

        # Windowを取得、セットする
        # stop_event = threading.Event()
        # thread = threading.Thread(target=self.api.timeline_stream, args=(e,))
        # thread.start()
        # stop_event.set()
        # TODO: どうやってウインドウが閉じられたかを判断するか
