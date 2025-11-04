import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class DateDriver:
    url = "http://wkawka.vicp.net:27890"  # http://wkawka.vicp.net:27890  http://localhost:3000/#/auth/login
    driver_path = 'D:/Python310/chromedriver.exe'
    username = 'hongaoqing'  # hongaoqing admin
    password = 'Qw123456'  # Qw123456 1234@Sys
    planning = '金属（演示）'
    URL_RETRY_WAIT = int(os.getenv("URL_RETRY_WAIT", 60))