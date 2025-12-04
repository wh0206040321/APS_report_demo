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
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.materialPage.materialControlDefinition_page import MaterialControlDefinition
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_materialRequirementsDefinition():
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
        list_ = ["计划运行", "方案管理", "物控需求定义"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物控需求定义页用例")
@pytest.mark.run(order=140)
class TestSMaterialRequirementsDefinitionPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addfail1(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.click_all_button("新增")
        sleep(1)
        material.click_confirm()
        message = material.get_error_message()
        assert message == "请填写表单必填项!"
        assert not material.has_fail_message()

    @allure.story("不填写字段映射不允许添加")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addfail2(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        adds = AddsPages(driver)
        material.click_all_button("新增")
        sleep(1)
        input_list = [
            '//div[div[text()=" 需求来源编码: "]]//input',
            '//div[div[text()=" 需求来源名称: "]]//input',
        ]
        select_list = [
            {"select": '//div[div[text()=" 数据库名称: "]]//input[@class="ivu-select-input"]', "value": '(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[1]/li[1]'},
            {"select": '//div[div[text()=" 表或视图名: "]]//input[@class="ivu-select-input"]', "value": '(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[2]/li[text()="APS_Order"]'},
        ]
        fields = [
            "DataSource",
            "OrderCode",
            "ItemCode",
            "PlanStartTime",
            "PlanQty",
            "BomVersion",
            "ReleaseMat"
        ]

        table_list = []

        for i, field in enumerate(fields, start=2):  # 从2开始递增
            entry = {
                "select": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]',
                "value": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]//li[{i}]'
            }
            table_list.append(entry)
        material.click_button('//label[span[text()="制造"]]')
        adds.batch_modify_select_input(select_list)
        adds.batch_modify_input(input_list, '1测试数据1')
        material.click_confirm()
        message = material.get_error_message()
        assert message == "请填写必录的字段映射!"
        assert not material.has_fail_message()

    @allure.story("添加需求来源编码成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addsuccess1(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "1测试数据1"
        material.add_data(value)
        message = material.get_find_message()
        material.select_input_mrq(value)
        ele = material.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{value}"]')
        assert message == "保存成功" and len(ele) == 1
        assert not material.has_fail_message()

    @allure.story("添加测试数据需求来源编码成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addsuccess2(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "1测试数据2"
        material.add_data(value)
        message = material.get_find_message()
        material.select_input_mrq(value)
        ele = material.finds_elements(By.XPATH,
                                      f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{value}"]')
        assert message == "保存成功" and len(ele) == 1
        assert not material.has_fail_message()

    @allure.story("添加测试数据需求来源编码成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addsuccess3(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "2测试数据2"
        material.add_data(value)
        message = material.get_find_message()
        material.select_input_mrq(value)
        ele = material.finds_elements(By.XPATH,
                                      f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{value}"]')
        assert message == "保存成功" and len(ele) == 1
        assert not material.has_fail_message()

    @allure.story("添加重复需求来源编码不允许添加")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_addrepeat(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "1测试数据1"
        material.add_data(value)
        sleep(1)
        message = material.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').text
        assert message == "记录已存在,请检查！"
        assert not material.has_fail_message()

    @allure.story("修改需求来源编码不允许修改")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_updaterepeat(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "1测试数据2"
        material.select_input_mrq(value)
        material.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{value}"]')
        material.click_all_button("编辑")
        sleep(2)
        ele = material.get_find_element_xpath('//div[div[text()=" 需求来源编码: "]]//input')
        assert not ele.is_enabled()
        assert not material.has_fail_message()

    @allure.story("修改名称和类型成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_updatesuccess(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        value = "1测试数据2"
        material.select_input_mrq(value)
        material.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{value}"]')
        material.click_all_button("编辑")
        sleep(2)
        material.enter_texts('//div[div[text()=" 需求来源名称: "]]//input', "1测试数据2修改")
        material.click_button('//label[span[text()="销售"]]')
        material.click_confirm()
        message = material.get_find_message()
        material.select_input_mrq(value)
        ele1 = material.get_find_element_xpath(f'(//table[@class="vxe-table--body"])[1]//tr[td[2]//span[text()="{value}"]]/td[3]').text
        ele2 = material.get_find_element_xpath(
            f'(//table[@class="vxe-table--body"])[1]//tr[td[2]//span[text()="{value}"]]/td[4]').text
        assert message == "保存成功" and ele1 == "1测试数据2修改" and ele2 == "销售"
        assert not material.has_fail_message()

    @allure.story("查询需求编码成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_selectsuccess1(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        material.click_button('//div[span[text()=" 需求编码: "]]//input[@class="ivu-select-input"]')
        material.click_button('//ul[@class="ivu-select-dropdown-list"]/li[2]/div')
        sleep(1)
        material.click_button('//button[span[text()="查询"]]')
        sel_value = material.get_find_element_xpath('//div[span[text()=" 需求编码: "]]//input[@class="ivu-select-input"]').get_attribute("value")
        material.wait_for_loading_to_disappear()
        ele = material.get_find_element_xpath(f'(//table[@class="vxe-table--body"])[1]//tr[1]/td[2]').text
        ele1 = material.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[1]//tr[2]/td[2]')
        assert sel_value == ele and len(ele1) == 0
        assert not material.has_fail_message()

    @allure.story("查询数据库名称成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_selectsuccess2(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        material.click_button('//div[span[text()="数据库名称: "]]//input[@class="ivu-select-input"]')
        material.click_button('(//ul[@class="ivu-select-dropdown-list"])[2]/li[1]')
        sleep(1)
        material.click_button('//button[span[text()="查询"]]')
        sel_value = material.get_find_element_xpath(
            '//div[span[text()="数据库名称: "]]//input[@class="ivu-select-input"]').get_attribute("value")
        material.wait_for_loading_to_disappear()
        eles = material.loop_judgment(f'(//table[@class="vxe-table--body"])[1]//tr/td[5]')
        assert all(sel_value == ele for ele in eles)
        assert not material.has_fail_message()

    @allure.story("过滤查需求来源编码成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_select1(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        name = "测试数据"
        sleep(1)
        material.select_input_mrq(name)
        sleep(2)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_select2(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        eles = material.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            material.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            material.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//input')
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_select3(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        name = "2"
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        material.hover("包含")
        sleep(1)
        material.select_input_mrq(name)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_select4(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        name = "2"
        material.wait_for_loading_to_disappear()
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        material.hover("符合开头")
        sleep(1)
        material.select_input_mrq(name)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not material.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_select5(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        name = "2"
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        material.hover("符合结尾")
        sleep(1)
        material.select_input_mrq(name)
        sleep(1)
        eles = material.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not material.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_clear(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
        material.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        material.hover("包含")
        sleep(1)
        material.select_input_mrq(name)
        sleep(1)
        material.click_button('//div[p[text()="需求来源编码"]]/following-sibling::div//i')
        material.hover("清除所有筛选条件")
        sleep(1)
        ele = material.get_find_element_xpath('//div[p[text()="需求来源编码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not material.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialRequirementsDefinition_delsuccess(self, login_to_materialRequirementsDefinition):
        driver = login_to_materialRequirementsDefinition  # WebDriver 实例
        material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition

        material.wait_for_loading_to_disappear()
        value = ['1测试数据1','1测试数据2','2测试数据2']
        material.del_all(xpath='//div[p[text()="需求来源编码"]]/following-sibling::div//input', value=value)
        material.right_refresh(name='物控需求定义')
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:1]
        ]

        assert all(len(elements) == 0 for elements in itemdata)
        assert not material.has_fail_message()