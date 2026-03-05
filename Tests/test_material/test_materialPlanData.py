import logging
import os
import re
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.materialPage.materialPlanData_page import MaterialPlanData
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_materialplandata():
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
        list_ = ["物控管理", "物控业务数据"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物料齐套结果，订单欠料表，物料欠料表，订单分批齐套，物料供应明细，供需分配明细页用例")
@pytest.mark.run(order=146)
class TestSPlanDataPage:

    @allure.story("点击查询订单齐套结果不报错")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询需求来源")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[3]').text
        material.click_button('//div[span[text()="需求来源:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询需求展开方式")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        driver.execute_script("document.body.style.zoom='0.6'")
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[22]').text
        material.click_button('//div[span[text()="需求展开方式:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[22]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询订单列表")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select3(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        driver.execute_script("document.body.style.zoom='1'")
        material.click_button('//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//div[@class="my-list-item"]//span)[last()]')
        material.click_select_button()
        name = material.get_find_element_xpath('//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]').get_attribute("value")
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询产品编码")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select4(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[10]').text
        material.click_button('//div[span[text()="产品编码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[10]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select5(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[5]'
        ).get_attribute('innerText')
        first_char = name[:2] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("包含")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(first_char in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select6(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[5]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合开头")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_select7(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[5]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合结尾")
        sleep(1)
        material.select_input('订单代码', last_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单齐套结果')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("点击齐套明细，齐套追溯成功")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_click1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]//span[text()="齐套明细"]')
        material.click_button('(//button[span[text()="查询"]])[2]')
        sleep(1)
        material.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]//span[text()="齐套追溯"]')
        material.click_button('//div[div[text()="订单齐套结果-齐套明细-齐套追溯"]]//i[@title="关闭"]')
        material.click_button('//div[div[text()="订单齐套结果-齐套明细"]]//i[@title="关闭"]')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击分批齐套成功")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_click2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]//span[text()="分批齐套"]')
        material.click_button('//div[div[div[text()="订单齐套结果-分批齐套"]]]//button[span[text()="刷新"]]')
        sleep(1)
        material.click_button('//div[div[text()="订单齐套结果-分批齐套"]]//i[@title="关闭"]')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击导出订单齐套结果不报错")
    # @pytest.mark.run(order=1)
    def test_material_ordercompleteresults_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单齐套结果"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询订单欠料表不报错")
    # @pytest.mark.run(order=1)
    def test_materia_orderdimension_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单欠料表"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询需求来源")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单欠料表"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[4]').text
        material.click_button('//div[span[text()="需求来源:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询订单列表")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单欠料表"])[1]')
        material.click_button('//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//div[@class="my-list-item"]//span)[last()]')
        material.click_select_button()
        name = material.get_find_element_xpath(
            '//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]').get_attribute("value")
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询产品编码")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select3(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单欠料表"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[6]').text
        material.click_button('//div[span[text()="产品编码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[6]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select4(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:2] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("包含")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(first_char in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select5(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合开头")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_material_orderdimension_select6(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合结尾")
        sleep(1)
        material.select_input('订单代码', last_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("点击导出订单欠料表不报错")
    # @pytest.mark.run(order=1)
    def test_materia_orderdimension_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单欠料表"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询物料欠料表不报错")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询需求来源")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[8]').text
        material.click_button('//div[span[text()="需求来源:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[8]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询订单列表")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        material.click_button('//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//div[@class="my-list-item"]//span)[last()]')
        material.click_select_button()
        name = material.get_find_element_xpath(
            '//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]').get_attribute("value")
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询采购员编码")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select3(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[2]').get_attribute('innerText')
        material.click_button('//div[span[text()="采购员编码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询物料代码")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select4(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        material.right_refresh('物料欠料表')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[3]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="物料代码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料欠料表')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select5(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.right_refresh('物料欠料表')
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[9]'
        ).get_attribute('innerText')
        first_char = name[:2] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("包含")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(first_char in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select6(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[9]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合开头")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_select7(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[9]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合结尾")
        sleep(1)
        material.select_input('订单代码', last_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单欠料表')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("点击导出物料欠料表不报错")
    # @pytest.mark.run(order=1)
    def test_material_materialdimension_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料欠料表"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询订单分批齐套不报错")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单分批齐套"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询需求来源")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单分批齐套"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[3]').text
        material.click_button('//div[span[text()="需求来源:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询订单列表")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单分批齐套"])[1]')
        material.click_button('//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//div[@class="my-list-item"]//span)[last()]')
        material.click_select_button()
        name = material.get_find_element_xpath(
            '//div[span[text()="订单列表:"]]//input[@placeholder="请选择"]').get_attribute("value")
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询产品编码")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select3(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单分批齐套"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[5]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="产品编码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select5(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:2] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("包含")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(first_char in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select6(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合开头")
        sleep(1)
        material.select_input('订单代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_select7(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        material.click_button('//div[div[p[text()="订单代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合结尾")
        sleep(1)
        material.select_input('订单代码', last_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('订单分批齐套')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("点击导出订单分批齐套不报错")
    # @pytest.mark.run(order=1)
    def test_material_batchcomplete_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="订单分批齐套"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询物料供应明细不报错")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询供应来源")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select1(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[3]').text
        material.click_button('//div[span[text()="供应来源:"]]//input[@placeholder="请选择"]')
        material.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询供应代码")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select2(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[4]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="供应代码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"])[last()]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询供应名称")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select3(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[5]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="供应名称:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"])[last()]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询业务单据号")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select4(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[6]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="业务单据号:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"])[last()]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[6]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("点击查询物料代码")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select5(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        name = material.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]/td[7]').get_attribute(
            'innerText')
        material.click_button('//div[span[text()="物料代码:"]]//input[@placeholder="请选择"]')
        sleep(1)
        material.click_button(f'(//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{name}"])[last()]')
        material.click_select_button()
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[7]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(name == text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_material_upplydetails_select6(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[4]'
        ).get_attribute('innerText')
        first_char = name[:2] if name else ""
        material.click_button('//div[div[p[text()="供应代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("包含")
        sleep(1)
        material.select_input('供应代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(first_char in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select7(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[4]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        material.click_button('//div[div[p[text()="供应代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合开头")
        sleep(1)
        material.select_input('供应代码', first_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_select8(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        name = material.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[4]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        material.click_button('//div[div[p[text()="供应代码"]]]//i[contains(@class,"suffixIcon")]')
        material.hover("符合结尾")
        sleep(1)
        material.select_input('供应代码', last_char)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[4]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        material.right_refresh('物料供应明细')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not material.has_fail_message()

    @allure.story("点击供应明细成功")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_click(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]//span[text()="供应明细"]')
        material.click_button('//div[div[text()="物料供应明细-供应明细"]]//i[@title="关闭"]')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击导出物料供应明细不报错")
    # @pytest.mark.run(order=1)
    def test_material_supplydetails_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="物料供应明细"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询供需分配明细不报错")
    # @pytest.mark.run(order=1)
    def test_material_allocationdetails_select(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="供需分配明细"])[1]')
        material.click_select_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击导出供需分配明细不报错")
    # @pytest.mark.run(order=1)
    def test_material_allocationdetails_export(self, login_to_materialplandata):
        driver = login_to_materialplandata  # WebDriver 实例
        material = MaterialPlanData(driver)  # 用 driver 初始化 MaterialPlanData
        material.click_button('(//span[text()="供需分配明细"])[1]')
        material.click_export_button()
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()