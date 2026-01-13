import logging
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.sched_page import SchedPage
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.systemPage.userRole_page import UserRolePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_userrole():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
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
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("用户权限管理页用例")
@pytest.mark.run(order=206)
class TestUserRolePage:

    @allure.story("点击新增不输入数据点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_user_addfail1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="用户代码"]]//input',
            '//div[label[text()="用户名称"]]//input',
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
            '//div[label[text()="用户有效日期"]]//input',
        ]
        sleep(0.5)
        user.click_all_button("新增")
        sleep(0.5)
        user.click_all_button("保存")
        sleep(2)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        user.click_all_button("取消")
        assert all(value == expected_color for value in value_list)
        assert not user.has_fail_message()

    @allure.story("点击只输入用户代码和用户名称点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_user_addfail2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1用户代码1'
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
            '//div[label[text()="用户有效日期"]]//input',
        ]
        xpath_value_map = {
            '//div[label[text()="用户代码"]]//input': name,
            '//div[label[text()="用户名称"]]//input': name,
        }
        sleep(0.5)
        user.click_all_button("新增")
        add.batch_modify_inputs(xpath_value_map)
        sleep(0.5)
        user.click_all_button("保存")
        sleep(2)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        user.click_all_button("取消")
        assert all(value == expected_color for value in value_list)
        assert not user.has_fail_message()

    @allure.story("点击输入用户代码和用户名称，密码和确认密码，点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_user_addfail3(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1用户代码1'
        password = 'Qw123456'
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="用户有效日期"]]//input',
        ]
        xpath_value_map = {
            '//div[label[text()="用户代码"]]//input': name,
            '//div[label[text()="用户名称"]]//input': name,
            '//div[label[text()="密码"]]//input': password,
            '//div[label[text()="确认密码"]]//input': password,
        }
        sleep(0.5)
        user.click_all_button("新增")
        add.batch_modify_inputs(xpath_value_map)
        sleep(0.5)
        user.click_all_button("保存")
        sleep(2)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        user.click_all_button("取消")
        assert all(value == expected_color for value in value_list)
        assert not user.has_fail_message()

    @allure.story("点击输入全部数据，不勾选角色，点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_user_addfail4(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1用户代码1'
        password = 'Qw123456'
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[label[text()="用户代码"]]//input': name,
            '//div[label[text()="用户名称"]]//input': name,
            '//div[label[text()="密码"]]//input': password,
            '//div[label[text()="确认密码"]]//input': password,
        }
        sleep(0.5)
        user.click_all_button("新增")
        add.batch_modify_inputs(xpath_value_map)
        user.click_button('//div[label[text()="用户有效日期"]]//input')
        user.click_button('//div[@class="ivu-date-picker-cells"]/span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"]')
        sleep(0.5)
        user.click_all_button("保存")
        message = user.get_error_message()
        user.click_all_button("取消")
        assert message == "请选择角色"
        assert not user.has_fail_message()

    @allure.story("添加用户成功")
    # @pytest.mark.run(order=1)
    def test_user_addsuccess(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1user1'
        password = 'Qw123456'
        role = '1测试角色代码1'
        user.add_user(name, password, role)
        user.click_all_button("保存")
        message = user.get_find_message()
        user.select_input(name)
        ele = user.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        user.right_refresh()
        assert message == "保存成功" and len(ele) == 1
        assert not user.has_fail_message()

    @allure.story("校验用户代码文本框，输入其他字符，显示只能包含字母和数字和下划线")
    # @pytest.mark.run(order=1)
    def test_user_verify1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1用户w+.?=-+a_1'
        list_ = [
            '//div[label[text()="用户代码"]]//input',
            '//div[label[text()="用户名称"]]//input'
        ]
        user.click_all_button("新增")
        user.enter_texts(list_[0], name)
        user.click_button(list_[1])
        sleep(0.5)
        ele = user.get_find_element_xpath(list_[0]).get_attribute("value")
        user.click_all_button("取消")
        assert ele == '1wa_1'
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,密码长度最小为8")
    # @pytest.mark.run(order=1)
    def test_user_verify2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["AAAb123", "AAAb123"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.click_all_button("新增")
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "密码最小长度为8位，最大为30位"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,密码长度最大为30")
    # @pytest.mark.run(order=1)
    def test_user_verify3(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["AAAb123111111111111111111111111", "AAAb123111111111111111111111111"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "密码最小长度为8位，最大为30位"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,不能包含特殊字符:<>')+/")
    # @pytest.mark.run(order=1)
    def test_user_verify4(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["Qw12+>34", "Qw12+>34"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "不能包含+: , [ < > ' ) / ，]符号"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,密码只含有字母和数字")
    # @pytest.mark.run(order=1)
    def test_user_verify5(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["Q1234567", "Q1234567"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "密码至少包含大写字母，小写字母，数字，特殊字符中的3类"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,密码首位字符不允许为空格字")
    # @pytest.mark.run(order=1)
    def test_user_verify6(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = [" Qw123456", " Qw123456"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "首位字符不允许为空格"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,不允许包含用户名")
    # @pytest.mark.run(order=1)
    def test_user_verify7(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["Q1user16", "Q1user16"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts('//div[label[text()="用户代码"]]//input', "1user1")
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify1 = user.get_verify_text("密码")
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert all(value == expected_color for value in value_list)
        assert verify1 == verify2 == "不允许包含用户名"
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不符合标准,输入中文")
    # @pytest.mark.run(order=1)
    def test_user_verify8(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        add = AddsPages(driver)
        password = ["Qq还会333611", "Qq还会333611"]
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        value_list = add.batch_acquisition_input(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        assert all(value == 'Qq333611' for value in value_list)
        assert not user.has_fail_message()

    @allure.story("校验密码和确认密码不一致")
    # @pytest.mark.run(order=1)
    def test_user_verify9(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        password = ["Qw123456", "Qw123446"]
        add = AddsPages(driver)
        list_ = [
            '//div[label[text()="密码"]]//input',
            '//div[label[text()="确认密码"]]//input',
        ]
        user.enter_texts(list_[0], password[0])
        user.enter_texts(list_[1], password[1])
        user.click_all_button("保存")
        sleep(0.5)
        verify2 = user.get_verify_text("确认密码")
        value_list = add.get_border_color(['//div[label[text()="确认密码"]]//input'])
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        user.click_all_button("取消")
        assert all(value == expected_color for value in value_list)
        assert verify2 == "与用户密码保持一致！"
        assert not user.has_fail_message()

    @allure.story("校验数字文本框和文本框")
    # @pytest.mark.run(order=1)
    def test_user_verify10(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "1111111111111111333311222211112222211111111133331111111444441111111111111111111111111111111111111111"
        password = 'Qw123456'
        role = '1测试角色代码2'
        user.add_user(name, password, role)
        user.enter_texts('//div[label[text()="密码有效天数"]]//input', name)
        num = user.get_find_element_xpath('//div[label[text()="密码有效天数"]]//input').get_attribute("value")
        user.click_all_button("保存")
        message = user.get_find_message()
        user.select_input(name)
        ele = user.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        user.right_refresh()
        assert message == "保存成功" and len(ele) == 1 and num == '100000'
        assert not user.has_fail_message()

    @allure.story("删除数字文本框和文本框")
    # @pytest.mark.run(order=1)
    def test_user_delverify10(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = ["1111111111111111333311222211112222211111111133331111111444441111111111111111111111111111111111111111"]
        user.del_(name)
        user.select_input(name)
        ele = user.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        user.right_refresh()
        assert len(ele) == 0
        assert not user.has_fail_message()

    @allure.story("添加用户重复")
    # @pytest.mark.run(order=1)
    def test_user_addrepeat(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1user1'
        password = 'Qw123456'
        role = '1测试角色代码2'
        user.add_user(name, password, role)
        user.click_all_button("保存")
        sleep(1)
        # 获取重复弹窗文字
        error_popup = user.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        user.click_all_button("取消")
        user.right_refresh()
        assert error_popup == "记录已存在,请检查！"
        assert not user.has_fail_message()

    @allure.story("添加测试数据，设置指定登录方式为扫码")
    # @pytest.mark.run(order=1)
    def test_user_t1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()
        name = '1user2'
        password = 'Qw123456'
        role = '1测试角色代码2'
        user.add_user(name, password, role)
        user.click_button('//div[label[text()="指定登录方式"]]//div[@class="ivu-select-selection"]')
        user.click_button('//ul/li[text()="扫码登录"]')
        user.click_all_button("保存")
        sleep(1)
        message = user.get_find_message()
        user.select_input(name)
        ele = user.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')

        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, '1测试计划单元小日程')
        ele_err = user.finds_elements(By.XPATH, f'//div[@class="ivu-modal-body"]//div[text()=" 用户登录类型错误 "]')
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert message == "保存成功" and len(ele) == 1 == len(ele_err)
        assert not user.has_fail_message()

    @allure.story("设置用户锁定成功")
    # @pytest.mark.run(order=1)
    def test_user_t2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()

        name = '1user2'
        password = 'Qw1234561'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        sy = user.get_find_element_xpath('(//div[label[text()="是否锁定"]]/div//span)[1]').get_attribute("class")
        user.click_button('//div[label[text()="指定登录方式"]]//div[@class="ivu-select-selection"]')
        user.click_button('//ul/li[text()="全部"]')
        if 'ivu-checkbox-checked' not in sy:
            user.click_button('(//div[label[text()="是否锁定"]]/div//span)[1]')
        user.click_all_button("保存")
        sleep(1)
        message = user.get_find_message()

        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, '1测试计划单元小日程')
        for i in range(6):
            user.click_button('//button[span[text()="关闭"]]')
            sleep(1)
            page.click_login_button()
            sleep(1)
        user.click_button('//button[span[text()="关闭"]]')
        page.login(name, 'Qw123456', '1测试计划单元小日程')
        ele_err = user.finds_elements(By.XPATH, f'//div[@class="ivu-modal-body"]//div[text()=" 账户被锁定,请稍后再试. "]')
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert 1 == len(ele_err)
        assert not user.has_fail_message()

    @allure.story("当前用户被锁定，点击解除当前锁定，取消锁定成功")
    # @pytest.mark.run(order=1)
    def test_user_lock2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()
        password = 'Qw123456'
        name = '1user2'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        # sleep(1)
        # user.click_all_button("编辑")
        # sleep(1)
        # sy = user.get_find_element_xpath('(//div[label[text()="是否锁定"]]/div//span)[1]').get_attribute("class")
        # if 'ivu-checkbox-checked' in sy:
        #     user.click_button('(//div[label[text()="是否锁定"]]/div//span)[1]')
        # sleep(1)
        # user.click_all_button("保存")
        # user.get_find_message()
        # user.right_refresh()
        # user.select_input(name)
        # sleep(1)
        table_sy = user.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{name}"]]/td[6]//span[1]').get_attribute(
            "class")
        if 'vxe-icon-checkbox-checked-fill' in table_sy:
            user.click_all_button('解除当前锁定')
            user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            message = user.get_find_message()
            assert message == "修改成功"
        else:
            assert 1 == 0

        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, '1测试计划单元小日程')
        err = user.finds_elements(By.XPATH, f'//div[@class="ivu-modal-body"]//div[text()="当前用户已经登录此单元，是否继续登录？"]')
        if len(err) == 1:
            user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        user.wait_for_loadingbox()
        profile_icon = user.get_find_element_xpath(
            f'//div[text()=" 1测试计划单元小日程 "]'
        )
        assert profile_icon.is_displayed()
        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert len(err) == 0
        assert not user.has_fail_message()

    @allure.story("设置用户禁用成功")
    # @pytest.mark.run(order=1)
    def test_user_t3(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()

        name = '1user2'
        password = 'Qw123456'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        sy = user.get_find_element_xpath('//div[label[text()="是否锁定"]]/div//span').get_attribute("class")
        if sy == 'ivu-checkbox ivu-checkbox-checked':
            user.click_button('//div[label[text()="是否锁定"]]/div//span')
        user.click_button('//div[label[text()="是否禁用"]]/div//span')
        user.click_all_button("保存")
        sleep(1)
        message = user.get_find_message()

        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, '1测试计划单元小日程')
        ele_err = user.finds_elements(By.XPATH, f'//div[@class="ivu-modal-body"]//div[text()=" 用户名或密码无效 "]')
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert message == "保存成功" and 1 == len(ele_err)
        assert not user.has_fail_message()

    @allure.story("设置用户有效期为之前的，显示已过期")
    # @pytest.mark.run(order=1)
    def test_user_t4(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()

        name = '1user2'
        password = 'Qw123456'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        sy = user.get_find_element_xpath('//div[label[text()="是否禁用"]]/div//span').get_attribute("class")
        if sy == 'ivu-checkbox ivu-checkbox-checked':
            user.click_button('//div[label[text()="是否禁用"]]/div//span')
        user.click_button('//div[label[text()="用户有效日期"]]//input')
        user.click_button(
            '//div[@class="ivu-date-picker-cells"]/span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"]/preceding-sibling::span[1]')
        user.click_all_button("保存")
        sleep(1)
        message = user.get_find_message()

        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, '1测试计划单元小日程')
        ele_err = user.finds_elements(By.XPATH, f'//div[@class="ivu-modal-body"]//div[text()=" 用户已失效,请联系管理员 "]')
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert message == "保存成功" and 1 == len(ele_err)
        assert not user.has_fail_message()

    @allure.story("修改用户名称，用户日期，用户类型，密码有效天数，角色代码成功")
    # @pytest.mark.run(order=1)
    def test_user_update(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()

        name = '1user2'
        password = 'Qw123456'
        module = '1测试计划单元标准'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)

        user.enter_texts('//div[label[text()="用户名称"]]//input', '修改用户名称')

        user.click_button('//div[label[text()="用户类型"]]//div[@class="ivu-select-selection"]')
        user.click_button('//ul/li[text()="计划用户"]')
        ele = user.get_find_element_xpath('//div[label[text()="密码有效天数"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        user.enter_texts('//div[label[text()="密码有效天数"]]//input', '2')

        user.click_button('//div[label[text()="用户有效日期"]]//input')
        user.click_button(
            '//div[@class="ivu-date-picker-cells"]/span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"]/following-sibling::span[1]')

        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', '1测试角色代码3')
        sleep(2)
        user.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2]/div/span)[2]')

        before_name = user.get_find_element_xpath('//div[label[text()="用户名称"]]//input').get_attribute("value")
        before_sel = user.get_find_element_xpath('//div[label[text()="用户类型"]]//div[@class="ivu-select-selection"]//span').text
        before_pass = user.get_find_element_xpath('//div[label[text()="密码有效天数"]]//input').get_attribute("value")
        user.click_all_button("保存")
        sleep(1)
        message = user.get_find_message()

        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        after_name = user.get_find_element_xpath('//div[label[text()="用户名称"]]//input').get_attribute("value")
        after_sel = user.get_find_element_xpath(
            '//div[label[text()="用户类型"]]//div[@class="ivu-select-selection"]//span').text
        after_pass = user.get_find_element_xpath('//div[label[text()="密码有效天数"]]//input').get_attribute(
            "value")
        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(name, password, module)
        user.wait_for_loadingbox()
        num_ = len(user.finds_elements(By.XPATH, f'//div[@class="listDivCon"]/div'))
        swich_name = user.get_find_element_xpath(f'//div[@class="ivu-dropdown-rel"]/div').text
        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert message == "保存成功" and num_ >= 7 and swich_name == module
        assert before_name == after_name and before_sel == after_sel and before_pass == after_pass == '2'
        assert not user.has_fail_message()

    @allure.story("当前用户没有被锁定，点击解除当前锁定，显示用户未锁定")
    # @pytest.mark.run(order=1)
    def test_user_lock1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = '1user2'
        user.select_input(name)
        sleep(1)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        sy = user.get_find_element_xpath('(//div[label[text()="是否锁定"]]/div//span)[1]').get_attribute("class")
        if 'ivu-checkbox-checked' in sy:
            user.click_button('(//div[label[text()="是否锁定"]]/div//span)[1]')
        sleep(1)
        user.click_all_button("保存")
        user.get_find_message()
        user.right_refresh()
        user.select_input(name)
        sleep(2)
        user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        table_sy = user.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{name}"]]/td[6]//span[1]').get_attribute(
            "class")
        if 'vxe-icon-checkbox-unchecked' in table_sy:
            user.click_all_button('解除当前锁定')
            message = user.get_error_message()
            assert message == "用户未锁定"
        else:
            assert 1 == 0
        assert not user.has_fail_message()

    @allure.story("点击解除所有锁定成功")
    # @pytest.mark.run(order=1)
    def test_user_lock3(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        user.wait_for_loading_to_disappear()
        user.click_all_button('解除所有锁定')
        user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = user.get_find_message()
        assert message == "修改成功"
        assert not user.has_fail_message()

    # @allure.story("当前用户被锁定，点击解除所有锁定，取消锁定成功")
    # # @pytest.mark.run(order=1)
    # def test_user_lock4(self, login_to_userrole):
    #     driver = login_to_userrole  # WebDriver 实例
    #     user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
    #     name = '1user2'
    #     user.select_input(name)
    #     sleep(1)
    #     user.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
    #     sleep(1)
    #     user.click_all_button("编辑")
    #     sleep(1)
    #     sy = user.get_find_element_xpath('//div[label[text()="是否锁定"]]/div//span').get_attribute("class")
    #     if sy != 'ivu-checkbox ivu-checkbox-checked':
    #         user.click_button('//div[label[text()="是否锁定"]]/div//span')
    #     sleep(1)
    #     user.click_all_button("保存")
    #     message = user.get_find_message()
    #     user.right_refresh()
    #     user.select_input(name)
    #     sleep(1)
    #     table_sy = user.get_find_element_xpath(
    #         f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{name}"]]/td[6]//span[1]').get_attribute(
    #         "class")
    #     if table_sy == 'vxe-checkbox--icon vxe-icon-checkbox-checked-fill':
    #         user.click_all_button('解除所有锁定')
    #         user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
    #         message = user.get_find_message()
    #         assert message == "修改成功"
    #     else:
    #         assert 1 == 0
    #     assert not user.has_fail_message()

    @allure.story("查询用户代码成功")
    # @pytest.mark.run(order=1)
    def test_user_select1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "1user2"
        user.select_input(name)
        sleep(1)
        eles = user.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        user.right_refresh()
        assert all(text == name for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not user.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_user_select2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        sleep(1)
        eles = user.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            user.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            user.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//input')
        eles = user.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        assert len(eles) == 0
        assert not user.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_user_select3(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "1"
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        user.hover("包含")
        sleep(1)
        user.select_input(name)
        sleep(1)
        eles = user.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not user.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_user_select4(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "1"
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        user.hover("符合开头")
        sleep(1)
        user.select_input(name)
        sleep(1)
        eles = user.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not user.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_user_select5(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "2"
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        user.hover("符合结尾")
        sleep(1)
        user.select_input(name)
        sleep(1)
        eles = user.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not user.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_user_clear(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        name = "3"
        sleep(1)
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        user.hover("包含")
        sleep(1)
        user.select_input(name)
        sleep(1)
        user.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        user.hover("清除所有筛选条件")
        sleep(1)
        ele = user.get_find_element_xpath('//div[p[text()="用户代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not user.has_fail_message()

    @allure.story("点击取消不会修改数据")
    # @pytest.mark.run(order=1)
    def test_user_cancel(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        before_name = "1user2"
        after_name = "修改成功"
        user.update_user(before_name, after_name)
        user.click_all_button("取消")
        user.right_refresh()
        user.select_input(before_name)
        sleep(1)
        eles = user.finds_elements(By.XPATH,
                                   f'(//table[@class="vxe-table--body"])[1]//tr/td[3]//span[text()="{after_name}"]')
        assert len(eles) == 0
        assert not user.has_fail_message()

    @allure.story("角色有用户使用不允许删除")
    # @pytest.mark.run(order=1)
    def test_user_roledel1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        user.click_button('(//span[text()="角色管理"])[1]')
        name = "1测试角色代码2"
        sleep(3)
        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name)
        sleep(1)
        user.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name}"]')
        user.click_all_button("删除")
        user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        user.wait_for_loading_to_disappear()
        message = user.get_find_element_xpath('//div[text()=" 记录已被使用,请检查 "]').text
        eles = user.finds_elements(By.XPATH,
                                   f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name}"]')
        user.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        user.right_refresh('角色管理')
        assert len(eles) == 1 and message == "记录已被使用,请检查"
        assert not user.has_fail_message()

    @allure.story("删除用户成功")
    # @pytest.mark.run(order=1)
    def test_user_del1(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        user.click_button('(//span[text()="用户权限管理"])[1]')
        user.wait_for_loading_to_disappear()
        names = ['1user2']
        user.del_(names)
        for name in names:
            xpath = f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name}"]'
            eles = user.finds_elements(By.XPATH, xpath)
            assert len(eles) == 0, f"用户 {name} 未成功删除"
        assert not user.has_fail_message()

    @allure.story("删除角色成功")
    # @pytest.mark.run(order=1)
    def test_user_roledel2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        username = DateDriver().username
        name1 = "1测试角色代码2"
        name2 = "1测试角色代码4"

        # 取消当前用户选中的角色
        user.select_input(username)
        user.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{username}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name1)
        sleep(1)
        user.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox is--checked"]')
        ele = user.get_find_element_xpath(
            '//div[div[p[text()="角色代码"]]]//input')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        sleep(1)
        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name2)
        sleep(1)
        user.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox is--checked"]')
        user.click_all_button("保存")
        user.get_find_message()

        user.click_button('(//span[text()="角色管理"])[1]')
        user.right_refresh('角色管理')
        # 等待遮罩层消失
        user.wait_for_el_loading_mask()
        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name1)
        sleep(1)
        user.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name1}"]')
        user.click_all_button("删除")
        user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        user.get_find_message()
        user.right_refresh('角色管理')
        user.wait_for_el_loading_mask()

        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name2)
        sleep(1)
        user.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name2}"]')
        user.click_all_button("删除")
        user.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        user.get_find_message()
        user.right_refresh('角色管理')
        user.wait_for_el_loading_mask()

        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name1)
        eles1 = user.finds_elements(By.XPATH,
                                   f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name1}"]')
        user.right_refresh('角色管理')
        user.wait_for_el_loading_mask()
        user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name2)
        eles2 = user.finds_elements(By.XPATH,
                                   f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name2}"]')
        assert len(eles1) == 0 and len(eles2) == 0
        assert not user.has_fail_message()

    @allure.story("已删除的用户不能登录")
    # @pytest.mark.run(order=1)
    def test_user_del2(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        user = UserRolePage(driver)  # 用 driver 初始化 UserRolePage
        page = LoginPage(driver)
        date_driver = DateDriver()

        name = '1user2'
        password = 'Qw123456'
        user.click_button('//div[@class="flex-alignItems-center"]')
        user.click_button('//ul/li/div[text()=" 注销 "]')
        page.enter_username(name)
        page.enter_password(password)
        page.click_button('//div[@class="ivu-select-head-flex"]/input')
        ele = user.finds_elements(By.XPATH, '//ul[@class="ivu-select-not-found"]/li[text()="无匹配数据"]')

        page.login(date_driver.username, date_driver.password, date_driver.planning)
        user.wait_for_loadingbox()
        list_ = ["系统管理", "系统设置", "用户权限管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        user.wait_for_loading_to_disappear()
        assert len(ele) == 1
        assert not user.has_fail_message()

    @allure.story("删除计划单元，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_plan_del(self, login_to_userrole):
        driver = login_to_userrole  # WebDriver 实例
        plan = PlanUnitPage(driver)  # 用 driver 初始化 UserRolePage
        plan.click_button('(//span[text()="计划单元"])[1]')
        layout = "测试布局A"

        value = ['1测试计划单元CTB', '1测试计划单元小日程',
                 '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        plan.del_all(value, '//p[text()="计划单元"]/ancestor::div[2]//input')
        sleep(2)
        data = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:3]
        ]
        plan.del_layout(layout)
        sleep(3)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in data)
        assert 0 == len(after_layout)
        assert not plan.has_fail_message()


