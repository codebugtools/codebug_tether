# -*- encoding: utf-8 -*-
"""twitter demo for CodeBug Tether.
Call with no arguments to pull latest tweets from home timeline.
Call with string argument to search for that term
"""
# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import time
import threading
import sys
import os
try:
    import twitter  # http://mike.verdone.ca/twitter/
except ImportError:
    print("You need to install Python Twitter Tools "
          "(http://mike.verdone.ca/twitter/).")
    sys.exit(1)
from codebug_tether import CodeBug


UPDATE_INTERVAL = 60

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
# CONSUMER_KEY = ""
# CONSUMER_SECRET = ""

OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""


class NoTweetsError(Exception):
    pass


class TwitterTicker(object):
    def __init__(self, codebug, oauth_token, oauth_secret, search_term=None):
        self.twitter = twitter.Twitter(
            auth=twitter.OAuth(
                oauth_token, oauth_secret,
                CONSUMER_KEY, CONSUMER_SECRET)
        )
        self.search_term = search_term
        self.codebug = codebug
        try:
            self.current_tweet = self.get_latest_tweet()
        except NoTweetsError:
            self.current_tweet = None
        self.display_tweet(self.current_tweet)
        self.timer = None

    # @property
    # def page(self):
    #     return self._current_page

    # @page.setter
    # def page(self, new_page):
    #     num_pages = 1 + int(len(self.current_tweet['text']) / PAGE_WIDTH)
    #     new_page %= num_pages
    #     self.display_tweet(self.current_tweet, new_page)

    def get_latest_tweet(self):
        if self.search_term is None:
            return self.twitter.statuses.home_timeline()[0]

        try:
            latest_tweets = self.twitter.search.tweets(
                q=self.search_term,
                since_id=self.current_tweet['id'])['statuses']
        except AttributeError:
            latest_tweets = self.twitter.search.tweets(
                q=self.search_term)['statuses']

        try:
            return latest_tweets[0]
        except IndexError:
            raise NoTweetsError()

    def update(self, event=None):
        """Updated the screen with the latest tweet."""
        print("Updating...")
        try:
            latest_tweet = self.get_latest_tweet()
        except NoTweetsError:
            return
        else:
            if self.current_tweet is None or \
                    latest_tweet['id'] != self.current_tweet['id']:
                self.current_tweet = latest_tweet
                self.display_tweet(self.current_tweet)

    def auto_update(self):
        self.update()
        # update again soon
        self.timer = threading.Timer(UPDATE_INTERVAL, self.auto_update)
        self.timer.start()

    def display_tweet(self, tweet, page=0):
        self._current_page = page
        text = tweet['text']
        print("DISPLAYING TWEET", text)
        self.codebug.clear()
        delay = 0.05
        for i in range(len(text) * 5 + 5):
            self.codebug.write_text(5 - i, 0, text)
            time.sleep(delay)

    def close(self):
        if self.timer is not None:
            self.timer.cancel()
        self.cad.lcd.clear()
        self.cad.lcd.backlight_off()

    def next_page(self, event=None):
        self.page += 1

    def previous_page(self, event=None):
        self.page -= 1


if __name__ == "__main__":
    try:
        search_term = sys.argv[1]
    except IndexError:
        search_term = None
        print("Using home timeline.")
    else:
        print("Searching for", search_term)

    twitter_creds = os.path.expanduser('~/.twitter_piface_demo_credentials')
    if not os.path.exists(twitter_creds):
        twitter.oauth_dance("CodeBug Tether Twitter",
                            CONSUMER_KEY,
                            CONSUMER_SECRET,
                            twitter_creds)

    oauth_token, oauth_secret = twitter.read_token_file(twitter_creds)

    codebug = CodeBug()

    global twitterticker
    twitterticker = TwitterTicker(codebug,
                                  oauth_token,
                                  oauth_secret,
                                  search_term)
    twitterticker.auto_update()  # start the updating process
