import logging
import os
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.other_page import OtherPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_toolbox():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        driver = create_driver(date_driver.driver_path)
        driver.implicitly_wait(3)

        # 初始化登录页面
        page = LoginPage(driver)  # 初始化登录页面
        url = date_driver.url
        print(f"[INFO] 正在导航到 URL: {url}")
        # 尝试访问 URL，捕获连接错误
        for attempt in range(2):
            try:
                page.navigate_to(url)
                break
            except WebDriverException as e:
                capture_screenshot(driver, f"login_fail_{attempt + 1}")
                logging.warning(f"第 {attempt + 1} 次连接失败: {e}")
                driver.refresh()
                sleep(date_driver.URL_RETRY_WAIT)
        else:
            logging.error("连接失败多次，测试中止")
            safe_quit(driver)
            raise RuntimeError("无法连接到登录页面")

        page.login(date_driver.username, date_driver.password, date_driver.planning)
        list_ = ["系统管理", "系统设置", "系统工具箱"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("系统工具箱页用例")
@pytest.mark.run(order=221)
class TestSToolboxPage:

    @allure.story("填写加密内容，加密秘钥，加密成功")
    # @pytest.mark.run(order=1)
    def test_toolbox_encryption(self, login_to_toolbox):
        driver = login_to_toolbox  # WebDriver 实例
        box = OtherPage(driver)  # 用 driver 初始化 OtherPage
        box.click_encryption_decryption(encryption_value="11", key='123')
        sleep(1)
        value = box.get_find_element_xpath('(//div[label[text()="加密后"]])[1]//textarea').get_attribute("value")
        ele = box.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert value == "4Be4+TNva90="
        assert not box.has_fail_message()

    @allure.story("填写解密内容，解密秘钥，解密成功")
    # @pytest.mark.run(order=1)
    def test_toolbox_decryption(self, login_to_toolbox):
        driver = login_to_toolbox  # WebDriver 实例
        box = OtherPage(driver)  # 用 driver 初始化 OtherPage
        box.click_encryption_decryption(decryption_value="4Be4+TNva90=", key='123')
        sleep(1)
        value = box.get_find_element_xpath('(//div[label[text()="解密后"]])[1]//textarea').get_attribute("value")
        ele = box.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert value == "11"
        assert not box.has_fail_message()
