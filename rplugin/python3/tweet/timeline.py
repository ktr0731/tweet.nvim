# -*- coding: utf-8 -*-

from .twitter_api import TwitterAPI

class Timeline:
    def __init__(self, win_id):
        self.win_id = win_id

        self._api = TwitterAPI()
        self._tweets = []
        self._since_id = None

        self._fetch()

    @property
    def tweets(self):
        self._fetch()
        return self._tweets

    def _fetch(self):
        tweets = self._api.timeline(self._since_id)

        if len(tweets) == 0:
            return

        self._since_id = tweets[0]['id_str']
        self._tweets = tweets + self._tweets
