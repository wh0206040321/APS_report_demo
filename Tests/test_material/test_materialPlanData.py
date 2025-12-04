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


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
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