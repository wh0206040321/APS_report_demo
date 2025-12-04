import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.worktasks_page import WorkTasksPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_worktasks():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        # 初始化 driver
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
        page.click_button('(//span[text()="计划管理"])[1]')  # 点击计划管理
        page.click_button('(//span[text()="计划业务数据"])[1]')  # 点击计划业务数据
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("工作和任务表测试用例")
@pytest.mark.run(order=19)
class TestWorkTasksPage:
    @allure.story("工作明细页面编辑制造数量成功")
    # @pytest.mark.run(order=1)
    def test_workdetails_updateitem(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作明细"])[1]')
        word.wait_for_loading_to_disappear()
        before_value = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[6]').text
        word.click_button('//table[@class="vxe-table--body"]//tr[1]/td[6]')
        word.click_all_button('编辑')
        sleep(1)
        ele = word.get_find_element_xpath('//div[label[text()="制造数量"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        word.enter_texts('//div[label[text()="制造数量"]]//input', '1234')
        word.click_confirm()
        after_value = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[6]').text
        assert after_value == '1234'

        word.click_button('//table[@class="vxe-table--body"]//tr[1]/td[6]')
        word.click_all_button('编辑')
        sleep(1)
        ele = word.get_find_element_xpath('//div[label[text()="制造数量"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        word.enter_texts('//div[label[text()="制造数量"]]//input', before_value)
        word.click_confirm()
        after_value = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[6]').text
        assert after_value == before_value
        assert not word.has_fail_message()

    @allure.story("工作明细页面查询工作代码成功")
    # @pytest.mark.run(order=1)
    def test_workdetails_select1(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[2]').text
        word.select_data(code='工作代码', name=name)
        wordcode = word.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        wordcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert wordcode == name and len(wordcode2) == 0
        assert not word.has_fail_message()

    @allure.story("工作明细页面过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_workdetails_select2(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = "1"
        word.click_button('//div[p[text()="制造数量"]]/following-sibling::div//i')
        word.hover("包含")
        sleep(1)
        word.enter_texts('//div[p[text()="制造数量"]]/following-sibling::div//input', name)
        sleep(1)
        eles = word.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[6]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not word.has_fail_message()

    @allure.story("工作明细页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_workdetails_ref(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作明细"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[p[text()="制造数量"]]/following-sibling::div//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[p[text()="制造数量"]]/following-sibling::div//input').get_attribute('value')
        assert ele == ""
        assert not word.has_fail_message()

    @allure.story("任务明细页面查询工作编号成功")
    # @pytest.mark.run(order=1)
    def test_taskdetails_select1(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        task = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        task.click_button('(//span[text()="任务明细"])[1]')
        task.wait_for_loading_to_disappear()
        name = task.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[6]').text
        task.select_data(code='工作编号', name=name)
        wordcode = task.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[6]'
        ).text
        # 定位第二行没有数据
        wordcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[6]',
        )
        assert wordcode == name and len(wordcode2) == 0
        assert not task.has_fail_message()

    @allure.story("任务明细页面过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_taskdetails_select2(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        task = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        task.click_button('(//span[text()="任务明细"])[1]')
        task.wait_for_loading_to_disappear()
        name = "1"
        task.click_button('//div[p[text()="总工时"]]/following-sibling::div//i')
        task.hover("包含")
        sleep(1)
        task.enter_texts('//div[p[text()="总工时"]]/following-sibling::div//input', name)
        sleep(1)
        eles = task.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[6]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not task.has_fail_message()

    @allure.story("任务明细页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_taskdetails_ref(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="任务明细"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[p[text()="代码"]]/following-sibling::div//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[p[text()="代码"]]/following-sibling::div//input').get_attribute(
            'value')
        assert ele == ""
        assert not word.has_fail_message()

    @allure.story("工作需求明细页面查询订单编号成功")
    # @pytest.mark.run(order=1)
    def test_requirementdetails_select1(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作需求明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[4]').text
        word.select_data(code='订单编号', name=name)
        wordcode = word.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[4]'
        ).text
        # 定位第二行没有数据
        wordcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[4]',
        )
        assert wordcode == name and len(wordcode2) == 0
        assert not word.has_fail_message()

    @allure.story("工作需求明细页面过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_requirementdetails_select2(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作需求明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = "1"
        word.click_button('//div[p[text()="订单编号"]]/following-sibling::div//i')
        word.hover("包含")
        sleep(1)
        word.enter_texts('//div[p[text()="订单编号"]]/following-sibling::div//input', name)
        sleep(1)
        eles = word.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not word.has_fail_message()

    @allure.story("工作需求明细页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_requirementdetails_ref(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作需求明细"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[p[text()="订单编号"]]/following-sibling::div//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[p[text()="订单编号"]]/following-sibling::div//input').get_attribute(
            'value')
        assert ele == ""
        assert not word.has_fail_message()

    @allure.story("工作关联明细页面查询订单编号成功")
    # @pytest.mark.run(order=1)
    def test_relateddetails_select1(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作关联明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = word.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[5]').text
        word.select_data(code='订单(左)', name=name)
        eles = word.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        assert len(eles) > 0
        assert all(name == ele for ele in eles)
        assert not word.has_fail_message()

    @allure.story("工作关联明细页面过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_relateddetails_select2(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作关联明细"])[1]')
        word.wait_for_loading_to_disappear()
        name = "1"
        word.click_button('//div[p[text()="订单(左)"]]/following-sibling::div//i')
        word.hover("包含")
        sleep(1)
        word.enter_texts('//div[p[text()="订单(左)"]]/following-sibling::div//input', name)
        sleep(1)
        eles = word.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not word.has_fail_message()

    @allure.story("工作关联明细页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_relateddetails_ref(self, login_to_worktasks):
        driver = login_to_worktasks  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="工作关联明细"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[p[text()="订单(左)"]]/following-sibling::div//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[p[text()="订单(左)"]]/following-sibling::div//input').get_attribute(
            'value')
        assert ele == ""
        assert not word.has_fail_message()