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
    page.click_button('(//span[text()="物控管理"])[1]')  # 点击物控管理
    page.click_button('(//span[text()="物控基础数据"])[1]')  # 点击物控基础数据
    page.click_button('(//span[text()="供应商信息"])[1]')  # 点击供应商信息
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("供应商信息测试用例")
@pytest.mark.run(order=104)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)

    @allure.story("添加供应商信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialVendors_addfail(self, login_to_item):
        sleep(3)
        # divs = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        # find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        # if len(find_layout) == 0 and len(divs) > 1:
        #     layout = "测试布局A"
        #     self.item.add_layout(layout)
        self.item.click_add_button()
        # 供应商代码xpath
        input_box = self.item.get_find_element_xpath(
            "//div[@id='tx0gv6lt-z2dv']//input"
        )
        # 联系人xpath
        inputname_box = self.item.get_find_element_xpath(
            "//div[@id='e4589osf-fgn3']//input"
        )
        # 电话xpath
        whs_code_box = self.item.get_find_element_xpath(
            "//div[@id='tnkc4719-huz5']//input"
        )
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        whs_code_color = whs_code_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
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

    @allure.story("添加供应商信息信息，只填写供应商代码，不填写联系人，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialVendors_addcodefail(self, login_to_item):
        # driver = login_to_item  # WebDriver 实例
        # item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='tx0gv6lt-z2dv']//input", "text1231"
        )
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='e4589osf-fgn3']//input"
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
    def test_materialVendors_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts("//div[@id='tx0gv6lt-z2dv']//input", "111")
        self.item.enter_texts("//div[@id='e4589osf-fgn3']//input", "111")
        self.item.enter_texts("//div[@id='tnkc4719-huz5']//input", "111")

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
    def test_materialVendors_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts("//div[@id='tx0gv6lt-z2dv']//input", "111")
        self.item.enter_texts("//div[@id='e4589osf-fgn3']//input", "111")
        self.item.enter_texts("//div[@id='tnkc4719-huz5']//input", "111")
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
    def test_materialVendors_delcancel(self, login_to_item):

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
    def test_materialVendors_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts("//div[@id='tx0gv6lt-z2dv']//input", "1测试A")
        self.item.enter_texts("//div[@id='e4589osf-fgn3']//input", "1测试A")
        self.item.enter_texts("//div[@id='tnkc4719-huz5']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert adddata == "1测试A", f"预期数据是1测试A，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("修改供应商代码重复")
    # @pytest.mark.run(order=1)
    def test_materialVendors_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 供应商代码输入111
        self.item.enter_texts("//div[@id='wxryw4ea-71oi']//input", "111")
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

    @allure.story("修改供应商代码成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_editcodesuccess(self, login_to_item):
        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        text = "1测试A5"
        # 供应商代码输入
        self.item.enter_texts(
            "//div[@id='wxryw4ea-71oi']//input", f"{text}"
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
    def test_materialVendors_editcodesuccess2(self, login_to_item):

        # 选中1测试A物料代码
        self.item.click_button('//tr[./td[2][.//span[contains(text(),"1测试A")]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 供应商代码输入
        self.item.enter_texts("//div[@id='wxryw4ea-71oi']//input", "1测试A")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 定位表格内容
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试A"]]]/td[2]'
        ).text
        assert itemdata == "1测试A", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_delsuccess1(self, login_to_item):
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
    def test_materialVendors_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='wxryw4ea-71oi']//input",
            "//div[@id='z99bga8f-59um']//input",
            "//div[@id='b3dmq4at-505f']//input",
            "//div[@id='lpuajgnl-w4bn']//input",
            "//div[@id='tfcztwig-bpyz']//input",
            "//div[@id='pwjnm6g5-r3wi']//input",
            "//div[@id='g05o5ikv-h98g']//input",
            "//div[@id='r05l4zyh-0mkg']//input",
            "//div[@id='vht0i4qg-tohl']//input",
            "//div[@id='q7vbvbvr-m50y']//input",
            "//div[@id='9nja3beq-3vul']//input",
            "//div[@id='qnla7m1x-jp14']//input",
            "//div[@id='98nsjrto-f7v5']//input",
            "//div[@id='muzdhwzt-zk46']//input",
            "//div[@id='h511lvst-ymil']//input",
            "//div[@id='mnr6qddb-byo9']//input",
            "//div[@id='o5t54uds-wpe1']//input",
            "//div[@id='nlaxbubj-sgw3']//input",
        ]
        # 日期的xpath
        date_xpath_list = [
            "//div[@id='mcdabmzy-zwt7']//input",
            "//div[@id='9ypxww95-ui8k']//input",
            "//div[@id='3ilkuaeu-5qs1']//input",
            "//div[@id='a46z78ba-g1le']//input",
            "//div[@id='jwpjthep-ld2y']//input"
        ]

        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(date_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中供应商代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(date_xpath_list, date_str)
        # print('input_values', input_values)
        # print('date_values', date_values)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(input_xpath_list) == len(input_values)
            and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_refreshsuccess(self, login_to_item):

        # 供应商代码筛选框输入111
        self.item.enter_texts(
            '//span[text()=" 供应商代码"]/ancestor::div[2]//input', "111"
        )
        itemtext = self.item.get_find_element_xpath(
            '//span[text()=" 供应商代码"]/ancestor::div[2]//input'
        ).text
        sleep(2)
        self.item.click_ref_button()
        assert itemtext == "", f"预期{itemtext}"
        assert not self.item.has_fail_message()

    @allure.story("查询工厂代码成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="供应商代码" and contains(@optid,"opt_")]')
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
    def test_materialVendors_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="供应商代码" and contains(@optid,"opt_")]')
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

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_delsuccess2(self, login_to_item):

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
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialVendors_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "222"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='tx0gv6lt-z2dv']//input",
            "//div[@id='576xc9w1-puug']//input",
            "//div[@id='b44la7cy-s934']//input",
            "//div[@id='tep1a5t0-szkc']//input",
            "//div[@id='e4589osf-fgn3']//input",
            "//div[@id='tnkc4719-huz5']//input",
            "//div[@id='7y24t1kd-a7wp']//input",
            "//div[@id='wge1mzjn-0ygn']//input",
            "//div[@id='xzv28jlv-t3ly']//input",
            "//div[@id='hvaaakjv-13it']//input",
            "//div[@id='da2kcz0f-x4kg']//input",
            "//div[@id='ct8gwmqk-2rkm']//input",
            "//div[@id='x0wyflt4-b0ii']//input",
            "//div[@id='ilss8dt1-p0zs']//input",
            "//div[@id='yo2m7t94-bhfz']//input",
            "//div[@id='zvb3rv6p-b27n']//input",
            "//div[@id='cnpm0qat-paig']//input",
            "//div[@id='vzaoizo2-m1sp']//input"
        ]
        # 日期的xpath
        date_xpath_list = [
            "//div[@id='hdr7gdia-n70t']//input",
            "//div[@id='zd8khtqf-czzy']//input",
            "//div[@id='kghz1un0-ldz9']//input",
            "//div[@id='bhl7i8jc-lh1o']//input",
            "//div[@id='oee9947k-z6o1']//input"
        ]

        # 编辑输入框的xpath
        input_xpath_list2 = [
            "//div[@id='wxryw4ea-71oi']//input",
            "//div[@id='z99bga8f-59um']//input",
            "//div[@id='b3dmq4at-505f']//input",
            "//div[@id='lpuajgnl-w4bn']//input",
            "//div[@id='tfcztwig-bpyz']//input",
            "//div[@id='pwjnm6g5-r3wi']//input",
            "//div[@id='g05o5ikv-h98g']//input",
            "//div[@id='r05l4zyh-0mkg']//input",
            "//div[@id='vht0i4qg-tohl']//input",
            "//div[@id='q7vbvbvr-m50y']//input",
            "//div[@id='9nja3beq-3vul']//input",
            "//div[@id='qnla7m1x-jp14']//input",
            "//div[@id='98nsjrto-f7v5']//input",
            "//div[@id='muzdhwzt-zk46']//input",
            "//div[@id='h511lvst-ymil']//input",
            "//div[@id='mnr6qddb-byo9']//input",
            "//div[@id='o5t54uds-wpe1']//input",
            "//div[@id='nlaxbubj-sgw3']//input",
        ]
        # 编辑日期的xpath
        date_xpath_list2 = [
            "//div[@id='mcdabmzy-zwt7']//input",
            "//div[@id='9ypxww95-ui8k']//input",
            "//div[@id='3ilkuaeu-5qs1']//input",
            "//div[@id='a46z78ba-g1le']//input",
            "//div[@id='jwpjthep-ld2y']//input"
        ]

        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(date_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        self.item.wait_for_loading_to_disappear()
        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')

        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list2, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(date_xpath_list2, date_str)
        print('input_values', input_values)
        print('date_values', date_values)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(input_xpath_list) == len(input_values)
                and len(date_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialVendors_delsuccess3(self, login_to_item):
        # 定位内容为‘222’的行
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
        layout = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        layout_name = "测试布局A"
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘222’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="222"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
