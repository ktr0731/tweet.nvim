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
        for line in tweets.split('\n'):
            self.nvim.current.buffer.append(line)
        self.nvim.command('setlocal nomodifiable')

    # def timeline_stream(self, conn, stop_event):
    #     first = True
    #     for line in conn.iter_lines():
    #         if stop_event.is_set():
    #             break
    #
    #         if first:
    #             first = False
    #             continue
    #
    #         if line:
    #             decoded_line = line.decode('utf-8')
    #             t = json.loads(decoded_line)
    #
    #             # 取りこぼしツイート
    #             if 'user' not in t or 'name' not in t['user'] or 'text' not in t:
    #                 continue
    #
    #             # うごかない
    #             # neovim.async_call(neovim.command, "echo '{name}: {tweet}\n\n----------\n'".format(name=t['user']['name'], tweet=t['text']))
    #             self.echo('{name}: {tweet}\n\n----------\n'.format(name=t['user']['name'], tweet=t['text']))

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

        self.echo(len(tweets))

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

        self.echo(tweets)
        self.home_timeline['since_id'] = tweets[-1]['id_str']

        if 'window_id' not in self.home_timeline:
            self.home_timeline['window_id'] = self.nvim.command_output('echo win_getid()').strip()

        self.prependTweet(content)

    @neovim.command('TimelineStream')
    def create_stream(self):
        self.echo("Sorry. Timeline streaming is not yet implemented...")
        # self.nvim.command("setlocal splitright")
        # self.nvim.command("vnew")
        # self.nvim.command("setlocal buftype=nofile bufhidden=hide nowrap nolist nonumber nomodifiable")
        #
        # win_id = self.nvim.command_output('echo win_getid()').strip()
        #
        # self.echo('Buf: {name} opened'.format(name=win_id))
        #
        # stop_event = threading.Event()
        # self.streams[win_id] = stop_event

        # thread = threading.Thread(target=self.api.timeline_stream, args=(stop_event))
        # thread = threading.Thread(target=self.timeline_stream(), args=(self.api.timeline_stream(), stop_event))
        # thread.start()

    @neovim.autocmd('BufWinLeave', sync=True)
    def close_timeline(self):
        if self.home_timeline['opened']:
            self.echo("Close timeline")
            self.home_timeline['opened'] = False
            del self.home_timeline['since_id']
            del self.home_timeline['window_id']

    def close_timeline_stream(self):
        if len(self.streams) == 0:
            return

        win_id = self.nvim.command_output('echo win_getid()').strip()

        self.echo('Buf: {name} closed'.format(name=win_id))

        if self.streams[win_id] is not None:
            self.streams[win_id].set()
