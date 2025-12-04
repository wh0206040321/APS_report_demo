import random
from time import sleep

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
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
    page.click_button('(//span[text()="收货场所"])[1]')  # 点击收货场所
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("收货场所测试用例")
@pytest.mark.run(order=106)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        # 必填新增输入框xpath
        self.req_input_add_xpath_list = [
            "//div[@id='lfqwszyk-n29u']//input",
            "//div[@id='323e9o6g-i39o']//input"
        ]
        # 必填编辑输入框xpath
        self.req_input_edit_xpath_list = [
            "//div[@id='09w4bb17-u8r1']//input",
            "//div[@id='h28itby9-4l9e']//input"
        ]

        # 全部新增输入框xpath
        self.all_input_add_xpath_list = [
            "//div[@id='lfqwszyk-n29u']//input",
            "//div[@id='323e9o6g-i39o']//input",
            "//div[@id='c3qzeqy5-zl5z']//input"
        ]
        # 全部编辑输入框xpath
        self.all_input_edit_xpath_list = [
            "//div[@id='09w4bb17-u8r1']//input",
            "//div[@id='h28itby9-4l9e']//input",
            "//div[@id='kaclahjx-tpv5']//input"
        ]

    @allure.story("添加收货场所信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_addfail(self, login_to_item):
        sleep(3)
        divs = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0 and len(divs) > 1:
            layout = "测试布局A"
            self.item.add_layout(layout)
            # 获取布局名称的文本元素
            name = self.item.get_find_element_xpath(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
            ).text
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none(self.req_input_add_xpath_list, color_value)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加收货场所信息，有多个必填只填写一项，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialDelArea_addcodefail(self, login_to_item):
        # 点击新增按钮
        self.item.click_add_button()
        # 输入第一个必填项
        self.item.enter_texts("//div[@id='lfqwszyk-n29u']//input", "text1231")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        xpath_list = [
            "//div[@id='323e9o6g-i39o']//input"
        ]
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none(xpath_list, color_value)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中新增行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"

        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_delcancel(self, login_to_item):

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
    def test_materialDelArea_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "222"
        date_str = "2025/07/23 00:00:00"

        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

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
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("修改测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_editcodesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "333"
        # 输入框的xpath


        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 批量修改输入框
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

    @allure.story("修改数据重复")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()

        # 物料代码等输入111
        text_str = "111"
        self.item.batch_modify_input(self.req_input_edit_xpath_list, text_str)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_delsuccess1(self, login_to_item):
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

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"

        # 选中编辑数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_edit_xpath_list, text_str)

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
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(self.all_input_edit_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_delsuccess2(self, login_to_item):

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

    @allure.story("过滤刷新成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_refreshsuccess(self, login_to_item):

        filter_results = self.item.filter_method('//span[text()=" 收货地代码"]/ancestor::div[3]//span//span//span')
        print('filter_results', filter_results)
        assert filter_results
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_add_xpath_list, text_str)

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
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.all_input_add_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="收货地代码" and contains(@optid,"opt_")]')
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
        # 点击刷新
        self.item.click_ref_button()
        assert itemcode == "111" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_materialDelArea_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="收货地代码" and contains(@optid,"opt_")]')
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
    def test_materialDelArea_delsuccess3(self, login_to_item):
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
        if len(layout) > 1:
            self.item.del_layout("测试布局A")
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
