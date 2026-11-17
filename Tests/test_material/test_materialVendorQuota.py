import logging
import random
import re
from datetime import date
from time import sleep

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.materialPage.warehouseLocation_page import WarehouseLocationPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, all_driver_instances


@pytest.fixture(scope="module")
def login_to_item():
    """初始化并返回 driver"""
    driver_path = DateDriver().driver_path
    driver = create_driver(driver_path)
    driver.implicitly_wait(3)

    # 初始化登录页面
    page = LoginPage(driver)  # 初始化登录页面
    page.navigate_to(DateDriver().url)  # 导航到登录页面
    page.login(DateDriver().username, DateDriver().password, DateDriver().planning)
    page.click_button('(//span[text()="物控管理"])[1]')  # 点击计划管理
    page.click_button('(//span[text()="物控基础数据"])[1]')  # 点击计划基础数据
    page.click_button('(//span[text()="供应商配额"])[1]')  # 点击供应商配额
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("供应商配额测试用例")
@pytest.mark.run(order=107)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        # 必填新增输入框xpath
        self.req_input_add_xpath_list = [
            "//div[span[text()=' 配额物料代码 ']]/following-sibling::div//input",
            "//div[span[text()=' 供应商物料编码 ']]/following-sibling::div//input",
            "//div[span[text()=' 配额 ']]/following-sibling::div//input",
        ]

        # 必填新增日期xpath
        self.req_date_add_xpath_list = ["//div[span[text()=' 开始时间 ']]/following-sibling::div//input",
                                        "//div[span[text()=' 结束时间 ']]/following-sibling::div//input"]

        self.xpath_list1 = [
            f'//div[span[text()=" 安全比例{i} "]]/following-sibling::div//input'
            for i in range(1, 4)
        ]
        self.xpath_list2 = [
            f'//div[span[text()=" 安全需求笔数{i} "]]/following-sibling::div//input'
            for i in range(1, 4)
        ]
        self.xpath_list3 = [
            f'//div[span[text()=" 自定义字符{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        self.xpath_list4 = [
            f'//div[span[text()=" 自定义数值{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]

        # 全部新增输入框xpath
        self.all_input_add_xpath_list = [
            "//div[span[text()=' MPQ ']]/following-sibling::div//input",
            "//div[span[text()=' MOQ ']]/following-sibling::div//input",
            "//div[span[text()=' 检验提前天数 ']]/following-sibling::div//input",
            "//div[span[text()=' 累计纳入数量 ']]/following-sibling::div//input",
            "//div[span[text()=' 备注 ']]/following-sibling::div//input",
        ]
        self.all_input_add_xpath_list += self.req_input_add_xpath_list + self.xpath_list1 + self.xpath_list2 + self.xpath_list3 + self.xpath_list4

        # 全部新增日期xpath
        self.all_date_add_xpath_list = [
            f'//div[span[text()=" 自定义日期{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        self.all_date_add_xpath_list += self.req_date_add_xpath_list

        self.box_list2 = [
            "//div[span[text()=' 主物料代码 ']]/following-sibling::div//i",
            "//div[span[text()=' 供应商代码 ']]/following-sibling::div//i",
            "//div[span[text()=' 收货日历 ']]/following-sibling::div//i",
            "//div[span[text()=' 收货场所 ']]/following-sibling::div//i",
        ]
        self.box_list3 = [
            "//div[span[text()=' 锁定期间 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全最大天数1 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全最大天数2 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全最大天数3 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全期间1 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全期间2 ']]/following-sibling::div//i",
            "//div[span[text()=' 安全期间3 ']]/following-sibling::div//i",
        ]

    @allure.story("添加供应商配额信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addfail(self, login_to_item):
        self.item.wait_for_loading_to_disappear()
        layout = "测试布局A"
        self.item.add_layout(layout)
        # 获取布局名称的文本元素
        name = self.item.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        val = self.item.get_error_message()
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert val == "校验不通过，请检查标红的表单字段！"
        assert not self.item.has_fail_message()

    @allure.story("添加供应商配额信息，有多个必填只填写一项，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialVendorQuota_addcodefail(self, login_to_item):
        # 点击新增按钮
        self.item.click_add_button()
        # 输入第一个必填项
        self.item.batch_modify_input(self.req_input_add_xpath_list, "text1231")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        val = self.item.get_error_message()
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert val == "校验不通过，请检查标红的表单字段！"
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box(self.box_list2[:2], value_bos)
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2[:2]
        ]
        all_value = self.req_input_add_xpath_list + self.req_date_add_xpath_list + self.box_list
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 选中新增行
        self.item.click_button(f'//tr/td[2][.//span[text()="{code_value}"]]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        after_all_value = self.item.batch_acquisition_inputs(all_value)

        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box(self.box_list2[:2], value_bos)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_delcancel(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[4][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[4][.//span[text()="111"]]]/td[4]'
        ).text
        assert itemdata == "111", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "222"
        date_str = "2025/07/23 00:00:00"

        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[2]/td[3])[last()]'
        self.item.batch_modify_dialog_box(self.box_list2[:2], value_bos)
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2[:2]
        ]
        all_value = self.req_input_add_xpath_list + self.req_date_add_xpath_list + self.box_list
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 选中新增行
        self.item.click_button(f'//tr/td[2][.//span[text()="{code_value}"]]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        after_all_value = self.item.batch_acquisition_inputs(all_value)

        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("修改测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_editcodesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "333"
        # 输入框的xpath

        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[4][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        all_value = self.req_input_add_xpath_list
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        # 选中新增行
        self.item.click_button(f'//tr/td[4][.//span[text()="{text_str}"]]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        after_all_value = self.item.batch_acquisition_inputs(all_value)

        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("修改数据重复")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[4][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box1(self.box_list2[:2], value_bos)
        sleep(2)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "11测试全部数据"
        date_str = "2025/07/23 00:00:00"

        # 选中编辑数据
        self.item.click_button('//tr[./td[4][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 点击修改按钮
        self.item.batch_modify_inputs(self.all_input_add_xpath_list, text_str)
        self.item.batch_modify_inputs(self.all_date_add_xpath_list, date_str)

        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box1(self.box_list2[:2], value_bos)
        self.item.batch_modify_dialog_box(self.box_list2[-2:], value_bos)
        self.item.batch_num_box(self.box_list3, '12')
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2 + self.box_list3
        ]
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        all_value = self.all_input_add_xpath_list + self.all_date_add_xpath_list + self.box_list
        len_num = len(all_value)
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        self.item.right_refresh('供应商配额')
        self.item.wait_for_loading_to_disappear()
        num = self.item.go_settings_page()
        sleep(1)
        self.item.select_input('配额物料代码', text_str)
        sleep(1)
        self.item.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
        sleep(1)
        self.item.click_edi_button()
        after_all_value = self.item.batch_acquisition_inputs(all_value)
        username = self.item.get_find_element_xpath(
            '//div[span[text()=" 更新者 "]]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = self.item.get_find_element_xpath(
            '//div[span[text()=" 更新时间 "]]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        logging.info(f"before_all_value: {before_all_value}, after_all_value: {after_all_value}")
        ele = self.item.finds_elements(By.XPATH,
                                       f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
        if len(ele) == 1:
            self.item.click_button(
                f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
            self.item.click_del_button()  # 点击删除
            self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            self.item.get_find_message()
            self.item.wait_for_loading_to_disappear()
            self.item.right_refresh('供应商配额')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("过滤刷新成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_refreshsuccess(self, login_to_item):

        filter_results = self.item.filter_method('//span[text()=" 主物料代码"]/ancestor::div[3]//span//span//span')
        print('filter_results', filter_results)
        assert filter_results
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "11测试全部数据"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        self.item.click_add_button()  # 点击添加
        self.item.batch_modify_inputs(self.all_input_add_xpath_list, text_str)
        self.item.batch_modify_inputs(self.all_date_add_xpath_list, date_str)

        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box(self.box_list2, value_bos)
        self.item.batch_num_box(self.box_list3, '12')
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2 + self.box_list3
        ]
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        all_value = self.all_input_add_xpath_list + self.all_date_add_xpath_list + self.box_list
        len_num = len(all_value)
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        self.item.right_refresh('供应商配额')
        self.item.wait_for_loading_to_disappear()
        num = self.item.go_settings_page()
        sleep(1)
        self.item.select_input('配额物料代码', text_str)
        sleep(1)
        self.item.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
        sleep(1)
        self.item.click_edi_button()
        after_all_value = self.item.batch_acquisition_inputs(all_value)
        username = self.item.get_find_element_xpath(
            '//div[span[text()=" 更新者 "]]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = self.item.get_find_element_xpath(
            '//div[span[text()=" 更新时间 "]]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        logging.info(f"before_all_value: {before_all_value}, after_all_value: {after_all_value}")
        ele = self.item.finds_elements(By.XPATH,
                                       f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
        if len(ele) == 1:
            self.item.click_button(
                f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{code_value}"]]')
            self.item.click_del_button()  # 点击删除
            self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            self.item.get_find_message()
            self.item.wait_for_loading_to_disappear()
            self.item.right_refresh('供应商配额')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addsuccess3(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "444"
        date_str = "2025/07/23 00:00:00"

        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box([self.box_list2[0]], value_bos)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[2]/td[3])[last()]'
        self.item.batch_modify_dialog_box([self.box_list2[1]], value_bos)
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2[:2]
        ]
        all_value = self.req_input_add_xpath_list + self.req_date_add_xpath_list + self.box_list
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 选中新增行
        self.item.select_input('配额物料代码', text_str)
        self.item.click_button(f'//tr/td[2][.//span[text()="{code_value}"]]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        after_all_value = self.item.batch_acquisition_inputs(all_value)

        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_addsuccess4(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "555"
        date_str = "2025/07/23 00:00:00"

        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[2]/td[3])[last()]'
        self.item.batch_modify_dialog_box([self.box_list2[0]], value_bos)
        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3])[last()]'
        self.item.batch_modify_dialog_box([self.box_list2[1]], value_bos)
        self.box_list = [
            xpath.rsplit("//i", 1)[0] + "//input"
            for xpath in self.box_list2[:2]
        ]
        all_value = self.req_input_add_xpath_list + self.req_date_add_xpath_list + self.box_list
        code_value = self.item.get_find_element_xpath(self.box_list[0]).get_attribute("value")
        before_all_value = self.item.batch_acquisition_inputs(all_value)
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        self.item.select_input('配额物料代码', text_str)
        # 选中新增行
        self.item.click_button(f'//tr/td[2][.//span[text()="{code_value}"]]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        after_all_value = self.item.batch_acquisition_inputs(all_value)

        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_selectcodesuccess(self, login_to_item):
        self.item.right_refresh('供应商配额')
        driver = login_to_item  # WebDriver 实例
        item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage
        name = item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[4]').text

        # 点击查询
        item.click_sel_button()
        sleep(1)
        # 定位名称输入框
        element_to_double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        sleep(1)
        # 点击工厂代码
        item.click_button('//div[text()="配额物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        # 定位第一行是否为产品A
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[4]'
        ).text
        # 点击刷新
        self.item.click_ref_button()
        assert itemcode == name
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_selectnodatasuccess(self, login_to_item):

        # 点击查询
        self.item.click_sel_button()
        sleep(1)
        # 定位名称输入框
        element_to_double_click = self.driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(self.driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        sleep(1)
        # 点击交付单号
        self.item.click_button('//div[text()="主物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        self.item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        self.item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        self.item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        self.item.click_select_button()
        itemcode = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        # 点击刷新
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_select2(self, login_to_item):
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = self.item.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            self.item.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            self.item.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//input')
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        self.item.right_refresh('供应商配额')
        assert len(eles) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_select3(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('主物料代码', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('供应商配额')
        assert all(first_char.lower() in text.lower() for text in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_select4(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合开头")
        sleep(1)
        self.item.select_input('主物料代码', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('供应商配额')
        assert all(str(item).lower().startswith(first_char.lower()) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_select5(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合结尾")
        sleep(1)
        self.item.select_input('主物料代码', last_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('供应商配额')
        assert all(str(item).lower().endswith(last_char.lower()) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_clear(self, login_to_item):
        name = "3"
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('主物料代码', name)
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("清除所有筛选条件")
        sleep(1)
        ele = self.item.get_find_element_xpath(
            '//div[div[span[text()=" 主物料代码"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        self.item.right_refresh('供应商配额')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_ctrlIrepeat(self, login_to_item):
        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = self.item.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
        self.item.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_ctrlI(self, login_to_item):
        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('配额物料代码', '1没有数据添加')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[4])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_ctrlM(self, login_to_item):
        self.item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]//input', '1没有数据修改')
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('配额物料代码', '1没有数据修改')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[4])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        assert not self.item.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_shiftdel(self, login_to_item):
        self.item.right_refresh('供应商配额')
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        sleep(1)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]//input', '1没有数据修改1')
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[4])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[4])[2]//input', '1没有数据修改12')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[4])[2]').text
        ele2 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[4])[2]//input').get_attribute("value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('配额物料代码', '1没有数据修改1')
        ele11 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[4])[1]').get_attribute(
            "innerText")
        ele22 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[4])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        assert not self.item.has_fail_message()
        self.item.select_input('配额物料代码', '1没有数据修改')
        before_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[2])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        self.item.click_del_button()
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        after_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_ctrlC(self, login_to_item):
        self.item.right_refresh('供应商配额')
        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = self.item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        self.item.click_button('//div[div[span[text()=" 主物料代码"]]]//input')
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        self.item.right_refresh('供应商配额')
        assert all(before_data in ele for ele in eles)
        assert not self.item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_shift(self, login_to_item):
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not self.item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_ctrls(self, login_to_item):
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = self.item.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not self.item.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_shiftdel1(self, login_to_item):
        self.item.right_refresh('供应商配额')
        self.item.select_input('开始日期', '2025/07/23 00:00:00')
        before_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[2])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        self.item.click_del_button()
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        after_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendorQuota_delsuccess3(self, login_to_item):
        layout_name = "测试布局A"
        self.item.del_layout(layout_name)
        sleep(1)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = self.driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout_name} "]'
        )
        assert 0 == len(after_layout)
        assert not self.item.has_fail_message()
