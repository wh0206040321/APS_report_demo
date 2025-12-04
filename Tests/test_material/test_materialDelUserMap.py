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
    page.click_button('(//span[text()="用户与物料员对照"])[1]')  # 点击物品
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("用户与物料员测试用例")
@pytest.mark.run(order=110)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)

    @allure.story("添加用户信息 不填写物料员点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_addfail(self, login_to_item):
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
        self.item.click_add_button()
        # 物料员代码xpath
        input_box = self.item.get_find_element_xpath(
            "//div[@id='rpfclioo-7p50']//input"
        )
        # 物料员名称xpath
        inputname_box = self.item.get_find_element_xpath(
            "//div[@id='04m2qyfz-z28h']//input"
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

    @allure.story("添加物料员信息，只填写用户，不填写物料员，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialDelUserMap_addcodefail(self, login_to_item):

        self.item.click_add_button()
        self.item.click_button("//div[@id='rpfclioo-7p50']//i")
        sleep(2)
        self.item.click_button('(//span[text()="钟锦鹏"])[1]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        input_box = self.item.get_find_element_xpath(
            "//div[@id='04m2qyfz-z28h']//input"
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
    def test_materialDelUserMap_addsuccess(self, login_to_item):

        self.item.click_add_button()
        self.item.enter_texts(
            "//div[@id='lo2km34z-5dbg']//input", "666"
        )
        self.item.click_button("//div[@id='rpfclioo-7p50']//i")
        sleep(2)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')

        self.item.click_button("//div[@id='04m2qyfz-z28h']//i")
        sleep(2)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        ele1 = self.item.get_find_element_xpath(
            "//div[@id='rpfclioo-7p50']//input"
        ).get_attribute("value")
        ele2 = self.item.get_find_element_xpath(
            "//div[@id='04m2qyfz-z28h']//input"
        ).get_attribute("value")
        ele3 = self.item.get_find_element_xpath(
            "//div[@id='lo2km34z-5dbg']//input"
        ).get_attribute("value")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{ele1}"]]]/td[2]'
        ).text
        adddata2 = self.item.get_find_element_xpath(
            f'//tr[./td[3][.//span[text()="{ele2}"]]]/td[3]'
        ).text
        adddata3 = self.item.get_find_element_xpath(
            '//tr[./td[4][.//span[text()="666"]]]/td[4]'
        ).text

        assert adddata == ele1 and adddata2 == ele2 and adddata3 == ele3
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入供应商代码
        self.item.enter_texts(
            "//div[@id='lo2km34z-5dbg']//input", "666"
        )
        self.item.click_button("//div[@id='rpfclioo-7p50']//i")
        sleep(2)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')

        self.item.click_button("//div[@id='04m2qyfz-z28h']//i")
        sleep(2)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(3)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_delcancel(self, login_to_item):

        # 定位内容为‘111’的行
        ele = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1])[1]/td[2]'
        ).text
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[1]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1])[1]/td[2]'
        ).text
        assert itemdata == ele, f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_addsuccess1(self, login_to_item):
        self.item.click_add_button()
        self.item.enter_texts("//div[@id='rpfclioo-7p50']//input", "zhong11")
        self.item.enter_texts("//div[@id='04m2qyfz-z28h']//input", "1")
        self.item.enter_texts("//div[@id='lo2km34z-5dbg']//input", "777")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        adddata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="zhong11"]]]/td[2]'
        ).text
        adddata2 = self.item.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="1"]]]/td[3]'
        ).text
        adddata3 = self.item.get_find_element_xpath(
            '//tr[./td[4][.//span[text()="777"]]]/td[4]'
        ).text

        assert adddata == "zhong11" and adddata2 == "1" and adddata3 == "777", f"预期数据是111，实际得到{adddata}"
        assert not self.item.has_fail_message()

    @allure.story("修改用户名重复")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="zhong11"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        # 用户弹窗
        self.item.click_button("//div[@id='2pj1qda7-bju3']//i")
        self.item.wait_for_loading_to_disappear()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        self.item.click_button("//div[@id='kwy45no3-x5iq']//i")
        self.item.wait_for_loading_to_disappear()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1])[2]/td[2]')
        # 物料员弹窗
        # self.item.click_button("//div[@id='kwy45no3-x5iq']//i")
        # sleep(2)
        # self.item.click_button('(//span[text()="111"])[1]')
        # self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')

        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(2)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_delsuccess1(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[4][.//span[text()="666"]]]/td[2]')
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
            By.XPATH, '//tr[./td[4][.//span[text()="666"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"

        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='2pj1qda7-bju3']//input",
            "//div[@id='kwy45no3-x5iq']//input",
            "//div[@id='r6gimbdo-vafa']//input"
        ]

        # 选中工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="zhong11"]]]/td[2]')
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
        assert (
            len(input_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("筛选")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_refreshsuccess(self, login_to_item):
        self.item.wait_for_loading_to_disappear()
        sleep(1)
        # 用户筛选框输入111
        self.item.enter_texts(
            '//span[text()=" 用户"]/ancestor::div[3]//input', "111"
        )
        self.item.click_ref_button()
        itemtext = self.item.get_find_element_xpath(
            '//span[text()=" 用户"]/ancestor::div[3]//input'
        ).text
        assert itemtext == "", f"预期{itemtext}"
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "test111"
        # 输入框的xpath
        input_xpath_list = [
            "//div[@id='rpfclioo-7p50']//input",
            "//div[@id='04m2qyfz-z28h']//input",
            "//div[@id='lo2km34z-5dbg']//input"
        ]
        input_xpath_list2 = [
            "//div[@id='2pj1qda7-bju3']//input",
            "//div[@id='kwy45no3-x5iq']//input",
            "//div[@id='r6gimbdo-vafa']//input"
        ]
        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(input_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中物料员代码
        self.item.click_button('//tr[./td[2][.//span[text()="test111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(input_xpath_list2, text_str)
        print('input_values', input_values)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(input_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询物料员代码成功")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_selectcodesuccess(self, login_to_item):
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
        # 点击用户
        item.click_button('//div[text()="用户" and contains(@optid,"opt_")]')
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
            "test111",
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
        assert itemcode == "test111" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_materialDelUserMap_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="用户" and contains(@optid,"opt_")]')
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
    def test_materialDelUserMap_delsuccess3(self, login_to_item):
        # 定位内容为‘test111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="test111"]]]/td[2]')
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
        # 定位内容为‘test111’的行
        self.item.wait_for_loading_to_disappear()
        self.item.click_button('//tr[td[4][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.item.wait_for_loading_to_disappear()
        itemdata1 = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="test111"]]]/td[2]'
        )
        itemdata2 = self.driver.find_elements(
            By.XPATH, '//tr[td[4][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata1) == 0 and len(itemdata2) == 0
        assert not self.item.has_fail_message()
