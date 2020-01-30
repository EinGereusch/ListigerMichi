from __future__ import unicode_literals

from log import logger

import os
import sys
import traceback

import argparse
import tweepy

from bot import Bot
from screenshots import make_screenshot

IDS_OF_OBSERVED_USER = []
SCREENSHOTS_FOLDER = None
CHROME_PATH = ''
CHROMEDRIVER_PATH = ''
USE_HEADLESS_MODE = True
SCREENSHOT_WINDOW_SIZE = "640x480"
USE_HEADLESS = True


# noinspection PyUnresolvedReferences,PyBroadException
def retweet_an_idiot(inbound_status: tweepy.Status, using_bot: Bot):
    try:
        status = using_bot.observing_api.get_status(inbound_status.id, tweet_mode="extended")
        logger.info("Retweeting " + status.full_text)
        start = status.display_text_range[0]
        end = status.display_text_range[1]
        link_to_original_tweet = "https://twitter.com/" \
                                 + str(inbound_status.author.screen_name) \
                                 + "/statuses/" \
                                 + str(inbound_status.id)
        replying_to_id = inbound_status.in_reply_to_status_id
        in_response_to_tweet = "Antwort an https://twitter.com/" \
                               + str(inbound_status.in_reply_to_screen_name) \
                               + "/statuses/" \
                               + str(replying_to_id) if replying_to_id is not None else None
        path_of_screenshot = SCREENSHOTS_FOLDER + str(inbound_status.id) + ".png"
        make_screenshot(CHROMEDRIVER_PATH, CHROME_PATH, link_to_original_tweet, path_of_screenshot,
                        USE_HEADLESS_MODE, window_size=SCREENSHOT_WINDOW_SIZE)
        retweet = using_bot.retweeting_api

        if os.path.exists(path_of_screenshot):
            outbound_tweet = retweet.update_with_media(path_of_screenshot, status=status.full_text[start:end])
        else:
            outbound_tweet = retweet.update_status(status=status.full_text[start:end])

        outbound_tweet_2 = retweet.update_status(link_to_original_tweet, in_reply_to_status_id=outbound_tweet.id)

        if in_response_to_tweet is not None:
            retweet.update_status(in_response_to_tweet, in_reply_to_status_id=outbound_tweet_2.id)
        if os.path.exists(path_of_screenshot):
            os.remove(path_of_screenshot)
    except:
        logger.error("Exeption occured", exc_info=True)
        traceback.print_exc()
        sys.exit(1)
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-read-consumer-key",
                        type=str,
                        required=True,
                        help="Called 'API Key' on your App's description on twitter.com")
    parser.add_argument("-read-consumer-secret",
                        type=str,
                        required=True,
                        help="Called 'API secret key' on your App's description on twitter.com")
    parser.add_argument("-read-access-token",
                        type=str,
                        required=True)
    parser.add_argument("-read-access-token-secret", 
                        type=str,
                        required=True)
    parser.add_argument("-ids-of-observed-user", help="Comma-separated list of user ids to observe", type=str,
                        default="", required=True)
    parser.add_argument("-chrome-path", help="Path to a Chrome installation", type=str, dest="chrome_path",
                        default="")
    parser.add_argument("-webdriver-path", help="Path to the Selenium Chrome Webdriver", type=str, dest="webdriver_path",
                        default="")
    parser.add_argument("-screenshots-folder", help="Path for temp. screenshots", type=str, dest="screenshots_folder",
                        default=None)
    parser.add_argument("-use-headless", help="Should be 'Yes' for machines without UI", type=str,
                        default="Yes")
    parser.add_argument("-write-consumer-key", type=str, default=None)
    parser.add_argument("-write-consumer-secret", type=str, default=None)
    parser.add_argument("-write-access-token", type=str, default=None)
    parser.add_argument("-write-access-token-secret", type=str, default=None)

    args = parser.parse_args()
    IDS_OF_OBSERVED_USER = args.ids_of_observed_user.split(",")
    CHROME_PATH = args.chrome_path
    CHROMEDRIVER_PATH = args.webdriver_path
    SCREENSHOTS_FOLDER = args.screenshots_folder
    USE_HEADLESS_MODE = args.use_headless == "Yes"

    if CHROMEDRIVER_PATH == "":
        logger.warn("Path to Chrome Webdriver not specidifed; Screenshots won't appear in Retweets.")
    if CHROME_PATH == "":
        logger.warn("Path to Chrome/Chromium not specidifed; Screenshots won't appear in Retweets.")

    if SCREENSHOTS_FOLDER is not None and not os.path.exists(SCREENSHOTS_FOLDER):
        os.makedirs(SCREENSHOTS_FOLDER)

    config_for_observer = Bot.APIConfig(args.read_consumer_key, args.read_consumer_secret,
                                        args.read_access_token, args.read_access_token_secret)
    if args.write_consumer_key is not None and args.write_consumer_secret is not None\
            and args.write_access_token is not None and args.write_access_token_secret:
        config_for_retweets = Bot.APIConfig(args.write_consumer_key, args.write_consumer_secret,
                                            args.write_access_token, args.write_access_token_secret)
    else:
        config_for_retweets = None

    bot = Bot(config_for_observer, config_for_retweeting=config_for_retweets, user_ids=IDS_OF_OBSERVED_USER)
    bot.callback = retweet_an_idiot
    logger.info("Booting.")
    stream = bot.run()

