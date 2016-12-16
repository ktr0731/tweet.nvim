# -*- coding: utf-8 -*-

from .twitter_api import TwitterAPI

class Timeline:
    def __init__(self, win_id):
        self.win_id = win_id

        self._api = TwitterAPI()
        self._tweets = []
        self._since_id = None

    def _fetch(self):
        tweets = self._api.timeline(self._since_id)

        if len(tweets) == 0:
            return

        self._since_id = tweets[0]['id_str']
        self._tweets = tweets + self._tweets

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


    @property
    def tweets(self):
        return self._tweets

    def retweet(self, id):
        self._api.retweet(id)
