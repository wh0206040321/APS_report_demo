import logging
import os
from datetime import datetime
from time import sleep
from datetime import date
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
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.other_page import OtherPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_interfaceconfiguration():
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
        list_ = ["数据接口底座", "WebAPI", "接口配置分发"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("接口配置分发页用例")
@pytest.mark.run(order=228)
class TestSInterfaceConfigurationPage:

    @allure.story("不填写数据点击新增不允许保存")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_addfail1(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.click_all_button("新增")
        interface.click_confirm()
        message = interface.get_error_message()
        assert message == "请填写数据"
        assert not interface.has_fail_message()

    @allure.story("只填写源系统和目的系统点击新增不允许保存")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_addfail2(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="源系统:"]]//input[@type="text"]',
            '(//li[text()="SRM"])[1]',
            '//div[label[text()="目的系统:"]]//input[@type="text"]',
            '(//li[text()="APS"])[2]'
        ]
        for xpath in xpath_list:
            interfaceconfiguration.click_button(xpath)
        interfaceconfiguration.click_confirm()
        message = interfaceconfiguration.get_error_message()
        assert message == "请填写数据"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_addsuccess1(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '11测试全部数据'
        interfaceconfiguration.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="访问地址:"]]//input[@type="text"]',
            '//div[label[text()="顺序号:"]]//input'
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[1]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[2]'},
            {"select": '//div[label[text()="服务方式:"]]//input[@type="text"]', "value": '//li[text()="WebApi"]'},
            {"select": '//div[label[text()="授权计划单元:"]]//input[@type="text"]', "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)
        interfaceconfiguration.click_button('//div[label[text()="授权计划单元:"]]//input[@type="text"]')
        select_list = [{"select": '//div[label[text()="接口环境:"]]//span', "value": f'(//li[text()="测试"])[2]'}]
        adds.batch_modify_select_input(select_list)

        interfaceconfiguration.click_confirm()
        message = interfaceconfiguration.get_find_message()
        driver.refresh()
        interfaceconfiguration.wait_for_loading_to_disappear()
        sleep(1)

        text = interfaceconfiguration.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{input_value}"]').text
        assert text == input_value
        assert message == "新增成功！"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("添加重复接口名称不允许添加")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_addrepeat(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '11测试全部数据'
        interfaceconfiguration.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="访问地址:"]]//input[@type="text"]',
            '//div[label[text()="顺序号:"]]//input'
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[1]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[2]'},
            {"select": '//div[label[text()="服务方式:"]]//input[@type="text"]', "value": '//li[text()="WebApi"]'},
            {"select": '//div[label[text()="授权计划单元:"]]//input[@type="text"]',
             "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)
        interfaceconfiguration.click_button('//div[label[text()="授权计划单元:"]]//input[@type="text"]')
        select_list = [{"select": '//div[label[text()="接口环境:"]]//span', "value": f'(//li[text()="测试"])[2]'}]
        adds.batch_modify_select_input(select_list)

        interfaceconfiguration.click_confirm()
        message = interfaceconfiguration.get_error_message()
        assert message == "接口名称不能重复"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_addsuccess2(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '测试数据22'
        interfaceconfiguration.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="访问地址:"]]//input[@type="text"]',
            '//div[label[text()="顺序号:"]]//input'
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[1]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[2]'},
            {"select": '//div[label[text()="服务方式:"]]//input[@type="text"]', "value": '//li[text()="WebApi"]'},
            {"select": '//div[label[text()="授权计划单元:"]]//input[@type="text"]',
             "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)
        interfaceconfiguration.click_button('//div[label[text()="授权计划单元:"]]//input[@type="text"]')
        select_list = [{"select": '//div[label[text()="接口环境:"]]//span', "value": f'(//li[text()="测试"])[2]'}]
        adds.batch_modify_select_input(select_list)

        interfaceconfiguration.click_confirm()
        message = interfaceconfiguration.get_find_message()
        driver.refresh()
        interfaceconfiguration.wait_for_loading_to_disappear()
        sleep(1)

        text = interfaceconfiguration.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{input_value}"]').text
        assert text == input_value
        assert message == "新增成功！"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("修改访问地址成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_update1(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.click_button('//table[@class="vxe-table--body"]//tr/td[3]//span[text()="测试数据22"]')
        interfaceconfiguration.click_all_button('编辑')
        interfaceconfiguration.enter_texts('//div[label[text()="访问地址:"]]//input[@type="text"]', '访问地址11')
        interfaceconfiguration.click_confirm()
        message = interfaceconfiguration.get_find_message()
        ele = interfaceconfiguration.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr[td[3]//span[text()="测试数据22"]]/td[9]').text
        assert ele == '访问地址11'
        assert message == "编辑成功！"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_select1(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.wait_for_loading_to_disappear()
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        sleep(1)
        eles = interfaceconfiguration.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            interfaceconfiguration.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
        sleep(1)
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//input')
        eles = interfaceconfiguration.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_select2(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.wait_for_loading_to_disappear()
        name = "1测试"
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interfaceconfiguration.hover("包含")
        sleep(1)
        interfaceconfiguration.select_input(name)
        sleep(1)
        eles = interfaceconfiguration.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_select3(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.wait_for_loading_to_disappear()
        name = "1"
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interfaceconfiguration.hover("符合开头")
        sleep(1)
        interfaceconfiguration.select_input(name)
        sleep(1)
        eles = interfaceconfiguration.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_select4(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.wait_for_loading_to_disappear()
        name = "2"
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interfaceconfiguration.hover("符合结尾")
        sleep(1)
        interfaceconfiguration.select_input(name)
        sleep(1)
        eles = interfaceconfiguration.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_clear(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interfaceconfiguration.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interfaceconfiguration.hover("包含")
        sleep(1)
        interfaceconfiguration.select_input(name)
        sleep(1)
        interfaceconfiguration.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interfaceconfiguration.hover("清除所有筛选条件")
        sleep(1)
        ele = interfaceconfiguration.get_find_element_xpath('//div[p[text()="接口名称"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not interfaceconfiguration.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_interfaceconfiguration_del(self, login_to_interfaceconfiguration):
        driver = login_to_interfaceconfiguration  # WebDriver 实例
        interfaceconfiguration = ImpPage(driver)  # 用 driver 初始化 ImpPage
        list_ = ['测试数据22', '11测试全部数据']
        for name in list_:
            interfaceconfiguration.click_button(f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{name}"]')
            interfaceconfiguration.click_all_button('删除')
            interfaceconfiguration.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            message = interfaceconfiguration.get_find_message()
            ele = interfaceconfiguration.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{name}"]')
            assert len(ele) == 0
            assert message == "删除成功！"
        assert not interfaceconfiguration.has_fail_message()