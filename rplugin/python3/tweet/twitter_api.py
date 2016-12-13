# -*- coding: utf-8 -*-

import os
import json
import neovim

from requests_oauthlib import OAuth1Session


class TwitterAPI:
    _api_base = 'https://api.twitter.com/1.1/'
    _stream_base = 'https://userstream.twitter.com/1.1/'

    def __init__(self, keys):
        self.twitter = OAuth1Session(
                keys['CONSUMER'],
                keys['CONSUMER_SECRET'],
                keys['ACCESS_TOKEN'],
                keys['ACCESS_TOKEN_SECRET'])

    def tweet(self, content):
        url = self._api_base + 'statuses/update.json'
        params = {'status': content}

        r = self.twitter.post(url, params=params)

    def timeline(self, since_id=None):
        if since_id is not None:
            url = self._api_base + 'statuses/home_timeline.json?count=100?since_id={id}'.format(id=since_id)
        else:
            url = self._api_base + 'statuses/home_timeline.json?count=100'

        r = self.twitter.get(url)
        return json.loads(r.text)

    def timeline_stream(self):
        url = self._stream_base + 'user.json'

        conn = self.twitter.get(url, stream=True)

        return conn

