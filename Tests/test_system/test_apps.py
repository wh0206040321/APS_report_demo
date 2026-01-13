import logging
import os
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.apps_page import AppsPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_apps():
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
        list_ = ["系统管理", "系统设置", "应用管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("应用管理页用例")
@pytest.mark.run(order=215)
class TestSAppsPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_apps_addfail1(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        apps.add_layout(layout)
        # 获取布局名称的文本元素
        name = apps.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        sleep(1)
        apps.click_all_button("新增")
        sleep(1)
        apps.click_save_button()
        message = apps.get_error_message()
        assert layout == name
        assert message == "请设计表格或填写字段"
        assert not apps.has_fail_message()

    @allure.story("新增输入应用代码，应用名称点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_apps_addfail2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = "testapp1"
        xpath_list = [
            '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
            '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
            '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
            '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
            '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        apps.click_save_button()
        message = apps.get_error_message()
        apps.click_close_button()
        assert message == "请设计表格或填写字段"
        assert not apps.has_fail_message()

    @allure.story("新增空白应用成功")
    # @pytest.mark.run(order=1)
    def test_apps_addsuccess2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = "appstest1"
        apps.click_all_button("新增")
        sleep(1)
        xpath_list = [
            '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
            '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
            '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
            '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
            '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        apps.click_button(xpath_list[2])
        apps.click_button('//li[text()="计划基础数据"]')

        apps.click_button(xpath_list[3])
        apps.click_button('//div[@class="flex-wrap"]/div[1]')

        apps.enter_texts(xpath_list[4], "1")
        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        apps.select_input(name)
        sleep(1)
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        apps.right_refresh()
        assert message == "新增成功！" and ele == name
        assert not apps.has_fail_message()

    @allure.story("不允许保存重复应用代码")
    # @pytest.mark.run(order=1)
    def test_apps_addrepeat(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = "appstest1"
        apps.click_all_button("新增")
        sleep(1)
        xpath_list = [
            '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
            '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
            '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
            '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
            '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        apps.click_button(xpath_list[2])
        apps.click_button('//li[text()="计划基础数据"]')

        apps.click_button(xpath_list[3])
        apps.click_button('//div[@class="flex-wrap"]/div[1]')

        apps.enter_texts(xpath_list[4], "1")
        apps.click_save_button()
        ele = apps.finds_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        apps.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        apps.click_close_button()
        assert len(ele) == 1
        assert not apps.has_fail_message()

    @allure.story("保存模版成功")
    # @pytest.mark.run(order=1)
    def test_apps_addsavetemplate1(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = "appstest测试模版1"
        apps.click_all_button("新增")
        sleep(1)
        xpath_list = [
            '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
            '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
            '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
            '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
            '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        apps.click_button(xpath_list[2])
        apps.click_button('//li[text()="计划基础数据"]')

        apps.click_button(xpath_list[3])
        apps.click_button('//div[@class="flex-wrap"]/div[1]')

        apps.enter_texts(xpath_list[4], "1")

        apps.click_save_template_button(name)
        apps.go_template()
        num = apps.get_template_num(name)
        apps.click_close_button()
        assert num == 1
        assert not apps.has_fail_message()

    @allure.story("使用模版，更新模版成功")
    # @pytest.mark.run(order=1)
    def test_apps_addsavetemplate2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        before_name = 'appstest测试模版1'
        afert_name = "appstest测试模版2"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        apps.go_template()
        apps.click_button(f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[contains(text(),"{before_name}")]]//span[text()=" 加载模板 "]')
        apps.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        apps.go_template()
        apps.click_button('//div[@class="d-flex background-color-fff"]/div[3]')
        before_name1 = apps.get_find_element_xpath(
            f'//div[label[text()="名称"]]//input[@placeholder="请输入"]'
        ).get_attribute("value")
        apps.enter_texts('//div[label[text()="名称"]]//input[@placeholder="请输入"]', afert_name)
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        apps.get_find_message()
        sleep(2)
        num = apps.get_template_num(afert_name)
        apps.click_button('//div[div[text()=" 应用设计 "]]/span')
        assert before_name1 == before_name
        assert num == 1
        assert not apps.has_fail_message()

    @allure.story("删除模版成功")
    # @pytest.mark.run(order=1)
    def test_apps_deletetemplate(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        values = ["appstest测试模版2"]
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        apps.go_template()
        apps.delete_template(values)
        sleep(3)
        for value in values:
            ele = apps.finds_elements(By.XPATH, f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[contains(text(),"{value}")]]')
            assert len(ele) == 0
        apps.click_button('//div[div[text()=" 应用设计 "]]/span')
        assert not apps.has_fail_message()

    @allure.story("修改应用点击关闭，弹出弹窗点击无需保存，不保存")
    # @pytest.mark.run(order=1)
    def test_apps_update1(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="应用名称"]]//input', "appstest1修改")
        apps.click_button('//div[div[text()=" 应用设计 "]]/span')
        apps.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="无需保存"]')
        sleep(1)
        apps.select_input(name)
        apps.wait_for_loading_to_disappear()
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[3]').text
        assert ele == name
        assert not apps.has_fail_message()

    @allure.story("修改应用点击关闭，弹出弹窗点击保存，保存成功")
    # @pytest.mark.run(order=1)
    def test_apps_update2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="应用名称"]]//input', "appstest1修改")
        apps.click_button('//div[div[text()=" 应用设计 "]]/span')
        apps.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="保存"]')
        message = apps.get_find_message()
        apps.click_apps_button()
        apps.select_input(name)
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[3]').text
        assert message == "编辑成功！"
        assert ele == "appstest1修改"
        assert not apps.has_fail_message()

    @allure.story("修改排序成功")
    # @pytest.mark.run(order=1)
    def test_apps_update3(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        xpath = '//div[@class="d-flex"]/div[label[text()="排序"]]//input'
        ele =apps.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="排序"]]//input', "10")
        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        apps.select_input(name)
        sleep(2)
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[8]').text
        assert message == "编辑成功！"
        assert ele == "10"
        assert not apps.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_apps_addnum(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        xpath = '//div[@class="d-flex"]/div[label[text()="排序"]]//input'
        ele = apps.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="排序"]]//input', "1文字ab.c。？~1_2+3")
        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        apps.select_input(name)
        sleep(2)
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[8]').text
        apps.right_refresh()
        assert message == "编辑成功！"
        assert ele == "1123"
        assert not apps.has_fail_message()

    @allure.story("校验数字文本框成功")
    # @pytest.mark.run(order=1)
    def test_apps_textverify(self, login_to_apps):
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "appstest1"
        apps.wait_for_loading_to_disappear()
        apps.select_input(name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        apps.click_all_button("编辑")
        xpath = '//div[@class="d-flex"]/div[label[text()="排序"]]//input'
        ele = apps.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="排序"]]//input', num)
        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        apps.select_input(name)
        sleep(2)
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[8]').text
        apps.right_refresh()
        assert message == "编辑成功！"
        assert ele == "10000"
        assert not apps.has_fail_message()

    # @allure.story("查询应用代码成功")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectsuccess(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #     name = "Item"
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     # 点击物料代码
    #     apps.click_button('//div[text()="应用代码" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     apps.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(2)
    #     # 定位第一行是否为name
    #     itemcode = apps.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
    #     )
    #     assert itemcode == name and len(itemcode2) == 0
    #     assert not apps.has_fail_message()
    #
    # @allure.story("没有数据时显示正常")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectnodatasuccess(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     # 点击物料代码
    #     apps.click_button('//div[text()="应用代码" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     apps.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "没有数据",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(2)
    #     itemcode = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
    #     )
    #     assert len(itemcode) == 0
    #     assert not apps.has_fail_message()
    #
    # @allure.story("查询应用名称包含计划成功")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectnamesuccess(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     name = "计划"
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     apps.click_button('//div[text()="应用名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     apps.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(2)
    #     eles = apps.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
    #     assert len(eles) > 0
    #     assert all(name in ele for ele in eles)
    #     assert not apps.has_fail_message()
    #
    # @allure.story("查询排序>5")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectsuccess1(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     num = 5
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     apps.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     apps.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         num,
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(2)
    #     eles = apps.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[8]')
    #     assert len(eles) > 0
    #     assert all(int(ele) > num for ele in eles)
    #     assert not apps.has_fail_message()
    #
    # @allure.story("查询应用名称包含物料并且排序>3")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectsuccess2(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     name = "物料"
    #     num = 3
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     apps.click_button('//div[text()="应用名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     apps.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     apps.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     apps.click_button('//div[text()=")" and contains(@optid,"opt_")]')
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
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     apps.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     apps.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     apps.click_button('//div[text()=">" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         num,
    #     )
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     apps.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(2)
    #     eles1 = apps.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[8]')
    #     eles2 = apps.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
    #     assert len(eles1) > 0 and len(eles2) > 0
    #     assert all(int(ele) > num for ele in eles1) and all(name in ele for ele in eles2)
    #     assert not apps.has_fail_message()
    #
    # @allure.story("查询应用名称包含物料或排序≥4")
    # # @pytest.mark.run(order=1)
    # def test_apps_selectsuccess3(self, login_to_apps):
    #     driver = login_to_apps  # WebDriver 实例
    #     apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     name = "物料"
    #     num = 4
    #     # 点击查询
    #     apps.click_all_button("查询")
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
    #     apps.click_button('//div[text()="应用名称" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
    #     )
    #     apps.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击包含
    #     apps.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
    #     )
    #     apps.click_button('//div[text()=")" and contains(@optid,"opt_")]')
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
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
    #     )
    #     apps.click_button('//div[text()="(" and contains(@optid,"opt_")]')
    #     # 点击物料优先度
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
    #     )
    #     apps.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
    #     )
    #     # 点击>
    #     apps.click_button('//div[text()="≥" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值0
    #     apps.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
    #         num,
    #     )
    #     # 点击（
    #     apps.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
    #     )
    #     apps.click_button('//div[text()=")" and contains(@optid,"opt_")]')
    #
    #     sleep(1)
    #
    #     # 点击确认
    #     apps.click_button(
    #         '(//div[@class="demo-drawer-footer"])[3]/button[2]'
    #     )
    #     sleep(1)
    #     # 获取目标表格第2个 vxe 表格中的所有数据行
    #     xpath_rows = '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")]'
    #
    #     # 先拿到总行数
    #     base_rows = driver.find_elements(By.XPATH, xpath_rows)
    #     total = len(base_rows)
    #
    #     valid_count = 0
    #     for idx in range(total):
    #         try:
    #             # 每次都按索引重新定位这一行
    #             row = driver.find_elements(By.XPATH, xpath_rows)[idx]
    #             tds = row.find_elements(By.TAG_NAME, "td")
    #             td3 = tds[2].text.strip()
    #             td8_raw = tds[7].text.strip()
    #             td8_raw = int(td8_raw) if td8_raw else 0
    #
    #             assert name in td3 or td8_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td8={td8_raw}"
    #             valid_count += 1
    #
    #         except StaleElementReferenceException:
    #             # 如果行元素失效，再重试一次
    #             row = driver.find_elements(By.XPATH, xpath_rows)[idx]
    #             tds = row.find_elements(By.TAG_NAME, "td")
    #             td3 = tds[2].text.strip()
    #             td8_raw = tds[7].text.strip()
    #             td8_raw = int(td8_raw) if td8_raw else 0
    #             assert name in td3 or td8_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td8={td8_raw}"
    #             valid_count += 1
    #     assert not apps.has_fail_message()
    #     print(f"符合条件的行数：{valid_count}")

    @allure.story("过滤查组件名称成功")
    # @pytest.mark.run(order=1)
    def test_apps_select1(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        apps.wait_for_loading_to_disappear()
        name = "物品"
        apps.enter_texts('//div[div[p[text()="应用名称"]]]//input', name)
        sleep(2)
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        list_ = [ele.text for ele in eles]
        apps.right_refresh()
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not apps.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_apps_select2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        apps.wait_for_loading_to_disappear()
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        sleep(1)
        eles = apps.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            apps.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            apps.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        apps.click_button('//div[div[p[text()="应用代码"]]]//input')
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        apps.right_refresh()
        assert len(eles) == 0
        assert not apps.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_apps_select3(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        apps.wait_for_loading_to_disappear()
        name = "Item"
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        apps.hover("包含")
        sleep(1)
        apps.select_input(name)
        sleep(1)
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        apps.right_refresh()
        assert all(name.casefold() in text.casefold() for text in list_)
        assert not apps.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_apps_select4(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "Item"
        apps.wait_for_loading_to_disappear()
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        apps.hover("符合开头")
        sleep(1)
        apps.select_input(name)
        sleep(1)
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        apps.right_refresh()
        assert all(str(item).startswith(name) for item in list_)
        assert not apps.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_apps_select5(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        apps.wait_for_loading_to_disappear()
        name = "a"
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        apps.hover("符合结尾")
        sleep(1)
        apps.select_input(name)
        sleep(1)
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        apps.right_refresh()
        assert all(str(item).lower().endswith(name.lower()) for item in list_)
        assert not apps.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_apps_clear(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        apps.wait_for_loading_to_disappear()
        name = "3"
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        apps.hover("包含")
        sleep(1)
        apps.select_input(name)
        sleep(1)
        apps.click_button('//div[p[text()="应用代码"]]/following-sibling::div//i')
        apps.hover("清除所有筛选条件")
        sleep(1)
        ele = apps.get_find_element_xpath('//div[p[text()="应用代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not apps.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_apps_delsuccess(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"

        value = ['appstest1']
        apps.del_all(xpath='//div[p[text()="应用代码"]]/following-sibling::div//input', value=value)
        sleep(2)
        apps.wait_for_loading_to_disappear()
        apps.del_layout(layout)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:1]
        ]
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in itemdata)
        assert 0 == len(after_layout)
        assert not apps.has_fail_message()
