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
from Pages.systemPage.database_page import DateBasePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_database():
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
        list_ = ["系统管理", "系统设置", "数据库维护"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("数据库维护页用例")
@pytest.mark.run(order=218)
class TestSDateBasePage:

    @allure.story("填写表代码点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_database_addfail1(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        data.add_table_code(button_name='新增', code='111')
        data.click_all_button("保存")
        message = data.get_error_message()
        assert message == "请填写表信息和字段信息"
        assert not data.has_fail_message()

    @allure.story("添加表成功")
    # @pytest.mark.run(order=1)
    def test_database_addsuccess(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        name = 'AAtest1'
        data.add_table_code(button_name='新增', code=name, field_code=name, fieldbutton_name='添加')
        message = data.get_find_message()
        data.select_input_database("表代码", name)
        sleep(1)
        ele = data.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert message == "保存成功"
        assert ele == name
        assert not data.has_fail_message()

    @allure.story("添加重复表代码不允许添加")
    # @pytest.mark.run(order=1)
    def test_database_addreport(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        name = 'AAtest1'
        data.add_table_code(button_name='新增', code=name, field_code=name, fieldbutton_name='添加')
        sleep(2)
        message = data.get_find_element_xpath('//div[text()=" 表已存在 "]').text
        assert message == "表已存在"
        assert not data.has_fail_message()

    @allure.story("添加字段代码成功")
    # @pytest.mark.run(order=1)
    def test_database_addcodesuccess(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        code = 'AAtest1'
        name = 'AAtest2'
        data.add_table_code(button_name='编辑', code=code, field_code=name, fieldbutton_name='添加')
        message = data.get_find_message()
        data.select_input_database("表代码", code)
        data.click_button(f'(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]//span[text()="{code}"]')
        data.click_all_button("编辑")
        sleep(2)
        eles = data.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[3]//tr/td[2]')
        assert len(eles) == 2
        assert message == "保存成功"
        assert not data.has_fail_message()

    @allure.story("添加重复字段代码不允许添加")
    # @pytest.mark.run(order=1)
    def test_database_addcoderepeat(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        code = 'AAtest1'
        name = 'AAtest2'
        data.add_table_code(button_name='编辑', code=code, field_code=name, fieldbutton_name='添加')
        message = data.get_error_message()
        assert message == '字段代码或者字段名称已经存在，不能再次创建！'
        assert not data.has_fail_message()

    @allure.story("编辑字段代码不允许重复")
    # @pytest.mark.run(order=1)
    def test_database_editfieldreport(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        add = AddsPages(driver)
        code = 'AAtest1'
        name = 'AAtest2'
        xpath_list = [
            '//div[label[text()="字段代码"]]//input',
            '//div[label[text()="字段名称"]]//input',
            '//div[label[text()="类型"]]//i',
            '//li[text()="整型"]',
        ]
        data.add_table_code(button_name='编辑', code=code, field_code=name, fieldbutton_name='编辑')
        add.batch_modify_input(xpath_list[:2], code)
        data.click_confirm()
        message = data.get_error_message()
        assert message == "字段代码或者字段名称已经存在，不能再次创建！"
        assert not data.has_fail_message()

    @allure.story("编辑字段代码成功")
    # @pytest.mark.run(order=1)
    def test_database_editsuccess(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        add = AddsPages(driver)
        code = 'AAtest1'
        name = 'AAtest2'
        xpath_list = [
            '//div[label[text()="字段代码"]]//input',
            '//div[label[text()="字段名称"]]//input',
            '//div[label[text()="类型"]]//i',
            '//li[text()="整型"]',
        ]
        data.add_table_code(button_name='编辑', code=code, field_code=name, fieldbutton_name='编辑')
        add.batch_modify_input(xpath_list[:2], code + name)
        data.click_button(xpath_list[2])
        data.click_button(xpath_list[3])
        data.click_confirm()
        data.click_all_button("保存")
        message = data.get_find_message()
        data.select_input_database("表代码", code)
        data.click_button(f'(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]//span[text()="{code}"]')
        data.click_all_button("编辑")
        sleep(2)
        eles = data.get_find_element_xpath(f'(//table[@class="vxe-table--body"])[3]//tr/td[2]//span[text()="{code+name}"]').text
        elesint = data.get_find_element_xpath(f'(//table[@class="vxe-table--body"])[3]//tr[td[3][//span[text()="{code+name}"]]]/td[4]').text
        assert eles == code+name and elesint == 'int'
        assert message == "保存成功"
        assert not data.has_fail_message()

    @allure.story("删除字段代码成功")
    # @pytest.mark.run(order=1)
    def test_database_delfield(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        code = 'AAtest1'
        name = 'AAtest2'
        data.add_table_code(button_name='编辑', code=code, field_code=code+name, fieldbutton_name='删除')
        message = data.get_find_message()
        data.right_refresh()
        sleep(1)
        data.select_input_database("表代码", code)
        sleep(1)
        data.click_button(f'(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]//span[text()="{code}"]')
        sleep(3)
        data.click_all_button("编辑")
        sleep(2)
        eles = data.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[3]//tr/td[2]')
        assert len(eles) == 1
        assert message == "保存成功"
        assert not data.has_fail_message()

    @allure.story("同步单表成功")
    # @pytest.mark.run(order=1)
    def test_database_synchronize1(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        data.click_synchronize_button("同步单表")
        message = data.get_find_message()
        assert message == "同步成功"
        assert not data.has_fail_message()

    @allure.story("同步所有表成功")
    # @pytest.mark.run(order=1)
    def test_database_synchronize2(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        data.click_synchronize_button("同步所有")
        message = data.get_find_message()
        assert message == "同步成功"
        assert not data.has_fail_message()

    @allure.story("数据库查询成功")
    # @pytest.mark.run(order=1)
    def test_database_dataselect1(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        name = 'APS_Item'
        data.click_select_button()
        data.enter_texts('//div[@class="content-siadeNav"]//input[@placeholder="请输入"]', name)
        sleep(1)
        eles = data.finds_elements(By.XPATH, '(//div[@class="content-siadeNav"]//div[@role="group"])[2]/div/div/span[2]')
        list_name = [ele.text for ele in eles]
        assert all(name in ele for ele in list_name)
        assert not data.has_fail_message()

    @allure.story("新增新建查询页面成功，并且执行查询数据库成功")
    # @pytest.mark.run(order=2)
    def test_database_dataselect2(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        text = 'SELECT DB_NAME();'
        data.click_select_button()
        data.click_button('//p[text()="新建查询"]')
        sleep(1)
        ele = data.get_find_element_xpath('(//textarea[@tabindex="0"])[2]')
        ele.send_keys(text)
        data.click_button('//p[text()="执行"]')
        sleep(1)
        num = data.finds_elements(By.XPATH, '//div[@role="tablist"]/div')
        eles = data.finds_elements(By.XPATH, '//table[@class="vxe-table--header"]//span[text()="序号"]')
        assert len(num) == 2 and len(eles) == 1
        assert not data.has_fail_message()

    @allure.story("过滤表名成功")
    # @pytest.mark.run(order=1)
    def test_database_select1(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        database.wait_for_loading_to_disappear()
        name = "AMRP"
        database.enter_texts('//div[div[p[text()="表名"]]]//input', name)
        sleep(2)
        eles = database.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[3]')
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not database.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_database_select2(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        database.wait_for_loading_to_disappear()
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        sleep(1)
        eles = database.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            database.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            database.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        eles = database.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        assert len(eles) == 0
        assert not database.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_database_select3(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        database.wait_for_loading_to_disappear()
        name = "Master"
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        database.hover("包含")
        sleep(1)
        database.select_input_database('表代码', name)
        sleep(1)
        eles = database.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not database.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_database_select4(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        name = "APS"
        database.wait_for_loading_to_disappear()
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        database.hover("符合开头")
        sleep(1)
        database.select_input_database('表代码', name)
        sleep(1)
        eles = database.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not database.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_database_select5(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        database.wait_for_loading_to_disappear()
        name = "Master"
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        database.hover("符合结尾")
        sleep(1)
        database.select_input_database('表代码', name)
        sleep(1)
        eles = database.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not database.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_database_clear(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        database = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        database.wait_for_loading_to_disappear()
        name = "3"
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        database.hover("包含")
        sleep(1)
        database.select_input_database('表代码', name)
        sleep(1)
        database.click_button('//div[p[text()="表代码"]]/following-sibling::div//i')
        database.hover("清除所有筛选条件")
        sleep(1)
        ele = database.get_find_element_xpath('//div[p[text()="表代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not database.has_fail_message()

    @allure.story("删除表数据成功")
    # @pytest.mark.run(order=1)
    def test_database_delfieldtable(self, login_to_database):
        driver = login_to_database  # WebDriver 实例
        data = DateBasePage(driver)  # 用 driver 初始化 DateBasePage
        code = 'AAtest1'
        data.wait_for_loading_to_disappear()
        data.select_input_database("表代码", code)
        sleep(1.5)
        data.click_button(f'(//table[@class="vxe-table--body"])[1]//tr[1]/td[2]//span[text()="{code}"]')
        data.click_all_button("删除")
        data.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = data.get_find_message()
        data.select_input_database("表代码", code)
        sleep(1)
        eles = data.finds_elements(By.XPATH, f'(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        assert len(eles) == 0
        assert message == "删除成功！"
        assert not data.has_fail_message()