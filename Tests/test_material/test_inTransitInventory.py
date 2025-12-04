import random
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


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
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
    page.click_button('(//span[text()="物控业务数据"])[1]')  # 点击计划基础数据
    page.click_button('(//span[text()="在途库存"])[1]')  # 点击在途库存
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("在途库存测试用例")
@pytest.mark.run(order=116)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        self.req_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='ala93hyv-asdp']//input",
            "//div[@id='x1k7t87i-tvc3']//input",
            "//div[@id='hpjqsv1m-5607']//input",
            "//div[@id='izykzohi-1l5u']//input",
        ]
        self.req_input_edit_xpath_list = [
            "//div[@id='xx7m7b9f-b17x']//input",
            "//div[@id='ohezjo9h-rfjj']//input",
            "//div[@id='iy5w2ran-gvws']//input",
            "//div[@id='0xkp18kz-538e']//input",
            "//div[@id='stgrae91-yols']//input",
        ]

        # 必填新增日期xpath
        self.req_date_add_xpath_list = ["//div[@id='f4ke63vb-p976']//input"]
        # 必填编辑日期xpath
        self.req_date_edit_xpath_list = ["//div[@id='q641pjc6-72hq']//input"]

        self.all_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='x1k7t87i-tvc3']//input",
            "//div[@id='hpjqsv1m-5607']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='z0h20cps-xzrs']//input",
            "//div[@id='7z1rv7fs-trb6']//input",
            "//div[@id='5607jw8y-5owy']//input",
            "//div[@id='hguo4esk-gii0']//input",
            "//div[@id='13j55ae1-8hj2']//input",
            "//div[@id='izykzohi-1l5u']//input",
            "//div[@id='ctfddy1k-hbmj']//input",
            "//div[@id='0t8pfkrw-y5i1']//input",
            "//div[@id='8sgoh6vh-0pz5']//input",
            "//div[@id='poxayyhi-9bss']//input",
            "//div[@id='zxc6ccwu-bnwe']//input",
            "//div[@id='15qig6pt-sj1x']//input",
            "//div[@id='ala93hyv-asdp']//input"
        ]

        self.all_date_add_xpath_list = [
            "//div[@id='f4ke63vb-p976']//input",
            "//div[@id='3ftxmm2w-wsu0']//input",
            "//div[@id='fiem2b4y-n1p4']//input",
            "//div[@id='kjspka9m-rggf']//input",
            "//div[@id='fuamd55w-q82r']//input",
            "//div[@id='u7zkevl6-j2rm']//input"
        ]

        self.all_input_edit_xpath_list = [
            "//div[@id='xx7m7b9f-b17x']//input",
            "//div[@id='ohezjo9h-rfjj']//input",
            "//div[@id='iy5w2ran-gvws']//input",
            "//div[@id='0xkp18kz-538e']//input",
            "//div[@id='stgrae91-yols']//input",
            "//div[@id='x6jyak6g-djx0']//input",
            "//div[@id='un840e10-hyfc']//input",
            "//div[@id='d82zp89g-3dbj']//input",
            "//div[@id='w4z46vv0-dbvt']//input",
            "//div[@id='7lghwgwr-8pys']//input",
            "//div[@id='q3s7swsm-8djd']//input",
            "//div[@id='1t56r2la-k30n']//input",
            "//div[@id='9e6qvlk6-1hfl']//input",
            "//div[@id='flktdy60-ijv0']//input",
            "//div[@id='6rzbvkx5-tre9']//input",
            "//div[@id='0lnsvgp9-gt7v']//input",
            "//div[@id='c3qlvloy-mmjz']//input"
        ]

        self.all_date_edit_xpath_list = [
            "//div[@id='q641pjc6-72hq']//input",
            "//div[@id='3kup70v6-yvm5']//input",
            "//div[@id='505hhv5m-6ayp']//input",
            "//div[@id='qb6fwjzp-eqbr']//input",
            "//div[@id='9ucfa7pd-24rf']//input",
            "//div[@id='pav1z642-b0wx']//input"
        ]

    @allure.story("添加库存信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_addfail(self, login_to_item):
        self.item.click_add_button()
        # 在途库存单据号xpath
        input_box = self.item.get_find_element_xpath(
            "//div[@id='p34nag46-7evf']//input"
        )
        # 在途数量xpath
        inputname_box = self.item.get_find_element_xpath(
            "//div[@id='izykzohi-1l5u']//div[1]"
        )

        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{bordername_color}"
        assert not self.item.has_fail_message()

    @allure.story("添加在途库存信息，只填写在途数量，不填写在途库存单据号等，不允许提交")
    # @pytest.mark.run(order=2)
    def test_inTransitInventory_addcodefail(self, login_to_item):

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='izykzohi-1l5u']//input", "text1231"
        )
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='p34nag46-7evf']//input"
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='ala93hyv-asdp']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)

        # 在途库存单据号
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "111")
        # 在途可用日期
        self.item.enter_texts("//div[@id='f4ke63vb-p976']//input", "2025/07/17 00:00:00")
        # 供应商代码
        self.item.enter_texts("//div[@id='x1k7t87i-tvc3']//input", "111")
        # 物料代码
        self.item.enter_texts("//div[@id='hpjqsv1m-5607']//input", "111")
        # 输入在途数量
        self.item.enter_texts("//div[@id='izykzohi-1l5u']//input", "111")
        # 输入行哈
        self.item.enter_texts("//div[@id='ala93hyv-asdp']//input", "111")

        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中新增行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, "111")
        # 批量获取日期选择框的value
        input_values2 = self.item.batch_acquisition_input(self.req_date_edit_xpath_list, "2025/07/17 00:00:00")
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values) and
                len(self.req_date_add_xpath_list) == len(input_values2)
        )
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_addrepeat(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        self.item.click_add_button()
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='ala93hyv-asdp']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.finds_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(error_popup) == 1
        )
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_delcancel(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).text
        assert itemdata == "111", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_addsuccess1(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "222"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='ala93hyv-asdp']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)
        self.item.batch_modify_input(self.req_date_add_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中新增行
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)
        # 批量获取日期选择框的value
        input_values2 = self.item.batch_acquisition_input(self.req_date_edit_xpath_list, "2025/07/23 00:00:00")

        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values) and
                len(self.req_date_add_xpath_list) == len(input_values2)
        )
        assert not self.item.has_fail_message()

    @allure.story("修改物料员代码成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_editcodesuccess(self, login_to_item):
        # 输入框要修改的值
        text_str = "333"
        date_str = "2025/07/25 00:00:00"
        # 输入框的xpath

        sleep(4)
        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        for req in self.req_input_edit_xpath_list:
            ele = self.item.get_find_element_xpath(req)
            # 清空数字输入框
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.BACK_SPACE)
            sleep(0.5)

        self.item.batch_modify_input(self.req_input_edit_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(self.req_input_edit_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("修改物料员代码重复")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_editrepeat(self, login_to_item):
        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)
        for req in self.req_input_edit_xpath_list:
            ele = self.item.get_find_element_xpath(req)
            # 清空数字输入框
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.BACK_SPACE)
            sleep(0.5)

        # 物料代码等输入111
        text_str = "111"
        self.item.batch_modify_input(self.req_input_edit_xpath_list, text_str)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        error_popup = self.item.finds_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(error_popup) == 1
        )
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_delsuccess1(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.get_find_message()
        self.item.click_ref_button()
        self.item.wait_for_loading_to_disappear()
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_editnamesuccess(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(4)
        # 选中编辑数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        for req in self.req_input_edit_xpath_list:
            ele = self.item.get_find_element_xpath(req)
            # 清空数字输入框
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.BACK_SPACE)
            sleep(0.5)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_edit_xpath_list, text_str)
        self.item.batch_modify_input(self.all_date_edit_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.all_input_edit_xpath_list, text_str)
        input_values2 = self.item.batch_acquisition_input(self.all_date_edit_xpath_list, date_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.all_input_edit_xpath_list) == len(input_values) and
                len(self.all_date_edit_xpath_list) == len(input_values2)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_delsuccess2(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_refreshsuccess(self, login_to_item):

        filter_results = self.item.filter_method('//span[text()=" 在途库存单据号"]/ancestor::div[3]//span//span//span')
        print('filter_results', filter_results)
        assert filter_results
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        self.item.click_add_button()  # 点击添加
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='ala93hyv-asdp']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)
        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_add_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(self.all_date_add_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中物料代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.all_input_edit_xpath_list, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(self.all_date_edit_xpath_list, date_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.all_input_add_xpath_list) == len(input_values)
                and len(self.all_date_add_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询物料员代码成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_selectcodesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage

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
        item.click_button('//div[text()="在途库存单据号" and contains(@optid,"opt_")]')
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
            "111",
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        # 定位第一行是否为产品A
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert itemcode == "111" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_selectnodatasuccess(self, login_to_item):

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
        # 点击物料代码
        self.item.click_button('//div[text()="在途库存单据号" and contains(@optid,"opt_")]')
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

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_inTransitInventory_delsuccess3(self, login_to_item):
        layout_name = "测试布局A"
        sleep(4)
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.click_ref_button()
        sleep(1)
        layout = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        print('layout', len(layout))
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
