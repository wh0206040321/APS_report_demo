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
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.expression_page import ExpressionPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_expression():
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
        list_ = ["系统管理", "系统设置", "表达式管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("表达式管理页用例")
@pytest.mark.run(order=212)
class TestSExpressionPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_expression_addfail1(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        expression.click_all_button("新增")
        sleep(1)
        expression.click_all_button("保存")
        message = expression.get_error_message()
        assert message == "请填写完整的信息才能提交"
        assert not expression.has_fail_message()

    @allure.story("新增只填写名称点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_expression_addfail2(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = '1测试表达式管理1'
        sleep(1)
        expression.click_all_button("新增")
        expression.enter_texts('//div[p[text()="名称: "]]//input', name)
        expression.click_all_button("保存")
        message = expression.get_error_message()
        assert message == "请填写完整的信息才能提交"
        assert not expression.has_fail_message()

    @allure.story("新增填写名称和分类点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_expression_addfail3(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1测试表达式管理1'
        expression.click_all_button("新增")
        expression.enter_texts('//div[p[text()="名称: "]]//input', name)
        expression.click_button('//div[p[text()="分类: "]]//input[@type="text"]')
        expression.click_button('//li[text()="图棒显示颜色"]')
        expression.click_all_button("保存")
        message = expression.get_error_message()
        assert message == "请填写完整的信息才能提交"
        assert not expression.has_fail_message()

    @allure.story("添加表达式管理成功")
    # @pytest.mark.run(order=1)
    def test_expression_addsuccess(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1测试表达式管理1'
        expression.click_all_button("新增")
        expression.enter_texts('//div[p[text()="名称: "]]//input', name)
        expression.click_button('//div[p[text()="分类: "]]//input[@type="text"]')
        expression.click_button('//li[text()="图棒显示颜色"]')
        expression.enter_texts('//div[p[text()="表达式: "]]//textarea', name)
        expression.click_all_button("保存")
        message = expression.get_find_message()
        expression.select_input_expression(name)
        eles = expression.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert eles == name
        assert message == "保存成功"
        assert not expression.has_fail_message()

    @allure.story("添加表达式管理重复不允许添加")
    # @pytest.mark.run(order=1)
    def test_expression_addrepeat1(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1测试表达式管理1'
        expression.click_all_button("新增")
        expression.enter_texts('//div[p[text()="名称: "]]//input', name)
        expression.click_button('//div[p[text()="分类: "]]//input[@type="text"]')
        expression.click_button('//li[text()="图棒显示颜色"]')
        expression.enter_texts('//div[p[text()="表达式: "]]//textarea', name)
        expression.click_all_button("保存")
        message = expression.get_error_message()
        assert message == "不可以新增名称和分类相同的数据"
        assert not expression.has_fail_message()

    @allure.story("修改表达式名称，相当于新增")
    # @pytest.mark.run(order=1)
    def test_expression_updatesuccess1(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        before_name = '1测试表达式管理1'
        afert_name = '1测试表达式管理2'
        expression.select_input_expression(before_name)
        expression.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        expression.click_all_button("编辑")
        expression.enter_texts('//div[p[text()="名称: "]]//input', afert_name)
        expression.click_all_button("保存")
        message = expression.get_find_message()
        expression.select_input_expression(afert_name)
        sleep(1)
        eles1 = expression.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        expression.select_input_expression(before_name)
        sleep(1)
        eles2 = expression.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert eles1 == afert_name and eles2 == before_name
        assert message == "保存成功"
        assert not expression.has_fail_message()

    @allure.story("修改表达式分类，相当于新增")
    # @pytest.mark.run(order=1)
    def test_expression_updatesuccess2(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1测试表达式管理1'
        expression.select_input_expression(name)
        sleep(1)
        expression.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        expression.click_all_button("编辑")
        expression.click_button('//div[p[text()="分类: "]]//input[@type="text"]')
        expression.click_button('//li[text()="分派规则"]')
        expression.click_all_button("保存")
        message = expression.get_find_message()
        expression.select_input_expression(name)
        sleep(1)
        eles1 = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[2]')
        eles2 = expression.get_find_element_xpath('//table[@class="vxe-table--body"]//tr/td[3]//span[text()="分派规则"]').text
        assert len(eles1) == 2
        assert eles2 == "分派规则"
        assert message == "保存成功"
        assert not expression.has_fail_message()

    @allure.story("修改表达式成功")
    # @pytest.mark.run(order=1)
    def test_expression_updatesuccess3(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = '1测试表达式管理2'
        text = '1111'
        expression.select_input_expression(name)
        sleep(2)
        expression.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        expression.click_all_button("编辑")
        expression.enter_texts('//div[p[text()="表达式: "]]//textarea', text)
        expression.click_all_button("保存")
        message = expression.get_find_message()
        expression.select_input_expression(name)
        sleep(1)
        expression.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        expression.click_all_button("编辑")
        testarea = expression.get_find_element_xpath('//div[p[text()="表达式: "]]//textarea').get_attribute('value')
        assert testarea == text
        assert message == "保存成功"
        assert not expression.has_fail_message()

    @allure.story("删除表达式成功")
    # @pytest.mark.run(order=1)
    def test_expression_del(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        value = ['1测试表达式管理1', '1测试表达式管理1', '1测试表达式管理2']
        expression.del_all(xpath='//div[div[p[text()="名称"]]]//input', value=value)
        ele = expression.get_find_element_xpath('//div[div[p[text()="名称"]]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:3]
        ]
        assert all(len(elements) == 0 for elements in itemdata)
        assert not expression.has_fail_message()

    @allure.story("查询表达式名称成功")
    # @pytest.mark.run(order=1)
    def test_expression_select1(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = "1"
        expression.select_input_expression(name)
        sleep(1)
        eles = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not expression.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_expression_select2(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        sleep(1)
        eles = expression.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            expression.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            expression.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//input')
        eles = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not expression.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_expression_select3(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = "逾期"
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        expression.hover("包含")
        sleep(1)
        expression.select_input_expression(name)
        sleep(1)
        eles = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not expression.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_expression_select4(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = "默认"
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        expression.hover("符合开头")
        sleep(1)
        expression.select_input_expression(name)
        sleep(1)
        eles = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not expression.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_expression_select5(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = "2"
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        expression.hover("符合结尾")
        sleep(1)
        expression.select_input_expression(name)
        sleep(1)
        eles = expression.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not expression.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_expression_clear(self, login_to_expression):
        driver = login_to_expression  # WebDriver 实例
        expression = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        sleep(1)
        name = "3"
        sleep(1)
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        expression.hover("包含")
        sleep(1)
        expression.select_input_expression(name)
        sleep(1)
        expression.click_button('//div[p[text()="名称"]]/following-sibling::div//i')
        expression.hover("清除所有筛选条件")
        sleep(1)
        ele = expression.get_find_element_xpath('//div[p[text()="名称"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not expression.has_fail_message()