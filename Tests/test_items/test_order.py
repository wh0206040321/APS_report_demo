import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.order_page import OrderPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_order():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        # 初始化 driver
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
        page.click_button('(//span[text()="计划管理"])[1]')  # 点击计划管理
        page.click_button('(//span[text()="计划业务数据"])[1]')  # 点击计划业务数据
        page.click_button('(//span[text()="制造订单"])[1]')  # 点击制造订单
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("制造订单表测试用例")
@pytest.mark.run(order=15)
class TestOrderPage:
    @allure.story("添加制造订单信息 不填写数据点击确认 不允许提交 并且添加了一新布局设置成默认启动布局")
    # @pytest.mark.run(order=1)
    def test_order_addfail(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        layout = "测试布局A"
        order.add_layout(layout)
        # 获取布局名称的文本元素
        name = order.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        sleep(2)
        order.click_add_button()
        # 制造订单代码xpath
        input_box = order.get_find_element_xpath(
            '(//label[text()="订单代码"])[1]/parent::div//input'
        )
        # 物品代码输入框
        inputitem_box = order.get_find_element_xpath(
            '(//label[text()="物料"])[1]/parent::div//input'
        )
        # 交货期输入框
        inputdate_box = order.get_find_element_xpath(
            '(//label[text()="交货期"])[1]/parent::div//input'
        )

        order.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        border_color = input_box.value_of_css_property("border-color")
        borderitem_color = inputitem_box.value_of_css_property("border-color")
        inputdate_box = inputdate_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color and borderitem_color == expected_color and inputdate_box == expected_color and name == layout
        assert not order.has_fail_message()

    @allure.story("添加制造订单信息，填写制造订单和物料，不填写交货期，不允许提交，并且增加一个判断上一个用例默认启动布局是否成功")
    # @pytest.mark.run(order=2)
    def test_order_addcodefail(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        layout = "测试布局A"
        div = order.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).get_attribute("class")
        order.click_add_button()
        # 填写订单代码
        order.enter_texts(
            '(//label[text()="订单代码"])[1]/parent::div//input', "text1231"
        )

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        order.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(3)
        # 交货期输入框
        inputdate_box = order.get_find_element_xpath(
            '(//label[text()="交货期"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        border_color = inputdate_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        # 判断上一步默认启动该布局成功
        assert (
            border_color == expected_color and div == "tabsDivItem tabsDivActive"
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not order.has_fail_message()

    @allure.story(
        "添加制造订单信息，只填写制造订单名称和交货期，不填写物料，不允许提交"
    )
    # @pytest.mark.run(order=3)
    def test_order_addnamefail(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()
        # 填写订单代码
        order.enter_texts(
            '(//label[text()="订单代码"])[1]/parent::div//input', "text1231"
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 点击确定
        order.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(2)
        input_box = order.get_find_element_xpath(
            '(//label[text()="物料"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not order.has_fail_message()

    @allure.story(
        "添加制造订单信息，只填写制造订单名称和交货期和物料，不填写计划数量，不允许提交"
    )
    # @pytest.mark.run(order=3)
    def test_order_addnumfail(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()
        # 填写订单代码
        order.enter_texts(
            '(//label[text()="订单代码"])[1]/parent::div//input', "text1231"
        )

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 清除计划数量
        num = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)

        # 点击确定
        order.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(2)
        input_box = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div/div[1]/div'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not order.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_order_addnum(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()  # 检查点击添加

        # 计划数量数字框输入文字字母符号数字
        num = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)
        order.enter_texts(
            '(//label[text()="计划数量"])[1]/parent::div//input', "e1文字abc。？~1_2+=3"
        )

        # 获取计划数量数字框
        ordernum = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        ).get_attribute("value")
        assert ordernum == "1123", f"预期{ordernum}"
        assert not order.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_order_addsel(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()  # 检查点击添加

        # 订单区分下拉框
        order.click_button(
            '(//label[text()="订单区分"])[1]/parent::div//input[@class="ivu-select-input"]'
        )
        # 订单区分选择 补充
        order.click_button('//li[text()="补充"]')
        # 获取下拉框
        ordersel = order.get_find_element_xpath(
            '(//label[text()="订单区分"])[1]/parent::div//input['
            '@class="ivu-select-input"]'
        ).get_attribute("value")
        assert ordersel == "补充", f"预期{ordersel}"
        assert not order.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_order_textverify(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()  # 检查点击添加
        name = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        # 填写订单代码
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 计划数量
        num = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)
        order.enter_texts('(//label[text()="计划数量"])[1]/parent::div//input', name)

        # 点击确定
        order.click_confirm_button()
        adddata = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        num_ = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[10]'
        ).text
        assert adddata == name and num_ == '9999999999'
        assert not order.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_order_addsuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()  # 检查点击添加
        name = "111"
        # 填写订单代码
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 计划数量
        num = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)
        order.enter_texts('(//label[text()="计划数量"])[1]/parent::div//input', "200")

        # 点击确定
        order.click_confirm_button()
        adddata = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name
        assert not order.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_order_addrepeat(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        order.click_add_button()  # 检查点击添加
        name = "111"
        # 填写订单代码
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 点击确定
        order.click_confirm_button()

        # 获取重复弹窗文字
        error_popup = order.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not order.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_order_delcancel(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "111"
        # 定位内容为‘111’的行
        order.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        order.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        order.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        orderdata = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert orderdata == name, f"预期{orderdata}"
        assert not order.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_order_addsuccess1(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"
        order.click_add_button()  # 检查点击添加
        # 填写订单代码
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)

        # 物料
        random_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{random_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 填写交货期
        order.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        order.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        order.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )

        # 点击确定
        order.click_confirm_button()
        adddata = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name
        assert not order.has_fail_message()

    @allure.story("修改制造订单代码重复")
    # @pytest.mark.run(order=1)
    def test_order_editrepeat(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"
        # 选中1测试A制造订单代码
        order.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        order.click_edi_button()

        # 制造订单代码输入111
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', "111")
        # 点击确定
        order.click_confirm_button()
        # 获取重复弹窗文字
        error_popup = order.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not order.has_fail_message()

    @allure.story("修改制造订单代码成功")
    # @pytest.mark.run(order=1)
    def test_order_editcodesuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"
        # 选中1测试A制造订单代码
        order.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        order.click_edi_button()

        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        sleep(1)
        # 制造订单代码输入
        order.enter_texts(
            '(//label[text()="订单代码"])[1]/parent::div//input', f"{text}"
        )
        # 点击确定
        order.click_confirm_button()
        sleep(1)
        # 定位表格内容
        orderdata = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]'
        ).text
        assert orderdata == text, f"预期{orderdata}"
        assert not order.has_fail_message()

    @allure.story("把修改后的制造订单代码改回来")
    # @pytest.mark.run(order=1)
    def test_order_editcodesuccess2(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"
        # 选中1B制造订单代码
        order.click_button(f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]')
        # 点击修改按钮
        order.click_edi_button()
        # 制造订单代码输入
        order.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)
        # 点击确定
        order.click_confirm_button()
        # 定位表格内容
        orderdata = order.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        assert orderdata == name, f"预期{orderdata}"
        assert not order.has_fail_message()

    @allure.story("修改物料名称，计划数量成功")
    # @pytest.mark.run(order=1)
    def test_order_editnamesuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"
        # 选中制造订单代码
        order.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        order.click_edi_button()

        # 物料
        randomitem_int = random.randint(1, 4)
        order.click_button('//label[text()="物料"]/parent::div/div//i')
        order.click_button(
            f'(//div[@class="vxe-grid--table-container"]//tr[{randomitem_int}]/td[2])[2]'
        )
        order.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        edititem = order.get_find_element_xpath(
            '(//label[text()="物料"])[1]/parent::div//input'
        ).get_attribute("value")

        # 计划数量数字框输入文字字母符号数字
        random_int = random.randint(1, 99)
        num = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)
        order.enter_texts(
            '(//label[text()="计划数量"])[1]/parent::div//input', f"{random_int}"
        )
        editnum = order.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        ).get_attribute("value")

        # 点击确定
        order.click_confirm_button()
        # 定位表格内容
        orderitem = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]/ancestor::tr/td[5]/div'
        ).text
        ordernum = order.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]/ancestor::tr/td[10]/div'
        ).text
        assert orderitem == edititem and ordernum == editnum
        assert not order.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_order_refreshsuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        # 制造订单代码筛选框输入123
        order.enter_texts(
            '//p[text()="订单代码"]/ancestor::div[2]//input', "123"
        )
        order.click_ref_button()
        ordertext = order.get_find_element_xpath(
            '//p[text()="订单代码"]/ancestor::div[2]//input'
        ).text
        assert ordertext == "", f"预期{ordertext}"
        assert not order.has_fail_message()

    @allure.story("查询制造订单代码成功")
    # @pytest.mark.run(order=1)
    def test_order_selectcodesuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1测试A"

        # 点击查询
        order.click_sel_button()
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
        # 点击制造订单代码
        order.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        order.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        order.click_select_button()
        # 定位第一行是否为1A
        ordercode = order.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        ordercode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert ordercode == name and len(ordercode2) == 0
        assert not order.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_order_selectnodatasuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 ItemPage

        # 点击查询
        order.click_sel_button()
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
        # 点击物料代码
        order.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        order.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        order.click_select_button()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        assert len(itemcode) == 0
        assert not order.has_fail_message()

    @allure.story("查询物订单代码包含A成功")
    # @pytest.mark.run(order=1)
    def test_order_selectnamesuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "A"
        # 点击查询
        order.click_sel_button()
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
        # 点击制造订单名称
        order.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        order.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        order.click_select_button()
        eles = order.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[2]')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not order.has_fail_message()

    @allure.story("查询订单代码包含1或计划数量>=100")
    # @pytest.mark.run(order=1)
    def test_order_selectsuccess3(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage

        name = "1"
        num = 100
        # 点击查询
        order.click_sel_button()
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
        # 点击订单代码
        order.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        order.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        order.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        order.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)
        double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
        )
        # 双击命令
        sleep(1)
        actions.double_click(double_click).perform()
        # 定义or元素的XPath
        or_xpath = '//div[text()="or" and contains(@optid,"opt_")]'

        try:
            # 首先尝试直接查找并点击or元素
            and_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, or_xpath))
            )
            and_element.click()
        except:
            # 如果直接查找失败，进入循环双击操作
            max_attempts = 5
            attempt = 0
            or_found = False

            while attempt < max_attempts and not or_found:
                try:
                    # 执行双击操作
                    actions.double_click(double_click).perform()
                    sleep(1)

                    # 再次尝试查找or元素
                    or_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, or_xpath))
                    )
                    or_element.click()
                    or_found = True
                except:
                    attempt += 1
                    sleep(1)

            if not or_found:
                raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'or'元素")

        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        order.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击计划数量
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        order.click_button('//div[text()="计划数量" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        order.click_button('//div[text()="≥" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值0
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        order.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        order.click_select_button()
        # 获取目标表格第2个 vxe 表格中的所有数据行
        xpath_rows = '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")]'

        # 先拿到总行数
        base_rows = driver.find_elements(By.XPATH, xpath_rows)
        total = len(base_rows)

        valid_count = 0
        for idx in range(total):
            try:
                # 每次都按索引重新定位这一行
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td2 = tds[1].text.strip()
                td10_raw = tds[9].text.strip()
                td10_raw = int(td10_raw) if td10_raw else 0

                assert name in td2 or td10_raw >= num, f"第 {idx + 1} 行不符合：td2={td2}, td8={td10_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td2 = tds[1].text.strip()
                td10_raw = tds[9].text.strip()
                td10_raw = int(td10_raw) if td10_raw else 0

                assert name in td2 or td10_raw >= num, f"第 {idx + 1} 行不符合：td2={td2}, td8={td10_raw}"
                valid_count += 1
        assert not order.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("查询计划数量>100")
    # @pytest.mark.run(order=1)
    def test_order_selectsuccess1(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        num = 100
        # 点击查询
        order.click_sel_button()
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
        # 点击制造订单优先度
        order.click_button('//div[text()="计划数量" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        order.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            num,
        )
        sleep(1)

        # 点击确认
        order.click_select_button()
        eles = order.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[10]')
        assert len(eles) > 0
        assert all(int(ele) > num for ele in eles)
        assert not order.has_fail_message()

    @allure.story("查询订单代码包含1A并且计划数量>100")
    # @pytest.mark.run(order=1)
    def test_order_selectsuccess2(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        name = "1"
        num = 100
        # 点击查询
        order.click_sel_button()
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
        # 点击制造订单名称
        order.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        order.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        order.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        order.click_button('//div[text()=")" and contains(@optid,"opt_")]')
        sleep(1)

        double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
        )
        # 双击命令
        actions.double_click(double_click).perform()
        # 定义and元素的XPath
        and_xpath = '//div[text()="and" and contains(@optid,"opt_")]'

        try:
            # 首先尝试直接查找并点击and元素
            and_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, and_xpath))
            )
            and_element.click()
        except:
            # 如果直接查找失败，进入循环双击操作
            max_attempts = 5
            attempt = 0
            and_found = False

            while attempt < max_attempts and not and_found:
                try:
                    # 执行双击操作
                    actions.double_click(double_click).perform()
                    sleep(1)

                    # 再次尝试查找and元素
                    and_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, and_xpath))
                    )
                    and_element.click()
                    and_found = True
                except:
                    attempt += 1
                    sleep(1)

            if not and_found:
                raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'and'元素")

        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        order.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击这种数量
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        order.click_button('//div[text()="计划数量" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        order.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        order.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        order.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        order.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        order.click_select_button()
        eles1 = order.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[10]')
        eles2 = order.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[2]')
        assert len(eles1) > 0 and len(eles2) > 0
        assert all(int(ele) > num for ele in eles1) and all(name in ele for ele in eles2)
        assert not order.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_order_addall(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        order.click_add_button()
        custom_xpath_list = [
            f'//label[text()="自定义字符{i}"]/following-sibling::div//input'
            for i in range(1, 51)
        ]
        text_list = [
            '//label[text()="订单代码"]/following-sibling::div//input',
            '//label[text()="关联订单组"]/following-sibling::div//input',
            '//label[text()="备注"]/following-sibling::div//input',
        ]
        text_list.extend(custom_xpath_list)
        adds.batch_modify_input(text_list, input_value)

        value_bos = '//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3]'
        spe_xpath_list = [
            f'//label[text()="生产特征{i}"]/following-sibling::div//i'
            for i in range(1, 11)
        ]
        box_list = [
            '//label[text()="物料"]/following-sibling::div//i',
            '//label[text()="BASE物料"]/following-sibling::div//i',
            '//label[text()="客户"]/following-sibling::div//i',
            '//label[text()="一对一关联指定料号"]/following-sibling::div//i',
            '//label[text()="后订单"]/following-sibling::div//i',
            '//label[text()="用户指定资源"]/following-sibling::div//i',
            '//label[text()="首工序资源"]/following-sibling::div//i',
        ]
        box_list.extend(spe_xpath_list)
        adds.batch_modify_dialog_box(box_list, value_bos)

        select_list = [
            {"select": '//label[text()="订单区分"]/following-sibling::div//i', "value": '//li[text()="补充"]'},
            {"select": '//label[text()="显示颜色"]/following-sibling::div//i',
             "value": '//span[text()="RGB(128,128,255)"]'},
            {"select": '//label[text()="分派方向"]/following-sibling::div//i', "value": '//li[text()="遵从优先度"]'},
            {"select": '//label[text()="订单状态"]/following-sibling::div//i', "value": '//li[text()="开始生产"]'},
        ]
        adds.batch_modify_select_input(select_list)

        input_num_value = '1'
        num_xpath_list1 = [
            f'//label[text()="数值特征{i}"]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        num_xpath_list2 = [
            f'//label[text()="自定义数字{i}"]/following-sibling::div//input'
            for i in range(1, 51)
        ]

        num_list = [
            '//label[text()="计划数量"]/following-sibling::div//input',
            '//label[text()="用户指定订单数量固定级别"]/following-sibling::div//input',
            '//label[text()="优先度"]/following-sibling::div//input',
            '//label[text()="显示顺序"]/following-sibling::div//input',
            '//label[text()="制造效率"]/following-sibling::div//input',
            '//label[text()="实绩数量"]/following-sibling::div//input',
            '//label[text()="系统内部资源计划顺序"]/following-sibling::div//input',
            '//label[text()="用户调整计划顺序"]/following-sibling::div//input',
        ]
        num_list.extend(num_xpath_list1 + num_xpath_list2)
        adds.batch_modify_input(num_list, input_num_value)

        time_xpath_list = [
            f'//label[text()="自定义日期{i}"]/following-sibling::div//input'
            for i in range(1, 21)
        ]
        time_list = [
            '//label[text()="订货时间"]/following-sibling::div//input',
            '//label[text()="最早开始时间"]/following-sibling::div//input',
            '//label[text()="交货期"]/following-sibling::div//input',
            '//label[text()="实绩结束时间"]/following-sibling::div//input',
        ]
        time_list.extend(time_xpath_list)
        adds.batch_order_time_input(time_list)

        box_input_list = [xpath.replace("//i", "//input") for xpath in box_list]
        select_input_list = [item["select"].replace("//i", "//input") for item in select_list]

        checked = order.get_find_element_xpath('//label[text()="非分派对象标志"]/following-sibling::div//label/span')
        if checked.get_attribute("class") == "ivu-checkbox":
            checked.click()
        before_checked = order.get_find_element_xpath(
            '//label[text()="非分派对象标志"]/following-sibling::div//label/span').get_attribute("class")

        all_value = text_list + box_input_list + select_input_list + num_list + time_list
        len_num = len(all_value)
        before_all_value = adds.batch_acquisition_input(all_value)
        order.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')
        sleep(1)
        driver.refresh()
        sleep(3)
        num = adds.go_settings_page()
        sleep(2)
        order.enter_texts(
            '//p[text()="订单代码"]/ancestor::div[2]//input', input_value
        )
        sleep(1)
        order.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{input_value}"]]')
        sleep(1)
        order.click_edi_button()
        sleep(1)
        after_all_value = adds.batch_acquisition_input(all_value)
        after_checked = order.get_find_element_xpath(
            '//label[text()="非分派对象标志"]/following-sibling::div//label/span').get_attribute("class")
        username = order.get_find_element_xpath('//label[text()="更新者"]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = order.get_find_element_xpath(
            '//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 17) and before_checked == after_checked
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not order.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_order_delsuccess(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        layout = "测试布局A"

        value = ['111', '1测试A', '11测试全部数据', '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        order.del_all(value)
        orderdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        order.del_layout(layout)
        sleep(5)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in orderdata)
        assert 0 == len(after_layout)
        assert not order.has_fail_message()

    @allure.story("计划需求增删查改")
    # @pytest.mark.run(order=1)
    def test_order_salesorder(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        list_name = ['11计划需求', '11计划需求测试']
        after_name = '11修改计划需求'
        order.click_button('//div[text()=" 制造订单 "]')
        order.click_button('//div[div[text()=" 制造订单 "]]/span')
        order.click_order_page('计划需求')
        add1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            order.add_order_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            order.add_order_data(list_name[0])
            ele0 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            order.edit_order_data(list_name[0], after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        order.select_order_data(after_name)
        speccode = order.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        order.del_order_data(after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        # 点击获取需求不报错
        order.click_button('//p[text()="获取需求"]')
        order.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = order.get_find_message()
        assert message == "成功"

        ele = order.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not order.has_fail_message()

    @allure.story("盘点库存增删查改")
    # @pytest.mark.run(order=1)
    def test_order_inventorycount(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        list_name = ['11盘点库存', '11盘点库存测试']
        after_name = '11修改盘点库存'
        order.click_button('//div[text()=" 制造订单 "]')
        order.click_button('//div[div[text()=" 制造订单 "]]/span')
        order.click_order_page('盘点库存')
        add1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            order.add_order_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            order.add_order_data(list_name[0])
            ele0 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            order.edit_order_data(list_name[0], after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        order.select_order_data(after_name)
        speccode = order.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        order.del_order_data(after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = order.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not order.has_fail_message()

    @allure.story("调整库存增删查改")
    # @pytest.mark.run(order=1)
    def test_order_adjustinventory(self, login_to_order):
        driver = login_to_order  # WebDriver 实例
        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        list_name = ['11调整库存', '11调整库存测试']
        after_name = '11修改调整库存'
        order.click_button('//div[text()=" 制造订单 "]')
        order.click_button('//div[div[text()=" 制造订单 "]]/span')
        order.click_order_page('调整库存')
        add1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            order.add_order_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            order.add_order_data(list_name[0])
            ele0 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            order.edit_order_data(list_name[0], after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        order.select_order_data(after_name)
        speccode = order.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        order.del_order_data(after_name)
        ele = order.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = order.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not order.has_fail_message()
