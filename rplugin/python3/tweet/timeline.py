# -*- coding: utf-8 -*-

import re
from .twitter_api import TwitterAPI

class Timeline:
    def __init__(self, win_id, home_timeline=False, list_id=None):
        self.win_id = win_id

        self._home_timeline = home_timeline
        self._list_id = list_id
        self._api = TwitterAPI()
        self._tweets = []
        self._since_id = None

        self._separater = re.compile('^-*$')

    def _fetch(self):
        if self._home_timeline:
            tweets = self._api.timeline(self._since_id, home_timeline=True)
        else:
            tweets = self._api.timeline(self._since_id, list_id=self._list_id)

        if len(tweets) == 0:
            return

        self._since_id = tweets[0]['id_str']
        self._tweets = tweets + self._tweets

    def _selectedTweet(self, buf):
        cnt = 0
        for line in buf:
            if self._separater.match(line) and line:
                cnt += 1

        return self._tweets[cnt]


    def generate(self, width):
        self._fetch()

        content = ''
        for tweet in self._tweets:
            if 'user' not in 'text' not in tweet:
                continue

            text = tweet['text'].replace('\n', '\n  ')
            text.rstrip()

            content += '{name} @{id}\n\n  {tweet}\n'.format(
                    name=tweet['user']['name'],
                    id=tweet['user']['screen_name'],
                    tweet=text,
                    created_at=tweet['created_at'])

            content += "-" * width + "\n"

        return content

    @property
    def tweets(self):
        return self._tweets

    def retweet(self, buf):
        tweet = self._selectedTweet(buf)
        id = tweet['id_str']
        self._api.retweet(id)

        return tweet

    def like(self, buf):
        tweet = self._selectedTweet(buf)
        id = tweet['id_str']
        self._api.like(id)

        return tweet

    def reply(self, buf, content):
        tweet = self._selectedTweet(buf)
        self._api.reply('@{name} {content}'.format(name=tweet['user']['screen_name'], content=content), tweet['id_str'])

        return tweet
