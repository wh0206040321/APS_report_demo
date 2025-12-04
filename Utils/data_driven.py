import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class DateDriver:

    URL_RETRY_WAIT = int(os.getenv("URL_RETRY_WAIT", 60))