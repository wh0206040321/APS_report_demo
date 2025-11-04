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
def login_to_acceptdata():
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
        list_ = ["数据接口底座", "WebAPI", "接收数据"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("接收数据页用例")
@pytest.mark.run(order=227)
class TestSAcceptDataPage:

    @allure.story("不填写数据点击新增不允许保存")
    # @pytest.mark.run(order=1)
    def test_acceptdata_addfail1(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.click_all_button("新增")
        acceptdata.click_confirm()
        message = acceptdata.get_error_message()
        assert message == "请填写数据"
        assert not acceptdata.has_fail_message()

    @allure.story("只填写源数据和目的系统点击新增不允许保存")
    # @pytest.mark.run(order=1)
    def test_acceptdata_addfail2(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="源系统:"]]//input[@type="text"]',
            '(//li[text()="SRM"])[2]',
            '//div[label[text()="目的系统:"]]//input[@type="text"]',
            '(//li[text()="APS"])[1]'
        ]
        for xpath in xpath_list:
            acceptdata.click_button(xpath)
        acceptdata.click_confirm()
        message = acceptdata.get_error_message()
        assert message == "请填写数据"
        assert not acceptdata.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_addsuccess1(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '11测试全部数据'
        acceptdata.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="中间表名:"]]//input[@type="text"]',
            '//div[label[text()="数据分类标识:"]]//input[@type="text"]',
            '//div[label[text()="接收后执行存储过程名称:"]]//input[@type="text"]',
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[2]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[1]'},
            {"select": '//div[label[text()="数据单元:"]]//input[@type="text"]', "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)

        time_list = [
            '//div[label[text()="有效结束日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[2]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[2]',
            '//div[label[text()="有效开始日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[1]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[1]',
        ]
        for xpath in time_list:
            acceptdata.click_button(xpath)

        acceptdata.click_confirm()
        message = acceptdata.get_find_message()
        driver.refresh()
        acceptdata.wait_for_loading_to_disappear()
        sleep(1)

        text = acceptdata.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{input_value}"]').text
        assert text == input_value
        assert message == "新增成功！"
        assert not acceptdata.has_fail_message()

    @allure.story("添加重复接口名称不允许添加")
    # @pytest.mark.run(order=1)
    def test_acceptdata_addrepeat(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '11测试全部数据'
        acceptdata.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="中间表名:"]]//input[@type="text"]',
            '//div[label[text()="数据分类标识:"]]//input[@type="text"]',
            '//div[label[text()="接收后执行存储过程名称:"]]//input[@type="text"]',
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[2]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[1]'},
            {"select": '//div[label[text()="数据单元:"]]//input[@type="text"]',
             "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)

        time_list = [
            '//div[label[text()="有效结束日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[2]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[2]',
            '//div[label[text()="有效开始日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[1]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[1]',
        ]
        for xpath in time_list:
            acceptdata.click_button(xpath)

        acceptdata.click_confirm()
        message = acceptdata.get_error_message()
        assert message == "接口名称不能重复"
        assert not acceptdata.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_addsuccess2(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        adds = AddsPages(driver)
        plan = DateDriver.planning
        input_value = '测试数据22'
        acceptdata.click_all_button("新增")

        text_list = [
            '//div[label[text()="接口名称:"]]//input[@type="text"]',
            '//div[label[text()="中间表名:"]]//input[@type="text"]',
            '//div[label[text()="数据分类标识:"]]//input[@type="text"]',
            '//div[label[text()="接收后执行存储过程名称:"]]//input[@type="text"]',
        ]
        adds.batch_modify_input(text_list, input_value)

        select_list = [
            {"select": '//div[label[text()="源系统:"]]//input[@type="text"]', "value": '(//li[text()="SRM"])[2]'},
            {"select": '//div[label[text()="目的系统:"]]//input[@type="text"]', "value": '(//li[text()="APS"])[1]'},
            {"select": '//div[label[text()="数据单元:"]]//input[@type="text"]',
             "value": f'(//li[text()="{plan}"])[last()]'},
        ]
        adds.batch_modify_select_input(select_list)

        time_list = [
            '//div[label[text()="有效结束日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[2]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[2]',
            '//div[label[text()="有效开始日期:"]]//input[@type="text"]',
            '(//span[contains(@class,"ivu-date-picker-cells-cell-today")])[1]',
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small" and span[contains(text(),"确定")]])[1]',
        ]
        for xpath in time_list:
            acceptdata.click_button(xpath)

        acceptdata.click_confirm()
        message = acceptdata.get_find_message()
        driver.refresh()
        acceptdata.wait_for_loading_to_disappear()
        sleep(1)

        text = acceptdata.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{input_value}"]').text
        assert text == input_value
        assert message == "新增成功！"
        assert not acceptdata.has_fail_message()

    @allure.story("修改中间表名成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_update1(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.click_button('//table[@class="vxe-table--body"]//tr/td[3]//span[text()="测试数据22"]')
        acceptdata.click_all_button('编辑')
        acceptdata.enter_texts('//div[label[text()="中间表名:"]]//input[@type="text"]', '测试数据22修改')
        acceptdata.click_confirm()
        message = acceptdata.get_find_message()
        ele = acceptdata.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr[td[3]//span[text()="测试数据22"]]/td[4]').text
        assert ele == '测试数据22修改'
        assert message == "编辑成功！"
        assert not acceptdata.has_fail_message()

    @allure.story("点击运行日志点击查询不报错,点击导出不报错")
    # @pytest.mark.run(order=1)
    def test_acceptdata_clickselect(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.click_button('//table[@class="vxe-table--body"]//tr[td[3]//span[text()="测试数据22"]]/td[12]//button')
        acceptdata.click_button('//span[text()="查询"]')
        acceptdata.click_button('//span[text()="导出"]')
        ele = acceptdata.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not acceptdata.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_acceptdata_select1(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.wait_for_loading_to_disappear()
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        sleep(1)
        eles = acceptdata.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            acceptdata.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
        sleep(1)
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//input')
        eles = acceptdata.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not acceptdata.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_select2(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.wait_for_loading_to_disappear()
        name = "1测试"
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        acceptdata.hover("包含")
        sleep(1)
        acceptdata.select_input(name)
        sleep(1)
        eles = acceptdata.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not acceptdata.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_select3(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.wait_for_loading_to_disappear()
        name = "1"
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        acceptdata.hover("符合开头")
        sleep(1)
        acceptdata.select_input(name)
        sleep(1)
        eles = acceptdata.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not acceptdata.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_select4(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.wait_for_loading_to_disappear()
        name = "2"
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        acceptdata.hover("符合结尾")
        sleep(1)
        acceptdata.select_input(name)
        sleep(1)
        eles = acceptdata.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not acceptdata.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_clear(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        acceptdata.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        acceptdata.hover("包含")
        sleep(1)
        acceptdata.select_input(name)
        sleep(1)
        acceptdata.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        acceptdata.hover("清除所有筛选条件")
        sleep(1)
        ele = acceptdata.get_find_element_xpath('//div[p[text()="接口名称"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not acceptdata.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_acceptdata_del(self, login_to_acceptdata):
        driver = login_to_acceptdata  # WebDriver 实例
        acceptdata = ImpPage(driver)  # 用 driver 初始化 ImpPage
        list_ = ['测试数据22', '11测试全部数据']
        for name in list_:
            acceptdata.click_button(f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{name}"]')
            acceptdata.click_all_button('删除')
            acceptdata.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            message = acceptdata.get_find_message()
            ele = acceptdata.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[3]//span[text()="{name}"]')
            assert len(ele) == 0
            assert message == "删除成功！"
        assert not acceptdata.has_fail_message()