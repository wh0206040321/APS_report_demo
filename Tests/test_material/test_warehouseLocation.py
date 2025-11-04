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
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0:
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
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        whs_code_color = whs_code_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
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
    def test_item_addcodefail(self, login_to_item):
        # driver = login_to_item  # WebDriver 实例
        # item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='p34nag46-7evf']//input", "text1231"
        )
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='u2tgl5h9-otp1']//input"
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_item_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入工厂代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "111")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "111")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "111")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).text
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert adddata == "111", f"预期数据是111，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_item_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入物料代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "111")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "111")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "111")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        sleep(1)
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
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
        # 输入工厂代码
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "1测试A")
        self.item.enter_texts("//div[@id='ywz9q11i-sp3b']//input", "1测试A")
        self.item.enter_texts("//div[@id='u2tgl5h9-otp1']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert adddata == "1测试A", f"预期数据是1测试A，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("修改工厂代码重复")
    # @pytest.mark.run(order=1)
    def test_item_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 工厂代码输入111
        self.item.enter_texts("//div[@id='2gqlayrh-vwyr']//input", "111")
        self.item.enter_texts("//div[@id='uqtb82o5-7f7f']//input", "111")
        self.item.enter_texts("//div[@id='mhj7cxc6-rywr']//input", "111")
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

    @allure.story("修改工厂代码成功")
    # @pytest.mark.run(order=1)
    def test_item_editcodesuccess(self, login_to_item):
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
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(3)
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]'
        ).text
        assert itemdata == text, f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("把修改后的物料代码改回来")
    # @pytest.mark.run(order=1)
    def test_item_editcodesuccess2(self, login_to_item):

        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 物料代码输入
        self.item.enter_texts("//div[@id='2gqlayrh-vwyr']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert itemdata == "1测试A", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_item_editnamesuccess(self, login_to_item):

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
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
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
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(input_xpath_list) == len(input_values)
            and item_sel == "否"
            and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("筛选刷新成功")
    # @pytest.mark.run(order=1)
    # def test_item_refreshsuccess(self, login_to_item):
    #     filter_results = self.item.filter_method('//span[text()=" 工厂代码"]/ancestor::div[3]//span//span//span')
    #     assert filter_results
    #     assert not self.item.has_fail_message()

    @allure.story("查询工厂代码成功")
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
        item.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[2]'
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
        assert itemcode == "222" and len(itemcode2) == 0
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
        self.item.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[2]'
        )
        sleep(1)
        itemcode = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        )
        # 点击刷新
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess3(self, login_to_item):
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

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess3(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
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
            By.XPATH, '//tr[./td[2][.//span[text()="222"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    # @allure.story("查询物料名字成功")
    # @pytest.mark.run(order=1)
    # def test_item_selectnamesuccess(self, login_to_item):
    #     driver = login_to_item  # WebDriver 实例
    #     item = ItemPage(driver)  # 用 driver 初始化 ItemPage
    #
    #     # 点击查询
    #     item.click_sel_button()
    #     sleep(1)
    #     # 定位名称输入框
    #     element_to_double_click = driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "M1",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行是否为M1
    #     itemcode = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[3]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[3]',
    #     )
    #     assert itemcode == "M1" and len(itemcode2) == 0
    #     assert not item.has_fail_message()

    # @allure.story("查询物料优先度>60")
    # @pytest.mark.run(order=1)
    # def test_item_selectsuccess1(self, login_to_item):
    #     driver = login_to_item  # WebDriver 实例
    #     item = ItemPage(driver)  # 用 driver 初始化 ItemPage
    #
    #     # 点击查询
    #     item.click_sel_button()
    #     sleep(1)
    #     # 定位名称输入框
    #     element_to_double_click = driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料优先度
    #     item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "60",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     # 定位第二行数据
    #     itemcode2 = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[6]'
    #     ).text
    #     assert int(itemcode) > 60 and int(itemcode2) > 60
    #     assert not item.has_fail_message()

    # @allure.story("查询物料名称包含材料并且物料优先度>70")
    # @pytest.mark.run(order=1)
    # def test_item_selectsuccess2(self, login_to_item):
    #     driver = login_to_item  # WebDriver 实例
    #     item = ItemPage(driver)  # 用 driver 初始化 ItemPage
    #
    #     # 点击查询
    #     item.click_sel_button()
    #     sleep(1)
    #
    #     # 定位名称输入框
    #     element_to_double_click = driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "材料",
    #     )
    #
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     double_click = driver.find_element(
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
    #         and_element = WebDriverWait(driver, 2).until(
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
    #                 and_element = WebDriverWait(driver, 2).until(
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
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         "70",
    #     )
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     itemname = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[3]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[10]',
    #     )
    #     # 判断第一行物料优先度>70 并且 物料名称为材料B 并且第二行没有数据
    #     assert int(itemcode) > 70 and itemname == "材料B" and len(itemcode2) == 0
    #     assert not item.has_fail_message()

    # @allure.story("查询物料名称包含材料或物料优先度>70")
    # @pytest.mark.run(order=1)
    # def test_item_selectsuccess3(self, login_to_item):
    #     driver = login_to_item  # WebDriver 实例
    #     item = ItemPage(driver)  # 用 driver 初始化 ItemPage
    #
    #     # 点击查询
    #     item.click_sel_button()
    #     sleep(1)
    #
    #     # 定位名称输入框
    #     element_to_double_click = driver.find_element(
    #         By.XPATH,
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
    #     )
    #     # 创建一个 ActionChains 对象
    #     actions = ActionChains(driver)
    #     # 双击命令
    #     actions.double_click(element_to_double_click).perform()
    #     sleep(1)
    #     # 点击物料名称
    #     item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "材料",
    #     )
    #
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #     double_click = driver.find_element(
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
    #         and_element = WebDriverWait(driver, 2).until(
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
    #                 or_element = WebDriverWait(driver, 2).until(
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
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值70
    #     item.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         "70",
    #     )
    #     # 点击（
    #     item.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     item.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     item.click_button(
    #         '(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[3]'
    #     )
    #     sleep(1)
    #     # 定位第一行物料优先度
    #     itemcode = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[6]'
    #     ).text
    #     itemname = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][1]/td[3]'
    #     ).text
    #     # 定位第二行数据
    #     itemcode2 = item.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")][2]/td[3]'
    #     ).text
    #     assert "材料" in itemname and int(itemcode) < 70 and "材料" in itemcode2
    #     assert not item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess(self, login_to_item):

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

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess1(self, login_to_item):

        # 定位内容为‘1测试A’的行
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
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
            By.XPATH, '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_item_add_success(self, login_to_item):
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

        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 修改是否可用 否
        self.item.click_button("//div[@id='i24ntrok-sf6n']")
        self.item.click_button('//li[text()="否"]')

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(date_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[4]')
        sleep(1)
        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(date_xpath_list, date_str)
        item_sel = self.item.get_find_element_xpath(
            "//div[@id='m1hs2m05-cwhg']//span"
        ).text
        print('input_values', input_values)
        print('date_values', date_values)
        print('item_sel', item_sel)
        sleep(1)
        assert (
                len(input_xpath_list) == len(input_values)
                and item_sel == "否"
                and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess(self, login_to_item):
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
        layout_name = "测试布局A"
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
