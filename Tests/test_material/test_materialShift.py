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
    page.click_button('(//span[text()="物控管理"])[1]')
    page.click_button('(//span[text()="物控基础数据"])[1]')
    page.click_button('(//span[text()="收货班次"])[1]')  # 点击收货班次
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("收货班次测试用例")
@pytest.mark.run(order=118)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)

    @allure.story("添加信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_addfail(self, login_to_item):
        sleep(3)
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0:
            layout = "测试布局A"
            self.item.add_layout(layout)
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//p[text()='请填写信息']")
            )
        )
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        # 检查元素是否包含子节点
        assert message.text == "请填写信息"
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_item_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        self.item.enter_texts(
            "//label[text()='代码']/following-sibling::div//input", "111"
        )

        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')

        sleep(1)
        # 点击修改按钮
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(['//label[text()="代码"]/following-sibling::div//input'], "111")
        print('input_values', input_values)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(input_values) == 1
        )
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_item_delcancel(self, login_to_item):
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
    def test_item_addsuccess1(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        self.item.enter_texts(
            "//label[text()='代码']/following-sibling::div//input", "222"
        )

        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')

        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="222"]]]/td[2]'
        ).text
        print('input_values', input_values)
        assert input_values == "222", f"预期数据是1测试A，实际得到{input_values}"
        assert not self.item.has_fail_message()

    @allure.story("修改测试数据成功")
    # @pytest.mark.run(order=1)
    def test_item_editcodesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "333"

        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        self.item.enter_texts(
            "//label[text()='代码']/following-sibling::div//input", text_str
        )
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
        input_values = self.item.batch_acquisition_input(["//label[text()='代码']/following-sibling::div//input"], text_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(input_values) == 1
        )
        assert not self.item.has_fail_message()

    @allure.story("修改数据重复")
    # @pytest.mark.run(order=1)
    def test_item_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()

        self.item.enter_texts(
            "//label[text()='代码']/following-sibling::div//input", "333"
        )
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
    def test_item_delsuccess1(self, login_to_item):
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
    def test_item_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "11"
        # 输入框的xpath
        input_xpath_list = [
            "//label[text()='代码']/following-sibling::div//input",
            "//label[text()='备注']/following-sibling::div//input",
        ]

        # 选中编辑数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 点击显示颜色下拉
        self.item.click_button("//label[text()='显示颜色']/following-sibling::div/div")
        self.item.click_button("//label[text()='显示颜色']/following-sibling::div/div//li[@class='ivu-select-item'][1]")
        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        self.item.batch_modify_input([
            "(//label[text()='时间']/following-sibling::div//input)[1]",
            "(//label[text()='时间']/following-sibling::div//input)[2]",
            "(//label[text()='时间']/following-sibling::div//input)[3]"
        ], "11")
        self.item.batch_modify_input([
            "(//label[text()='时间']/following-sibling::div//input)[4]",
            "(//label[text()='时间']/following-sibling::div//input)[5]",
            "(//label[text()='时间']/following-sibling::div//input)[6]"
        ], "22")

        sleep(1)
        # 点击添加
        self.item.click_button("//span[text()='添加']")
        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据行
        self.item.click_button('//tr[./td[2][.//span[text()="11"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        time_text = self.item.get_find_element_xpath(
            '//span[text()="11:11:11-22:22:22"]'
        ).text
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(input_xpath_list) == len(input_values) and time_text == "11:11:11-22:22:22"
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess2(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="11"]]]/td[2]')
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
            By.XPATH, '//tr[./td[2][.//span[text()="11"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    # @allure.story("过滤刷新成功")
    # # @pytest.mark.run(order=1)
    # def test_item_refreshsuccess(self, login_to_item):
    #
    #     filter_results = self.item.filter_method('//span[text()=" 班次代码"]/ancestor::div[3]//span//span//span')
    #     print('filter_results', filter_results)
    #     assert filter_results
    #     assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_item_add_success(self, login_to_item):

        # 输入框的xpath
        input_xpath_list = [
            "//label[text()='代码']/following-sibling::div//input",
            "//label[text()='备注']/following-sibling::div//input",
        ]
        text_str = "22"
        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 点击显示颜色下拉
        self.item.click_button("//label[text()='显示颜色']/following-sibling::div/div")
        self.item.click_button("//label[text()='显示颜色']/following-sibling::div/div//li[@class='ivu-select-item'][1]")
        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        self.item.batch_modify_input([
            "(//label[text()='时间']/following-sibling::div//input)[1]",
            "(//label[text()='时间']/following-sibling::div//input)[2]",
            "(//label[text()='时间']/following-sibling::div//input)[3]"
        ], "11")
        self.item.batch_modify_input([
            "(//label[text()='时间']/following-sibling::div//input)[4]",
            "(//label[text()='时间']/following-sibling::div//input)[5]",
            "(//label[text()='时间']/following-sibling::div//input)[6]"
        ], "22")

        sleep(1)
        # 点击添加
        self.item.click_button("//span[text()='添加']")
        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据行
        self.item.click_button('//tr[./td[2][.//span[text()="22"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        time_text = self.item.get_find_element_xpath(
            '//span[text()="11:11:11-22:22:22"]'
        ).text
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(input_xpath_list) == len(input_values) and time_text == "11:11:11-22:22:22"
        )
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_item_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="班次代码" and contains(@optid,"opt_")]')
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
            "22",
        )
        sleep(1)

        # 点击确认
        item.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[4]'
        )
        sleep(1)
        # 定位第一行是否为产品A
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[2]',
        )
        # 点击刷新
        self.item.click_ref_button()
        assert itemcode == "22" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_item_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="班次代码" and contains(@optid,"opt_")]')
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
        self.item.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[4]'
        )
        sleep(2)
        itemcode = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        )
        sleep(1)

        # 点击刷新
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess3(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="22"]]]/td[2]')
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
        layout_name = "测试布局A"
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="22"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
