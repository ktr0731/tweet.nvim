# -*- coding: utf-8 -*-

import os
import json

from requests_oauthlib import OAuth1Session


class TwitterAPI:
    _api_base = 'https://api.twitter.com/1.1/'
    _stream_base = 'https://stream.twitter.com/1.1/'

    def __init__(self, keys):
        self.twitter = OAuth1Session(
                keys['CONSUMER'],
                keys['CONSUMER_SECRET'],
                keys['ACCESS_TOKEN'],
                keys['ACCESS_TOKEN_SECRET'])

        url = self._api_base + 'friends/ids.json' + '?screen_name=ktr_0731'
        r = self.twitter.get(url)

        self.friends = [str(e) for e in (r.json())['ids']]

    def tweet(self, content):
        url = self._api_base + 'statuses/update.json'
        params = {'status': content}

        r = self.twitter.post(url, params=params)

    def timeline_stream(self, stop_event, writer):
        url = self._stream_base + 'statuses/filter.json'

        params = {'follow': ','.join(self.friends)}
        r = self.twitter.post(url, params=params, stream=True)

        for line in r.iter_lines():
            if stop_event.is_set():
                break

            if line:
                decoded_line = line.decode('utf-8')
                t = json.loads(decoded_line)

                # 取りこぼしツイート
                if t['user'] is None or t['user']['name'] is None or t['text'] is None:
                    continue

                writer("{name}: {tweet}\n\n----------\n".format(name=t['user']['name'], tweet=t['text']))
                # return "{name}: {tweet}\n\n----------\n".format(name=t['user']['name'], tweet=t['text'])
