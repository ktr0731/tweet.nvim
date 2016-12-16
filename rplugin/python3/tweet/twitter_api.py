# -*- coding: utf-8 -*-

import os
import json
import neovim

from requests_oauthlib import OAuth1Session


class TwitterAPI:
    api_base = 'https://api.twitter.com/1.1/'
    stream_base = 'https://userstream.twitter.com/1.1/'

    def __init__(self):
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

    def tweet(self, content):
        url = self.api_base + 'statuses/update.json'
        params = {'status': content}

        self.twitter.post(url, params=params)

    def retweet(self, id):
        url = self.api_base + 'statuses/retweet/{}.json'.format(id)

        self.twitter.post(url)

    def like(self, id):
        url = self.api_base + 'favorites/create.json'
        params = {'id': id}

        self.twitter.post(url, params=params)

    def timeline(self, since_id=None):
        url = self.api_base + 'statuses/home_timeline.json?count=100'

        if since_id is not None:
            url += '&since_id={id}'.format(id=since_id)

        r = self.twitter.get(url)
        return json.loads(r.text)

    def timeline_stream(self):
        url = self._stream_base + 'user.json'

        conn = self.twitter.get(url, stream=True)

        return conn
