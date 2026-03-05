import random
import re
from time import sleep

import allure
import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.materialPage.warehouseLocation_page import WarehouseLocationPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, all_driver_instances


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
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
    page.click_button('(//span[text()="仓库库位"])[1]')  # 点击物品
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("仓库库位测试用例")
@pytest.mark.run(order=100)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)

    @allure.story("添加仓库库位信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_addfail(self, login_to_item):
        sleep(3)
        divs = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0 and len(divs) > 1:
            layout = "测试布局A"
            self.item.add_layout(layout)
        self.item.click_add_button()
        # 工厂代码xpath
        input_box = self.item.get_find_element_xpath(
            "//div[@id='p34nag46-7evf']//input"
        )
        # 仓库编码xpath
        inputname_box = self.item.get_find_element_xpath(
            "//div[@id='ywz9q11i-sp3b']//input"
        )
        # 库位编码xpath
        whs_code_box = self.item.get_find_element_xpath(
            "//div[@id='u2tgl5h9-otp1']//input"
        )
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        whs_code_color = whs_code_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        sleep(1)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{bordername_color}"
        assert (
                whs_code_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{whs_code_color}"
        assert not self.item.has_fail_message()

    @allure.story("添加仓库库位信息，只填写工厂代码，不填写仓库编码，不允许提交")
    # @pytest.mark.run(order=2)
    def test_warehouselocation_addcodefail(self, login_to_item):
        # driver = login_to_item  # WebDriver 实例
        # item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='p34nag46-7evf']//input", "text1231"
        )
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='u2tgl5h9-otp1']//input"
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        sleep(1)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入工厂代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "111")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "111")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "111")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).text
        assert adddata == "111", f"预期数据是111，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入物料代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "111")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "111")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "111")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        sleep(1)
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_delcancel(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).get_attribute('innerText')
        assert itemdata == "111", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入工厂代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "1测试A")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "1测试A")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "1测试A")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert adddata == "1测试A", f"预期数据是1测试A，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("修改工厂代码重复")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 工厂代码输入111
        self.item.enter_texts("//div[@id='2gqlayrh-vwyr']//input", "111")
        self.item.enter_texts("//div[@id='uqtb82o5-7f7f']//input", "111")
        self.item.enter_texts("//div[@id='mhj7cxc6-rywr']//input", "111")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute('innerText')
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("修改工厂代码成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_editcodesuccess(self, login_to_item):
        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = "1测试A5"
        # 物料代码输入
        self.item.enter_texts(
            "//div[@id='2gqlayrh-vwyr']//input", f"{text}"
        )
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]'
        ).text
        assert itemdata == text, f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("把修改后的物料代码改回来")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_editcodesuccess2(self, login_to_item):

        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 物料代码输入
        self.item.enter_texts("//div[@id='2gqlayrh-vwyr']//input", "1测试A")
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert itemdata == "1测试A", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "222"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='2gqlayrh-vwyr']//input",
            "//div[@id='x2xfoigm-rdd2']//input",
            "//div[@id='ze6hpeia-qlcv']//input",
            "//div[@id='8rmn9d4u-ll8o']//input",
            "//div[@id='uqtb82o5-7f7f']//input",
            "//div[@id='mhj7cxc6-rywr']//input",
            "//div[@id='jwmtz1cs-qxcf']//input",
            "//div[@id='mw9lvgil-ay4b']//input",
            "//div[@id='9hougeja-f19h']//input",
            "//div[@id='euflllc4-91y5']//input",
            "//div[@id='cd607kel-iwfp']//input",
            "//div[@id='uw1sjnqs-by95']//input",
            "//div[@id='b42zf3g4-ly6d']//input",
            "//div[@id='sv7m9mzk-eo1b']//input",
            "//div[@id='qpydcf68-3n30']//input",
            "//div[@id='me9njjkp-e9rg']//input",
            "//div[@id='8czb193p-h4wb']//input"
        ]
        # 日期的xpath
        date_xpath_list = [
            "//div[@id='f9nnaus3-q1qr']//input",
            "//div[@id='890pwofe-fsbm']//input",
            "//div[@id='pcceybkb-1zqi']//input",
            "//div[@id='h21yy3zx-sob7']//input",
            "//div[@id='w2b54of4-62z0']//input"
        ]

        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 修改是否可用 否
        self.item.click_button("//div[@id='m1hs2m05-cwhg']")
        self.item.click_button('//div[@class="my-list-item"]')

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(date_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(date_xpath_list, date_str)
        item_sel = self.item.get_find_element_xpath(
            '//div[@id="m1hs2m05-cwhg"]//input'
        ).get_attribute("value")
        print('input_values', input_values)
        print('date_values', date_values)
        print('item_sel', item_sel)
        sleep(1)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            len(input_xpath_list) == len(input_values)
            and item_sel == "否"
            and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("筛选刷新成功")
    # @pytest.mark.run(order=1)
    # def test_warehouselocation_refreshsuccess(self, login_to_item):
    #     filter_results = self.item.filter_method('//span[text()=" 工厂代码"]/ancestor::div[3]//span//span//span')
    #     assert filter_results
    #     assert not self.item.has_fail_message()

    @allure.story("查询工厂代码成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="工厂代码" and contains(@optid,"opt_")]')
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
            "222",
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
        item.right_refresh('仓库库位')
        assert itemcode == "222" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="工厂代码" and contains(@optid,"opt_")]')
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
        self.item.right_refresh('仓库库位')
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    # @allure.story("查询物料名字成功")
    # @pytest.mark.run(order=1)
    # def test_warehouselocation_selectnamesuccess(self, login_to_item):
    #
    #     # 点击查询
    #     self.item.click_sel_button()
    #     sleep(1)
    #     # 定位名称输入框
    #     element_to_double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(self.driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     self.item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     self.item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "M1",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     self.item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行是否为M1
    #     itemcode = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[3]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = self.driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[3]',
    #     )
    #     self.item.click_ref_button()
    #     assert itemcode == "M1" and len(itemcode2) == 0
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("查询物料优先度>60")
    # @pytest.mark.run(order=1)
    # def test_warehouselocation_selectsuccess1(self, login_to_item):
    #     # 点击查询
    #     self.item.click_sel_button()
    #     sleep(1)
    #     # 定位名称输入框
    #     element_to_double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(self.driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料优先度
    #     self.item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     self.item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "60",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     self.item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     # 定位第二行数据
    #     itemcode2 = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[6]'
    #     ).text
    #     self.item.click_ref_button()
    #     assert int(itemcode) > 60 and int(itemcode2) > 60
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("查询物料名称包含材料并且物料优先度>70")
    # @pytest.mark.run(order=1)
    # def test_warehouselocation_selectsuccess2(self, login_to_item):
    #
    #     # 点击查询
    #     self.item.click_sel_button()
    #     sleep(1)
    #
    #     # 定位名称输入框
    #     element_to_double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(self.driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     self.item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     self.item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     self.item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "材料",
    #     )
    #
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     self.item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
    #     )
    #     # 双击命令
    #     actions.double_click(double_click).perform()
    #     # 定义and元素的XPath
    #     and_xpath = '//div[text()="and" and contains(@optid,"opt_")]'
    #
    #     try:
    #         # 首先尝试直接查找并点击and元素
    #         and_element = WebDriverWait(self.driver, 2).until(
    #             EC.presence_of_element_located((By.XPATH, and_xpath))
    #         )
    #         and_element.click()
    #     except:
    #         # 如果直接查找失败，进入循环双击操作
    #         max_attempts = 5
    #         attempt = 0
    #         and_found = False
    #
    #         while attempt < max_attempts and not and_found:
    #             try:
    #                 # 执行双击操作
    #                 actions.double_click(double_click).perform()
    #                 sleep(1)
    #
    #                 # 再次尝试查找and元素
    #                 and_element = WebDriverWait(self.driver, 2).until(
    #                     EC.presence_of_element_located((By.XPATH, and_xpath))
    #                 )
    #                 and_element.click()
    #                 and_found = True
    #             except:
    #                 attempt += 1
    #                 sleep(1)
    #
    #         if not and_found:
    #             raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'and'元素")
    #
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     self.item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     self.item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     self.item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         "70",
    #     )
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     self.item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     self.item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     itemname = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[3]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = self.driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[10]',
    #     )
    #     self.item.click_ref_button()
    #     # 判断第一行物料优先度>70 并且 物料名称为材料B 并且第二行没有数据
    #     assert int(itemcode) > 70 and itemname == "材料B" and len(itemcode2) == 0
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("查询物料名称包含材料或物料优先度>70")
    # @pytest.mark.run(order=1)
    # def test_warehouselocation_selectsuccess3(self, login_to_item):
    #
    #     # 点击查询
    #     self.item.click_sel_button()
    #     sleep(1)
    #
    #     # 定位名称输入框
    #     element_to_double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(self.driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     self.item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     self.item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     self.item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "材料",
    #     )
    #
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     self.item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #     double_click = self.driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
    #     )
    #     # 双击命令
    #     sleep(1)
    #     actions.double_click(double_click).perform()
    #     # 定义or元素的XPath
    #     or_xpath = '//div[text()="or" and contains(@optid,"opt_")]'
    #
    #     try:
    #         # 首先尝试直接查找并点击or元素
    #         and_element = WebDriverWait(self.driver, 2).until(
    #             EC.presence_of_element_located((By.XPATH, or_xpath))
    #         )
    #         and_element.click()
    #     except:
    #         # 如果直接查找失败，进入循环双击操作
    #         max_attempts = 5
    #         attempt = 0
    #         or_found = False
    #
    #         while attempt < max_attempts and not or_found:
    #             try:
    #                 # 执行双击操作
    #                 actions.double_click(double_click).perform()
    #                 sleep(1)
    #
    #                 # 再次尝试查找or元素
    #                 or_element = WebDriverWait(self.driver, 2).until(
    #                     EC.presence_of_element_located((By.XPATH, or_xpath))
    #                 )
    #                 or_element.click()
    #                 or_found = True
    #             except:
    #                 attempt += 1
    #                 sleep(1)
    #
    #         if not or_found:
    #             raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'or'元素")
    #
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     self.item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     self.item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     self.item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值70
    #     self.item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         "70",
    #     )
    #     # 点击（
    #     self.item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     self.item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     self.item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     itemname = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[3]'
    #     ).text
    #     # 定位第二行数据
    #     itemcode2 = self.item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[3]'
    #     ).text
    #     self.item.click_ref_button()
    #     assert "材料" in itemname and int(itemcode) < 70 and "材料" in itemcode2
    #     assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_delsuccess3(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="222"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_delsuccess1(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='ywz9q11i-sp3b']//input",
            "//div[@id='x1k7t87i-tvc3']//input",
            "//div[@id='u2tgl5h9-otp1']//input",
            "//div[@id='hpjqsv1m-5607']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='9kwcbp3b-z9da']//input",
            "//div[@id='ioo2843u-6pt1']//input",
            "//div[@id='kzika1fs-vslf']//input",
            "//div[@id='vyacskuk-jdgm']//input",
            "//div[@id='36wkcynw-olw8']//input",
            "//div[@id='7u7zprt5-x3u7']//input",
            "//div[@id='r7g6swm9-olis']//input",
            "//div[@id='ez0xsy8r-wtcm']//input",
            "//div[@id='dolz7gel-9n5q']//input",
            "//div[@id='p5msl36t-vfaz']//input",
            "//div[@id='c78gauwj-5nq8']//input"
        ]
        # 日期的xpath
        date_xpath_list = [
            "//div[@id='2zi9znnj-d0ph']//input",
            "//div[@id='h53h14kg-0kls']//input",
            "//div[@id='onz7o1pq-qqkn']//input",
            "//div[@id='s8kxww7w-dyoj']//input",
            "//div[@id='kn5u70w2-42xf']//input"
        ]

        input_xpath_list1 = [
            "//div[@id='2gqlayrh-vwyr']//input",
            "//div[@id='uqtb82o5-7f7f']//input",
            "//div[@id='x2xfoigm-rdd2']//input",
            "//div[@id='mhj7cxc6-rywr']//input",
            "//div[@id='ze6hpeia-qlcv']//input",
            "//div[@id='8rmn9d4u-ll8o']//input",
            "//div[@id='jwmtz1cs-qxcf']//input",
            "//div[@id='mw9lvgil-ay4b']//input",
            "//div[@id='b42zf3g4-ly6d']//input",
            "//div[@id='9hougeja-f19h']//input",
            "//div[@id='sv7m9mzk-eo1b']//input",
            "//div[@id='euflllc4-91y5']//input",
            "//div[@id='qpydcf68-3n30']//input",
            "//div[@id='cd607kel-iwfp']//input",
            "//div[@id='me9njjkp-e9rg']//input",
            "//div[@id='uw1sjnqs-by95']//input",
            "//div[@id='8czb193p-h4wb']//input"
        ]
        # 日期的xpath
        date_xpath_list1 = [
            "//div[@id='pcceybkb-1zqi']//input",
            "//div[@id='f9nnaus3-q1qr']//input",
            "//div[@id='h21yy3zx-sob7']//input",
            "//div[@id='890pwofe-fsbm']//input",
            "//div[@id='w2b54of4-62z0']//input"
        ]

        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 修改是否可用 否
        self.item.click_button("//div[@id='i24ntrok-sf6n']")
        self.item.click_button('//div[@class="my-list-item"]/span[text()="否"]')

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(date_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list1, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(date_xpath_list1, date_str)
        item_sel = self.item.get_find_element_xpath(
            "//div[@id='m1hs2m05-cwhg']//input"
        ).get_attribute("value")
        print('input_values', input_values)
        print('date_values', date_values)
        print('item_sel', item_sel)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
                len(input_xpath_list) == len(input_values)
                and item_sel == "否"
                and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_select2(self, login_to_item):
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = self.item.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            self.item.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            self.item.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//input')
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        self.item.right_refresh('仓库库位')
        assert len(eles) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_select3(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('工厂代码', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('仓库库位')
        assert all(first_char in text for text in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_select4(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合开头")
        sleep(1)
        self.item.select_input('工厂代码', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('仓库库位')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_select5(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合结尾")
        sleep(1)
        self.item.select_input('工厂代码', last_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('仓库库位')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_clear(self, login_to_item):

        name = "3"
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('工厂代码', name)
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("清除所有筛选条件")
        sleep(1)
        ele = self.item.get_find_element_xpath('//div[div[span[text()=" 工厂代码"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        self.item.right_refresh('仓库库位')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_ctrlIrepeat(self, login_to_item):

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
    def test_warehouselocation_ctrlI(self, login_to_item):

        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        self.item.select_input('工厂代码', '1没有数据添加')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_ctrlM(self, login_to_item):

        self.item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('工厂代码', '1没有数据修改')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        assert not self.item.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_shiftdel(self, login_to_item):
        self.item.right_refresh('仓库库位')
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        sleep(1)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改1')
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据修改12')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
        ele2 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('工厂代码', '1没有数据修改1')
        ele11 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        ele22 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        assert not self.item.has_fail_message()
        self.item.select_input('工厂代码', '1没有数据修改')
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
    def test_warehouselocation_ctrlC(self, login_to_item):
        self.item.right_refresh('仓库库位')
        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = self.item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        self.item.click_button('//div[div[span[text()=" 工厂代码"]]]//input')
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        self.item.right_refresh('仓库库位')
        assert all(before_data in ele for ele in eles)
        assert not self.item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_shift(self, login_to_item):

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
    def test_warehouselocation_ctrls(self, login_to_item):

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

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_warehouselocation_delsuccess(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.click_ref_button()
        sleep(1)
        layout = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        layout_name = "测试布局A"
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
