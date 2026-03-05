import logging
import os
import re
from datetime import datetime
from time import sleep

import allure
import pyautogui
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

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_apps_ctrlIrepeat(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = apps.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = apps.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
        apps.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not apps.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_apps_ctrlI(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        apps.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        apps.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = apps.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        apps.get_find_message()
        apps.select_input('1没有数据添加')
        ele2 = apps.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not apps.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_apps_ctrlM(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        apps.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        apps.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[3])[2]//input', '1没有数据修改')
        ele1 = apps.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[3])[2]//input').get_attribute(
            "value")
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        apps.get_find_message()
        apps.wait_for_loading_to_disappear()
        apps.enter_texts('//div[div[p[text()="应用名称"]]]//input', '1没有数据修改')
        ele2 = apps.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[3])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        assert not apps.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_apps_shiftdel(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.right_refresh('应用管理')
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]']
        apps.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = apps.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        apps.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        apps.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加1')
        sleep(2)
        apps.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        apps.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        apps.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据添加12')
        sleep(1)
        ele1 = apps.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
        ele2 = apps.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        apps.get_find_message()
        apps.select_input('1没有数据添加1')
        ele11 = apps.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        ele22 = apps.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        assert not apps.has_fail_message()
        apps.select_input('1没有数据添加')
        before_data = apps.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[1]']
        apps.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = apps.get_find_element_xpath(elements[2])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        apps.click_all_button('删除')
        apps.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = apps.get_find_message()
        apps.wait_for_loading_to_disappear()
        after_data = apps.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not apps.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_apps_ctrlC(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.right_refresh('应用管理')
        apps.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        apps.click_button('//div[div[p[text()="应用代码"]]]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = apps.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        apps.right_refresh('应用管理')
        assert all(before_data in ele for ele in eles)
        assert not apps.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_apps_shift(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
                    '//table[@class="vxe-table--body"]//tr[2]//td[1]']
        apps.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = apps.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = apps.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not apps.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_apps_ctrls(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
                    '//table[@class="vxe-table--body"]//tr[2]//td[1]']
        apps.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = apps.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = apps.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = apps.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not apps.has_fail_message()

    @allure.story("模拟ctrl+m修改,编辑对话框应用代码不可编辑")
    # @pytest.mark.run(order=1)
    def test_apps_ctrlMDisabled(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        apps.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        apps.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        ele1 = apps.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "disabled")
        apps.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert ele1
        assert not apps.has_fail_message()

    @allure.story("上传已有的应用成功")
    # @pytest.mark.run(order=1)
    def test_apps_upload1(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        dir_ = 'apptest1'
        apps.click_all_button('导入')
        # 清理 .crdownload 文件，避免上传未完成的文件
        current_dir = os.path.dirname(__file__)
        download_path = os.path.join(current_dir, "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)
        # 1. 准备上传文件路径
        upload_file = os.path.join(download_path, f"{dir_}.json")
        assert os.path.isfile(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        apps.get_find_element_xpath('(//input[@type="file"])[2]')
        pyautogui.write(upload_file)
        sleep(3)
        pyautogui.press('enter')
        sleep(1)
        pyautogui.press('enter')
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr/td[2]//label/span').get_attribute("class")
        if 'ivu-checkbox-checked' not in ele:
            apps.click_button('//table[@class="vxe-table--body"]//tr/td[2]//label/span')

        apps.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        but = apps.finds_elements(By.XPATH, '//div[@class="ivu-modal-body"]//span[text()="确定"]')
        if len(but) == 1:
            apps.click_button('//div[@class="ivu-modal-body"]//span[text()="确定"]')
        message = apps.get_find_message()
        assert message == '编辑成功！'
        assert not apps.has_fail_message()

    @allure.story("上传没有的应用成功")
    # @pytest.mark.run(order=1)
    def test_apps_upload2(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 AppsPage
        dir_ = '11AA'
        apps.click_all_button('导入')
        # 清理 .crdownload 文件，避免上传未完成的文件
        current_dir = os.path.dirname(__file__)
        download_path = os.path.join(current_dir, "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)
        # 1. 准备上传文件路径
        upload_file = os.path.join(download_path, f"{dir_}.json")
        assert os.path.isfile(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        apps.get_find_element_xpath('(//input[@type="file"])[2]')
        pyautogui.write(upload_file)
        sleep(3)
        pyautogui.press('enter')
        sleep(1)
        pyautogui.press('enter')
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr/td[2]//label/span').get_attribute(
            "class")
        if 'ivu-checkbox-checked' not in ele:
            apps.click_button('//table[@class="vxe-table--body"]//tr/td[2]//label/span')

        apps.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        message = apps.get_find_message()
        assert message == '新增成功！'
        assert not apps.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_apps_delsuccess(self, login_to_apps):
        driver = login_to_apps  # WebDriver 实例
        apps = AppsPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"

        value = ['appstest1', '11AA']
        apps.del_all(xpath='//div[p[text()="应用代码"]]/following-sibling::div//input', value=value)
        apps.right_refresh()
        try:
            apps.del_layout(layout)
        except Exception:
            print(f"布局 '{layout}' 可能不存在或已被删除")
        sleep(2)
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
