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
    page.click_button('(//span[text()="物控基础数据"])[1]')  # 点击计划基础数据
    page.click_button('(//span[text()="物料员"])[1]')  # 点击物品
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("物料员测试用例")
@pytest.mark.run(order=109)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        # 必填新增输入框xpath
        self.req_input_add_xpath_list = [
            "//div[@id='gd8ku89o-3d7y']//input",
            "//div[@id='skmun9z1-nw6o']//input"
        ]
        # 必填编辑输入框xpath
        self.req_input_edit_xpath_list = [
            "//div[@id='iyta2630-he9e']//input",
            "//div[@id='vlz4ket8-z4ke']//input"
        ]

        # 全部新增输入框xpath
        self.all_input_add_xpath_list = [
            "//div[@id='gd8ku89o-3d7y']//input",
            "//div[@id='skmun9z1-nw6o']//input"
            "//div[@id='kzar0tht-6si6']//input"
        ]
        # 全部编辑输入框xpath
        self.all_input_edit_xpath_list = [
            "//div[@id='iyta2630-he9e']//input",
            "//div[@id='vlz4ket8-z4ke']//input",
            "//div[@id='wvd5j8jq-bkkh']//input"
        ]

    @allure.story("添加供应商信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_addfail(self, login_to_item):
        sleep(3)
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0:
            layout = "测试布局A"
            self.item.add_layout(layout)
            # 获取布局名称的文本元素
            name = self.item.get_find_element_xpath(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
            ).text
        self.item.click_add_button()
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 物料员代码xpath
        input_box = self.item.get_find_element_xpath(
            "//div[@id='gd8ku89o-3d7y']//input"
        )
        # 物料员名称xpath
        inputname_box = self.item.get_find_element_xpath(
            "//div[@id='skmun9z1-nw6o']//input"
        )

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

    @allure.story("添加物料员信息，只填写物料员代码，不填写物料员名称，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialBuyer_addcodefail(self, login_to_item):

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='gd8ku89o-3d7y']//input", "text1231"
        )
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='skmun9z1-nw6o']//input"
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
    def test_materialBuyer_addsuccess(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        # 输入物料员代码
        self.item.enter_texts("//div[@id='gd8ku89o-3d7y']//input", "111")
        self.item.enter_texts("//div[@id='skmun9z1-nw6o']//input", "111")
        self.item.enter_texts("//div[@id='kzar0tht-6si6']//input", "111")

        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).text
        assert adddata == "111", f"预期数据是111，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts("//div[@id='gd8ku89o-3d7y']//input", "111")
        self.item.enter_texts("//div[@id='skmun9z1-nw6o']//input", "111")
        self.item.enter_texts("//div[@id='kzar0tht-6si6']//input", "111")
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
    def test_materialBuyer_delcancel(self, login_to_item):

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
    def test_materialBuyer_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts("//div[@id='gd8ku89o-3d7y']//input", "1测试A")
        self.item.enter_texts("//div[@id='skmun9z1-nw6o']//input", "1测试A")
        self.item.enter_texts("//div[@id='kzar0tht-6si6']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert adddata == "1测试A", f"预期数据是1测试A，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("修改物料员代码成功")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_editcodesuccess(self, login_to_item):
        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        text = "1测试A5"
        # 物料员代码输入
        self.item.enter_texts(
            "//div[@id='iyta2630-he9e']//input", f"{text}"
        )
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(3)
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]'
        ).text
        assert itemdata == text, f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("把修改后的供应商代码改回来")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_editcodesuccess2(self, login_to_item):
        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 供应商代码输入
        self.item.enter_texts("//div[@id='iyta2630-he9e']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert itemdata == "1测试A", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("修改物料员代码重复")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 供应商代码输入111
        self.item.enter_texts("//div[@id='iyta2630-he9e']//input", "111")
        self.item.enter_texts("//div[@id='vlz4ket8-z4ke']//input", "111")
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
    def test_materialBuyer_delsuccess1(self, login_to_item):
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
    def test_materialBuyer_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"

        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='iyta2630-he9e']//input",
            "//div[@id='vlz4ket8-z4ke']//input",
            "//div[@id='wvd5j8jq-bkkh']//input"
        ]

        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中物料员代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        print('input_values', input_values)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(input_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_delsuccess2(self, login_to_item):

        # 定位内容为‘1测试A’的行
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
        # 定位内容为‘1测试A’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    # @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    # def test_materialBuyer_refreshsuccess(self, login_to_item):
    #
    #     # 物料代码筛选框输入123
    #     self.item.enter_texts(
    #         '//p[text()="物料员代码"]/ancestor::div[2]//input', "123"
    #     )
    #     self.item.click_ref_button()
    #     itemtext = self.item.get_find_element_xpath(
    #         '//p[text()="物料员代码"]/ancestor::div[2]//input'
    #     ).text
    #     assert itemtext == "", f"预期{itemtext}"
    #     assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        input_xpath_list2 = [
            "//div[@id='iyta2630-he9e']//input",
            "//div[@id='vlz4ket8-z4ke']//input",
            "//div[@id='wvd5j8jq-bkkh']//input"
        ]
        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 批量修改输入框
        self.item.enter_texts("//div[@id='gd8ku89o-3d7y']//input", "111")
        self.item.enter_texts("//div[@id='skmun9z1-nw6o']//input", "111")
        self.item.enter_texts("//div[@id='kzar0tht-6si6']//input", "111")
        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中物料员代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list2, text_str)
        print('input_values', input_values)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            3 == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询物料员代码成功")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="物料员代码" and contains(@optid,"opt_")]')
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
    def test_materialBuyer_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="物料员代码" and contains(@optid,"opt_")]')
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
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBuyer_delsuccess3(self, login_to_item):
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
