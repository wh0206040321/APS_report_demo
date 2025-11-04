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
from Pages.systemPage.expression_page import ExpressionPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_dictionary():
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
        list_ = ["系统管理", "系统设置", "字典"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("字典页用例")
@pytest.mark.run(order=219)
class TestSDictionaryPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_dictionary_addfail1(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 dictionary
        sleep(1)
        dictionary.click_all_button("新增")
        sleep(1)
        dictionary.click_confirm()
        message = dictionary.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not dictionary.has_fail_message()

    @allure.story("新增只填写枚举值点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_dictionary_addfail2(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = '1字典1'
        xpath_list = [
            '//div[@id="240ciohl-584b"]//input',
            '//div[@id="wsgjozwj-57r6"]//input',
            '//div[@id="0tj1refm-xmig"]//input',
        ]
        dictionary.click_all_button("新增")
        add.batch_modify_input(xpath_list[:1], name)
        dictionary.click_confirm()
        message = dictionary.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not dictionary.has_fail_message()

    @allure.story("添加字典成功")
    # @pytest.mark.run(order=1)
    def test_dictionary_addsuccess1(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        sleep(1)
        name = '1字典1'
        xpath_list = [
            '//div[@id="240ciohl-584b"]//input',
            '//div[@id="wsgjozwj-57r6"]//input',
            '//div[@id="0tj1refm-xmig"]//input',
        ]
        dictionary.click_all_button("新增")
        add.batch_modify_input(xpath_list, name)
        dictionary.click_confirm()
        message = dictionary.get_find_message()
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
        dictionary.select_input_dictionary(name)
        ele = dictionary.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert ele == name
        assert message == "保存成功"
        assert not dictionary.has_fail_message()

    @allure.story("添加同一个分类枚举值，枚举值不同，添加成功")
    # @pytest.mark.run(order=1)
    def test_dictionary_addsuccess2(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        sleep(1)
        name = '1字典2'
        xpath_list = [
            '//div[@id="240ciohl-584b"]//input',
            '//div[@id="wsgjozwj-57r6"]//input',
            '//div[@id="0tj1refm-xmig"]//input',
        ]
        dictionary.click_all_button("新增")
        add.batch_modify_input(xpath_list[:2], name)
        add.enter_texts(xpath_list[2], '1字典1')
        dictionary.click_confirm()
        message = dictionary.get_find_message()
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="1字典1"])[1]')
        eles = dictionary.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[2]')
        ele = dictionary.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{name}"]').text
        assert len(eles) == 2
        assert ele == name
        assert message == "保存成功"
        assert not dictionary.has_fail_message()

    @allure.story("不允许添加重复枚举值和名称")
    # @pytest.mark.run(order=1)
    def test_dictionary_addrepeat(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        sleep(1)
        name = '1字典1'
        xpath_list = [
            '//div[@id="240ciohl-584b"]//input',
            '//div[@id="wsgjozwj-57r6"]//input',
            '//div[@id="0tj1refm-xmig"]//input',
        ]
        dictionary.click_all_button("新增")
        add.batch_modify_input(xpath_list, name)
        dictionary.click_confirm()
        message = dictionary.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').text
        assert message == "记录已存在,请检查！"
        assert not dictionary.has_fail_message()

    @allure.story("编辑枚举值成功")
    # @pytest.mark.run(order=1)
    def test_dictionary_editsuccess1(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1字典1'
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
        dictionary.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        dictionary.click_all_button("编辑")
        dictionary.enter_texts('//div[@id="l1ysu7kj-7dnz"]//input', '1字典3')
        dictionary.click_confirm()
        message = dictionary.get_find_message()
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
        ele = dictionary.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="1字典3"]').text
        assert message == "编辑成功！"
        assert ele == '1字典3'
        assert not dictionary.has_fail_message()

    @allure.story("编辑分类，列表会增加")
    # @pytest.mark.run(order=1)
    def test_dictionary_editsuccess2(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1字典3'
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
        dictionary.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        dictionary.click_all_button("编辑")
        dictionary.enter_texts('//div[@id="t5rmb5q4-17fw"]//input', '修改分列')
        dictionary.click_confirm()
        # message = dictionary.get_find_message()
        dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="修改分列"])[1]')
        ele = dictionary.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        # assert message == "编辑成功！"
        assert ele == name
        assert not dictionary.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_dictionary_delete(self, login_to_dictionary):
        driver = login_to_dictionary  # WebDriver 实例
        dictionary = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        list_name = ['1字典1', '修改分列']
        for name in list_name:
            dictionary.click_button(f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
            dictionary.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]')
            dictionary.click_all_button("删除")
            dictionary.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            message = dictionary.get_find_message()
            assert message == "删除成功！"
        for name in list_name:
            eles = dictionary.finds_elements(By.XPATH, f'(//div[@id="o6c3f11v-czxj"]//span[text()="{name}"])[1]')
            assert len(eles) == 0
        assert not dictionary.has_fail_message()

