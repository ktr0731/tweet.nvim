# -*- coding: utf-8 -*-

import os
import json
import neovim

from requests_oauthlib import OAuth1Session
from requests import exceptions

class TwitterAPI:
    MAX_CHARS = 140

    _api_base = 'https://api.twitter.com/1.1/'
    stream_base = 'https://userstream.twitter.com/1.1/'

    def __init__(self):
        keys = {
                'CONSUMER': '',
                'CONSUMER_SECRET': '',
                'ACCESS_TOKEN': '',
                'ACCESS_TOKEN_SECRET': ''
                }

        for key in keys.keys():
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
        url = self._api_base + 'statuses/update.json'
        params = {'status': content}

        self.twitter.post(url, params=params)

    def retweet(self, id):
        url = self._api_base + 'statuses/retweet/{}.json'.format(id)

        self.twitter.post(url)

    def like(self, id):
        url = self._api_base + 'favorites/create.json?id={}'.format(id)

        self.twitter.post(url)

    def reply(self, content, id):
        url = self._api_base + 'statuses/update.json?in_reply_to_status_id={}'.format(id)
        params = {'status': content}

        self.twitter.post(url, params=params)

    def timeline(self, since_id=None, home_timeline=False, mentions_timeline=False, list_id=None):
        if home_timeline:
            url = self._api_base + 'statuses/home_timeline.json?count=100'
        elif mentions_timeline:
            url = self._api_base + 'statuses/mentions_timeline.json?count=100'
        else:
            url = self._api_base + 'lists/statuses.json?count=100&list_id={}'.format(list_id)

        if since_id is not None:
            url += '&since_id={}'.format(since_id)

        r = self.twitter.get(url)
        return json.loads(r.text)

    def lists(self):
        url = self._api_base + 'lists/list.json'

        r = self.twitter.get(url)

        return json.loads(r.text)

    def timeline_stream(self):
        url = self._stream_base + 'user.json'

        conn = self.twitter.get(url, stream=True)

        return conn
