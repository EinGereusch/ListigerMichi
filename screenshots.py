import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# noinspection PyBroadException
from log import logger


def make_screenshot(path_of_chromedriver: str, chrome_path: str, of_url: str, at_path: str, use_headless_mode: bool,
                    window_size: str):
    try:
        logger.info(f"Attempt to take a screenshot of {of_url}: "
                    f"\n\tUsing webdriver {path_of_chromedriver}"
                    f"\n\tUsing chrome/chromium at {chrome_path}")
        chrome_options = Options()
        chrome_options.add_argument("--window-size=%s" % window_size)
        chrome_options.add_argument("--remote-debugging-port=9222")  # this
        if use_headless_mode:
            chrome_options.add_argument("--headless")

        chrome_options.binary_location = chrome_path
        if not of_url.startswith('http'):
            raise Exception('URLs need to start with "http"')

        driver = webdriver.Chrome(
            executable_path=path_of_chromedriver,
            chrome_options=chrome_options
        )
        driver.get(of_url)
        time.sleep(5)
        driver.save_screenshot(at_path)
        driver.close()
    except Exception as e:
        logger.error(f"Exception of type {type(e)} occurred on an attempt to take a screenshot: {str(e)}")
        pass
