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


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_operation():
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
        list_ = ["系统管理", "系统设置", "操作日志"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("操作日志页用例")
@pytest.mark.run(order=225)
class TestSOperationPage:

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_operation_ref(self, login_to_operation):
        driver = login_to_operation  # WebDriver 实例
        operation = OtherPage(driver)  # 用 driver 初始化 OtherPage
        operation.wait_for_loading_to_disappear()
        operation.select_input_online("刷新")
        operation.click_all_button("刷新")
        operation.wait_for_loading_to_disappear()
        ele = operation.get_find_element_xpath('//div[div[span[text()=" 用户代码"]]]//input').get_attribute('value')
        assert ele == ""
        assert not operation.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_operation_select(self, login_to_operation):
        driver = login_to_operation  # WebDriver 实例
        operation = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = "a"
        operation.click_button('//div[div[span[text()=" 用户代码"]]]//i[@class="vxe-icon-funnel suffixIcon"]')
        operation.hover("包含")
        sleep(1)
        operation.select_input_online(name)
        sleep(1)
        eles = operation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not operation.has_fail_message()