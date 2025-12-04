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
from Pages.materialPage.materialControlDefinition_page import MaterialControlDefinition
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_materialCalculateResume():
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
        list_ = ["计划运行", "计算工作台", "物控计算履历"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        material = MaterialControlDefinition(driver)
        material.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物控计算履历页用例")
@pytest.mark.run(order=144)
class TestSMaterialCalculateResumePage:

    @allure.story("点击查询物控计算单号成功")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_select1(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition

        material.click_select_mcr(code='1')
        name = material.get_find_element_xpath('//div[span[text()="物控计算单号:"]]//input[@class="ivu-select-input"]').get_attribute("value")
        ele = material.get_find_element_xpath(f'(//table[@class="vxe-table--body"])[1]//tr[1]/td[3]').text
        ele1 = material.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[1]//tr[2]/td[3]')
        assert name == ele and len(ele1) == 0
        assert not material.has_fail_message()

    @allure.story("点击查询物控方案名称成功")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_select2(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition

        material.click_select_mcr(data='1')
        name = material.get_find_element_xpath(
            '//div[span[text()="物控方案名称:"]]//input[@class="ivu-select-input"]').get_attribute("value")
        eles = material.loop_judgment('//table[@class="vxe-table--body"]//tr/td[5]')
        assert all(name == ele for ele in eles)
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询-订单齐套结果不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_completeresults(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('订单齐套结果')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询-订单分批齐套不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_batchcomplete(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('订单分批齐套')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询- 欠料表（订单维度） 不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_orderdimension(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('欠料表（订单维度）')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询- 欠料表（物料维度） 不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_materialdimension(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('欠料表（物料维度）')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询-物料供应明细 不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_supplydetails(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('物料供应明细')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询-供需分配明细 不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_allocationdetails(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('供需分配明细')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击详情点击查询-交付需求明细 不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_details_requirementdetails(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_details('交付需求明细')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    @allure.story("点击日志不报错")
    # @pytest.mark.run(order=1)
    def test_materialCalculateResume_clicklog(self, login_to_materialCalculateResume):
        driver = login_to_materialCalculateResume  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_button('//button[span[text()="日志"]]')
        material.click_button('(//button[span[text()="关闭"]])[last()]')
        ele = material.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not material.has_fail_message()

    # @allure.story("删除数据成功")
    # # @pytest.mark.run(order=1)
    # def test_materialCalculateResume_del(self, login_to_materialCalculateResume):
    #     driver = login_to_materialCalculateResume  # WebDriver 实例
    #     material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
    #     before_data = material.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
    #     before_count = int(re.search(r'\d+', before_data).group())
    #     material.click_button('(//button[span[text()="删除"]])[1]')
    #     material.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
    #     material.get_find_message()
    #     sleep(1)
    #     after_data = material.get_find_element_xpath(
    #         '(//span[contains(text(),"条记录")])[1]'
    #     ).text
    #     after_count = int(re.search(r'\d+', after_data).group())
    #     assert before_count - after_count == 1, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
    #     assert not material.has_fail_message()


