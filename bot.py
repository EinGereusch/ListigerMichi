import logging
import sys
from typing import Optional, Callable
import tweepy

from log import logger

logging.basicConfig(level=logging.INFO, format='%(message)s')


class Bot(tweepy.StreamListener):

    class APIConfig:
        def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
            self.access_token = access_token
            self.access_token_secret = access_token_secret

        def configure(self) -> tweepy.API:
            oauth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            oauth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(oauth, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)
            api.verify_credentials()
            return api

    def __init__(self, config_of_observer: APIConfig, user_ids: str, config_for_retweeting: APIConfig = None):
        super().__init__()
        self.observing_api = config_of_observer.configure()
        if config_for_retweeting is None:
            self.retweeting_api = self.observing_api
        else:
            self.retweeting_api = config_for_retweeting.configure()
        self.api = self.observing_api
        self.me = self.api.me()
        self.callback: Optional[Callable[[tweepy.Status, Bot], None]] = None
        self.ids_of_observed_users = user_ids
        self.running_stream = None

    def run(self):
        if self.running_stream is not None:
            return self.running_stream
        self.running_stream = tweepy.Stream(self.observing_api.auth, self)
        if self.ids_of_observed_users is not None:
            self.running_stream.filter(follow=self.ids_of_observed_users)
        return self.running_stream

    def on_connect(self):
        logger.info("Running.")

    def on_status(self, status):
        if status is None or \
                status.user is None or \
                status.user.id is None or \
                str(status.user.id) not in (self.ids_of_observed_users or []):
            logger.info(f"Skipped {status}")
            return
        if self.callback is not None:
            self.callback(status, self)

    def on_error(self, status_code):
        logger.error(f"Error with code {status_code} occurred.")
        if status_code != 420:
            sys.exit(-1)
        return True
