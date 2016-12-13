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

    def echo(self, message):
        self.nvim.command("echo '[Tweet.nvim] {}'".format(message))

    # def prependTweet(self, tweet):
    #     self.nvim.command("echo '[Tweet.nvim] {}'".format(tweet))
        # self.nvim.command("setlocal modifiable")
        # self.nvim.current.buffer.append(tweet, 0)
        # self.nvim.command("setlocal nomodifiable")

    def timeline(self, conn, stop_event):
        first = True
        for line in conn.iter_lines():
            if stop_event.is_set():
                break

            if first:
                first = False
                continue

            if line:
                decoded_line = line.decode('utf-8')
                t = json.loads(decoded_line)

                # 取りこぼしツイート
                if 'user' not in t or 'name' not in t['user'] or 'text' not in t:
                    continue

                # うごかない
                neovim.async_call(neovim.command, "echo '{name}: {tweet}\n\n----------\n'".format(name=t['user']['name'], tweet=t['text']))
                # self.echo('{name}: {tweet}\n\n----------\n'.format(name=t['user']['name'], tweet=t['text']))
                # print("{name}: {tweet}\n\n----------\n".format(name=t['user']['name'], tweet=t['text']))

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
    def create_stream(self):
        self.nvim.command("setlocal splitright")
        self.nvim.command("vnew")
        self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")

        win_id = self.nvim.command_output('echo win_getid()').strip()

        self.echo('Buf: {name} opened'.format(name=win_id))

        stop_event = threading.Event()
        self.streams[win_id] = stop_event

        # thread = threading.Thread(target=self.api.timeline_stream, args=(stop_event))
        thread = threading.Thread(target=self.timeline, args=(self.api.timeline_stream(), stop_event))
        thread.start()

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if len(self.streams) == 0:
            return

        win_id = self.nvim.command_output('echo win_getid()').strip()

        self.echo('Buf: {name} closed'.format(name=win_id))

        if self.streams[win_id] is not None:
            self.streams[win_id].set()
