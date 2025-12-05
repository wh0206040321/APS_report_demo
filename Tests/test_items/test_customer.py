import logging
import random
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.customer_page import CustomerPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from selenium.webdriver.common.keys import Keys


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_customer():
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
        page.click_button('(//span[text()="计划基础数据"])[1]')  # 点击计划基础数据
        page.click_button('(//span[text()="客户"])[1]')  # 点击客户
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("客户表测试用例")
@pytest.mark.run(order=3)
class TestCustomerPage:
    @allure.story("添加客户信息 不填写数据点击确认 不允许提交，添加测试布局")
    # @pytest.mark.run(order=1)
    def test_customer_addfail(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        layout = "测试布局A"
        customer.add_layout(layout)
        # 获取布局名称的文本元素
        name = customer.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        customer.click_add_button()
        # 客户代码xpath
        input_box = customer.get_find_element_xpath(
            '(//label[text()="客户代码"])[1]/parent::div//input'
        )
        # 客户名称xpath
        inputname_box = customer.get_find_element_xpath(
            '(//label[text()="客户名称"])[1]/parent::div//input'
        )
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值

        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert name == layout
        assert not customer.has_fail_message()

    @allure.story("添加客户信息，只填写客户代码，不填写客户名称，不允许提交")
    # @pytest.mark.run(order=2)
    def test_customer_addcodefail(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        customer.click_add_button()
        customer.enter_texts(
            '(//label[text()="客户代码"])[1]/parent::div//input', "text1231"
        )
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = customer.get_find_element_xpath(
            '(//label[text()="客户名称"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not customer.has_fail_message()

    @allure.story("添加客户信息，只填写客户名称，不填写客户代码，不允许提交")
    # @pytest.mark.run(order=3)
    def test_customer_addnamefail(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        customer.click_add_button()
        customer.enter_texts(
            '(//label[text()="客户名称"])[1]/parent::div//input', "text1231"
        )

        # 点击确定
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = customer.get_find_element_xpath(
            '(//label[text()="客户代码"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not customer.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_customer_addnum(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        customer.click_add_button()  # 检查点击添加
        ele = customer.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        # 显示顺序输入文字字母符号数字
        customer.enter_texts(
            '(//label[text()="显示顺序"])[1]/parent::div//input', "e1文字abc。+？~1._2+3"
        )
        sleep(1)
        # 获取显示顺序框
        customernum = customer.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        ).get_attribute("value")
        assert customernum == "1123", f"预期{customernum}"
        assert not customer.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_customer_addsel(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        customer.click_add_button()  # 检查点击添加
        # 显示颜色下拉框
        customer.click_button(
            '//div[label[text()="显示颜色"]]//i'
        )
        # 选择颜色4
        customer.click_button('//div[@class="d-flex"]/span[text()="4"]')
        # 获取下拉框数值
        customersel = customer.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text
        assert customersel == "4", f"预期{customersel}"
        assert not customer.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_customer_textverify(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        customer.add_test_data(name)
        customer.enter_texts('//label[text()="显示顺序"]/parent::div//input', name)
        # 点击确定
        customer.click_confirm_button()
        adddata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        num_ = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]'
        ).text
        assert adddata == name and num_ == '9999999999', f"预期数据是{name}，实际得到{adddata}"
        assert not customer.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_customer_addsuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111"
        customer.add_test_data(name)
        # 点击确定
        customer.click_confirm_button()
        adddata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是{name}，实际得到{adddata}"
        assert not customer.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_customer_addrepeat(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111"
        customer.add_test_data(name)
        # 点击确定
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = customer.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not customer.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_customer_delcancel(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111"
        # 定位内容为‘111’的行
        customer.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        customer.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        customer.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        customerdata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert customerdata == name, f"预期{customerdata}"
        assert not customer.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_customer_addsuccess1(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "1测试A"
        customer.add_test_data(name)
        # 点击确定
        customer.click_confirm_button()
        adddata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是1测试A，实际得到{adddata}"
        assert not customer.has_fail_message()

    @allure.story("修改客户代码重复")
    # @pytest.mark.run(order=1)
    def test_customer_editrepeat(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "1测试A"
        # 选中1测试A客户代码
        customer.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        customer.click_edi_button()
        # 客户代码输入111
        customer.enter_texts('(//label[text()="客户代码"])[1]/parent::div//input', "111")
        # 点击确定
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = customer.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not customer.has_fail_message()

    @allure.story("修改客户代码成功")
    # @pytest.mark.run(order=1)
    def test_customer_editcodesuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "1测试A"
        # 选中1测试A客户代码
        customer.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        customer.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 客户代码输入
        customer.enter_texts(
            '(//label[text()="客户代码"])[1]/parent::div//input', f"{text}"
        )
        # 点击确定
        customer.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        customer.wait_for_loading_to_disappear()
        # 定位表格内容
        customerdata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]'
        ).text
        assert customerdata == text, f"预期{customerdata}"
        assert not customer.has_fail_message()

    @allure.story("把修改后的客户代码改回来")
    # @pytest.mark.run(order=1)
    def test_customer_editcodesuccess2(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "1测试A"
        # 选中1测试A客户代码
        customer.click_button(f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]')
        # 点击修改按钮
        customer.click_edi_button()
        # 客户代码输入
        customer.enter_texts('(//label[text()="客户代码"])[1]/parent::div//input', name)
        # 点击确定
        customer.click_confirm_button()
        # 定位表格内容
        customerdata = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert customerdata == name, f"预期{customerdata}"
        assert not customer.has_fail_message()

    @allure.story("修改客户名称，显示颜色，显示顺序")
    # @pytest.mark.run(order=1)
    def test_customer_editnamesuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "1测试A"
        # 选中客户代码
        customer.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        customer.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 输入修改的客户名称
        customer.enter_texts(
            '(//label[text()="客户名称"])[1]/parent::div//input', f"{text}"
        )
        # 获取修改好的值
        editname = customer.get_find_element_xpath(
            '(//label[text()="客户名称"])[1]/parent::div//input'
        ).get_attribute("value")

        # 修改显示颜色
        customer.click_button(
            '//div[label[text()="显示颜色"]]//i'
        )
        # 选择5
        customer.click_button('//div[@class="d-flex"]/span[text()="5"]')
        # 获取下拉框的值
        customersel = customer.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text

        # 修改显示顺序
        ele = customer.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        # 显示顺序输入文字字母符号数字
        customer.enter_texts(
            '(//label[text()="显示顺序"])[1]/parent::div//input', "66"
        )
        sleep(1)
        # 获取显示顺序框
        customernum = customer.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        ).get_attribute("value")
        # 点击确定
        customer.click_confirm_button()
        sleep(1)
        # 定位表格内容
        customername = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]/div'
        ).text
        color = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]/div'
        ).text
        sleep(1)
        num = customer.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]/div'
        ).text
        assert (
            customername == editname
            and color == customersel
            and num == customernum
        )
        assert not customer.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_customer_refreshsuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        # 客户代码筛选框输入123
        customer.enter_texts(
            '//p[text()="客户代码"]/ancestor::div[2]//input', "123"
        )
        customer.click_ref_button()
        customertext = customer.get_find_element_xpath(
            '//p[text()="客户代码"]/ancestor::div[2]//input'
        ).text
        assert customertext == "", f"预期{customertext}"
        assert not customer.has_fail_message()

    @allure.story("查询客户代码成功")
    # @pytest.mark.run(order=1)
    def test_customer_selectcodesuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111"
        # 点击查询
        customer.click_sel_button()
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
        # 点击客户代码
        customer.click_button('//div[text()="客户代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        customer.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        customer.click_select_button()
        # 定位第一行是否为111
        customercode = customer.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        customercode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert customercode == name and len(customercode2) == 0
        assert not customer.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_customer_selectnodatasuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        # 点击查询
        customer.click_sel_button()
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
        # 点击客户代码
        customer.click_button('//div[text()="客户代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        customer.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        customer.click_select_button()
        customercode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        assert len(customercode) == 0
        assert not customer.has_fail_message()

    @allure.story("查询客户名字成功")
    # @pytest.mark.run(order=1)
    def test_customer_selectnamesuccess(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        name = "111"
        # 点击查询
        customer.click_sel_button()
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
        # 点击客户名称
        customer.click_button('//div[text()="客户名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        customer.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        customer.click_select_button()
        eles = customer.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        # 定位第一行是否为111
        assert len(eles) > 0
        assert all(name == v for v in eles)
        assert not customer.has_fail_message()

    @allure.story("查询显示顺序<10")
    # @pytest.mark.run(order=1)
    def test_customer_selectsuccess1(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        # 点击查询
        customer.click_sel_button()
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
        # 点击客户优先度
        customer.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        customer.click_button('//div[text()="<" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "10",
        )
        sleep(1)

        # 点击确认
        customer.click_select_button()
        eles = customer.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        assert len(eles) > 0
        assert all(int(v) < 10 for v in eles)
        assert not customer.has_fail_message()

    @allure.story("查询客户名称包含美并且显示顺序<10")
    # @pytest.mark.run(order=1)
    def test_customer_selectsuccess2(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        # 点击查询
        customer.click_sel_button()
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
        # 点击客户名称
        customer.click_button('//div[text()="客户名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        customer.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        customer.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "美",
        )

        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        customer.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        customer.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击客户优先度
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        customer.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        customer.click_button('//div[text()="<" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            "10",
        )
        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        customer.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        customer.click_select_button()
        name = customer.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        code = customer.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        assert len(code) > 0 and len(name) > 0
        assert all(int(code) < 10 for code in code) and all(
            "美" in name for name in name
        )
        assert not customer.has_fail_message()

    @allure.story("查询客户名称以美开头或显示顺序>10")
    # @pytest.mark.run(order=1)
    def test_customer_selectsuccess3(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage

        # 点击查询
        customer.click_sel_button()
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
        # 点击名称
        customer.click_button('//div[text()="客户名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        customer.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        customer.click_button('//div[text()="Begins with" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "美",
        )

        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        customer.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        customer.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击显示顺序
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        customer.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        customer.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值10
        customer.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            "10",
        )
        # 点击（
        customer.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        customer.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        customer.click_select_button()
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
                td3 = tds[2].text.strip()
                td5_raw = tds[4].text.strip()
                td5_val = int(td5_raw) if td5_raw else 0

                assert "美" in td3 or td5_val > 10, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td5_raw = tds[4].text.strip()
                td5_val = int(td5_raw) if td5_raw else 0
                assert "美" in td3 or td5_val > 10, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1
        assert not customer.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_customer_addall(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        data_list = ["全部数据", "20"]
        customer.click_add_button()  # 检查点击添加
        customer.add_input_all(data_list[0], data_list[1])
        sleep(1)
        customer.enter_texts(
            '//p[text()="客户代码"]/ancestor::div[2]//input', data_list[0]
        )
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{data_list[0]}"]]]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = [data_list[0], data_list[0], '2', data_list[1], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[0], f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text)):
            if i == 26:
                assert str(e) in str(a), f"第28项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not customer.has_fail_message()

    @allure.story("重新打开浏览器，数据还存在")
    # @pytest.mark.run(order=1)
    def test_customer_restart(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        data_list = ["全部数据", "20"]
        customer.enter_texts(
            '//p[text()="客户代码"]/ancestor::div[2]//input', data_list[0]
        )
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{data_list[0]}"]]]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = [data_list[0], data_list[0], '2', data_list[1], data_list[0], data_list[0], data_list[0],
                    data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0], data_list[0],
                    data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1], data_list[1],
                    data_list[1], data_list[1], data_list[1], data_list[0], f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text)):
            if i == 26:
                assert str(e) in str(a), f"第28项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not customer.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_customer_delsuccess1(self, login_to_customer):
        driver = login_to_customer  # WebDriver 实例
        customer = CustomerPage(driver)  # 用 driver 初始化 CustomerPage
        layout = "测试布局A"

        value = ['全部数据', '111', '1测试A','111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        customer.del_all(value, '//p[text()="客户代码"]/ancestor::div[2]//input')
        data = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        customer.del_layout(layout)
        customer.wait_for_loading_to_disappear()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in data)
        assert 0 == len(after_layout)
        assert not customer.has_fail_message()
