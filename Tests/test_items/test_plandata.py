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
def login_to_plandata():
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


@allure.feature("计划信息计划评估页测试用例")
@pytest.mark.run(order=20)
class TestPlanDataPage:

    @allure.story("计划消息页面查询信息内容成功")
    # @pytest.mark.run(order=1)
    def test_planningAnnouncement_select1(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="计划消息"])[1]')
        information.wait_for_loading_to_disappear()
        information.select_data(code='消息内容', name='分派结果')
        eles = information.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        sleep(1)
        assert all('分派结果' == text for text in eles)
        assert not information.has_fail_message()

    @allure.story("计划消息页面过滤条件查询成功")
    # @pytest.mark.run(order=1)
    def test_planningAnnouncement_select2(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="计划消息"])[1]')
        information.wait_for_loading_to_disappear()
        name = "分派"
        information.click_button('//div[div[span[text()=" 消息内容"]]]//i[@class="vxe-icon-funnel suffixIcon"]')
        information.hover("符合开头")
        sleep(1)
        information.enter_texts('//div[div[span[text()=" 消息内容"]]]//input', name)
        sleep(1)
        eles = information.loop_judgment('//table[@class="vxe-table--body"]//tr//td[3]')
        assert all(str(item).startswith(name) for item in eles)
        assert not information.has_fail_message()

    @allure.story("计划消息页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_planningAnnouncement_ref(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="计划消息"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[div[span[text()=" 消息内容"]]]//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[div[span[text()=" 消息内容"]]]//input').get_attribute('value')
        assert ele == ""
        assert not word.has_fail_message()

    @allure.story("计划评估页面过滤查询成功")
    # @pytest.mark.run(order=1)
    def test_planEvaluation_select1(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="计划评估"])[1]')
        information.wait_for_loading_to_disappear()
        name = "1"
        information.click_button('//div[div[span[text()=" 制造订单数"]]]//i[@class="vxe-icon-funnel suffixIcon"]')
        information.hover("包含")
        sleep(1)
        information.enter_texts('//div[div[span[text()=" 制造订单数"]]]//input', name)
        sleep(1)
        eles = information.loop_judgment('//table[@class="vxe-table--body"]//tr//td[5]')
        assert all(name in text for text in eles)
        assert not information.has_fail_message()

    @allure.story("计划评估页面删除成功")
    # @pytest.mark.run(order=1)
    def test_planEvaluation_del(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="计划评估"])[1]')
        word.wait_for_loading_to_disappear()
        # 定位第一行
        word.click_button(
            '//table[@class="vxe-table--body"]//tr[1]//td[3]'
        )
        before_data = word.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        word.click_all_button("删除")  # 点击删除
        word.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        sleep(1)
        after_data = word.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not word.has_fail_message()

    @allure.story("计划评估页面刷新成功")
    # @pytest.mark.run(order=1)
    def test_planEvaluation_ref(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        word = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        word.click_button('(//span[text()="计划评估"])[1]')
        word.wait_for_loading_to_disappear()
        word.enter_texts('//div[div[span[text()=" 代码"]]]//input', '1')
        word.click_all_button("刷新")
        word.wait_for_loading_to_disappear()
        ele = word.get_find_element_xpath('//div[div[span[text()=" 代码"]]]//input').get_attribute('value')
        assert ele == ""
        assert not word.has_fail_message()

    @allure.story("日计划报表页面资源代码查询成功")
    # @pytest.mark.run(order=1)
    def test_dailyPlan_select1(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="日计划报表"])[1]')
        information.wait_for_loading_el_skeleton()
        information.click_button('//div[@id="1hfwxqtn-j5mr"]//input')
        information.click_button('(//div[@class="my-list vxe-list"])[3]//span[1]')
        information.click_button('//div[@id="4whnlvxq-9gwo"]/button')
        sleep(3)
        name = information.get_find_element_xpath('//div[@id="1hfwxqtn-j5mr"]//span[@class="el-select__tags-text"]').text
        eles = driver.find_elements(By.XPATH,
                                    '(//table[@class="vxe-table--body"])[1]//tr[position() < last()]/td[2]')

        values = [e.get_attribute("textContent").strip() for e in eles]
        assert all(v == name for v in values)
        assert not information.has_fail_message()

    @allure.story("日计划报表页面物料代码查询成功")
    # @pytest.mark.run(order=1)
    def test_dailyPlan_select2(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="日计划报表"])[1]')
        information.wait_for_loading_el_skeleton()
        information.click_button('//div[@id="7aqg845h-0cy0"]//input')
        information.click_button('(//div[@class="my-list vxe-list"])[3]//span[1]')
        information.click_button('//div[@id="4whnlvxq-9gwo"]/button')
        sleep(3)
        name = information.get_find_element_xpath(
            '//div[@id="7aqg845h-0cy0"]//span[@class="el-select__tags-text"]').text

        eles = driver.find_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr[position() < last()]/td[4]')
        values = [e.get_attribute("textContent").strip() for e in eles]
        assert all(v == name for v in values)
        assert not information.has_fail_message()

    @allure.story("日计划报表页面订单代码查询成功")
    # @pytest.mark.run(order=1)
    def test_dailyPlan_select3(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="日计划报表"])[1]')
        information.wait_for_loading_el_skeleton()
        information.click_button('//div[@id="1zkjq6u8-nfal"]//input')
        information.click_button('(//div[@class="my-list vxe-list"])[3]//span[1]')
        information.click_button('//div[@id="4whnlvxq-9gwo"]/button')
        sleep(3)
        name = information.get_find_element_xpath(
            '//div[@id="1zkjq6u8-nfal"]//span[@class="el-select__tags-text"]').text

        eles = driver.find_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr[position() < last()]/td[3]')
        values = [e.get_attribute("textContent").strip() for e in eles]
        assert all(v == name for v in values)
        assert not information.has_fail_message()

    @allure.story("日计划报表页面资源代码和物料代码查询成功")
    # @pytest.mark.run(order=1)
    def test_dailyPlan_select4(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="日计划报表"])[1]')
        information.wait_for_loading_el_skeleton()
        information.click_button('//div[@id="1hfwxqtn-j5mr"]//input')
        information.click_button('(//div[@class="my-list vxe-list"])[3]//span[1]')

        information.click_button('//div[@id="7aqg845h-0cy0"]//input')
        information.click_button('(//div[@class="my-list vxe-list"])[3]//span[1]')

        information.click_button('//div[@id="4whnlvxq-9gwo"]/button')
        sleep(3)
        name1 = information.get_find_element_xpath(
            '//div[@id="1hfwxqtn-j5mr"]//span[@class="el-select__tags-text"]').text
        name2 = information.get_find_element_xpath(
            '//div[@id="7aqg845h-0cy0"]//span[@class="el-select__tags-text"]').text

        eles1 = driver.find_elements(By.XPATH,
                                    '(//table[@class="vxe-table--body"])[1]//tr[position() < last()]/td[2]')
        eles2 = driver.find_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr[position() < last()]/td[4]')
        values1 = [e.get_attribute("textContent").strip() for e in eles1]
        values2 = [e.get_attribute("textContent").strip() for e in eles2]
        for v1, v2 in zip(values1, values2):
            assert v1 == name1 and v2 == name2, f"行不匹配: v1={v1}, v2={v2}, 期望=({name1}, {name2})"
        assert not information.has_fail_message()

    @allure.story("日计划报表页面点击按工作按订单成功")
    # @pytest.mark.run(order=1)
    def test_dailyPlan_click(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="日计划报表"])[1]')
        information.wait_for_loading_el_skeleton()
        information.click_button('//div[text()=" 按工作 "]')
        sleep(1)
        ele1 = information.get_find_element_xpath('(//table[@class="vxe-table--header"])[3]//tr/th[2]').text

        information.click_button('//div[text()=" 按订单 "]')
        sleep(1)
        ele2 = information.get_find_element_xpath('(//table[@class="vxe-table--header"])[5]//tr/th[2]').text
        assert ele1 == '工作代码' and ele2 == '订单代码'
        assert not information.has_fail_message()

    @allure.story("计划评估仪表盘打开不报错")
    # @pytest.mark.run(order=1)
    def test_planDial_click(self, login_to_plandata):
        driver = login_to_plandata  # WebDriver 实例
        information = WorkTasksPage(driver)  # 用 driver 初始化 WorkTasksPage
        information.click_button('(//span[text()="计划评估仪表盘"])[1]')
        information.wait_for_loading_to_disappear()
        ele = information.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not information.has_fail_message()