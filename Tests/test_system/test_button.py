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
from Pages.systemPage.expression_page import ExpressionPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_button():
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
        list_ = ["系统管理", "系统设置", "工具栏按钮管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("工具栏按钮管理页用例")
@pytest.mark.run(order=217)
class TestSButtonPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_button_addfail1(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        button.add_layout(layout)
        # 获取布局名称的文本元素
        name = button.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        sleep(1)
        button.click_all_button("新增")
        sleep(1)
        button.click_confirm()
        message = button.get_error_message()
        assert layout == name
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not button.has_fail_message()

    @allure.story("新增只填写按钮代码点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_button_addfail2(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Abutton1'
        button.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:1], name)
        button.click_confirm()
        message = button.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not button.has_fail_message()

    @allure.story("新增填写按钮代码和按钮名称点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_button_addfail3(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Abutton1'
        button.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        button.click_confirm()
        message = button.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not button.has_fail_message()

    @allure.story("添加按钮成功")
    # @pytest.mark.run(order=1)
    def test_button_addsuccess(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Abutton1'
        button.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        add.click_button(xpath_list[2])
        add.click_button(xpath_list[3])
        button.click_confirm()
        message = button.get_find_message()
        button.select_input_button(name)
        eles = button.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert eles == name
        assert message == "新增成功！"
        assert not button.has_fail_message()

    @allure.story("添加重复按钮代码不允许添加")
    # @pytest.mark.run(order=1)
    def test_button_addrepeat1(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Abutton1'
        button.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        add.click_button(xpath_list[2])
        add.click_button(xpath_list[3])
        button.click_confirm()
        sleep(1)
        message = button.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').text
        assert message == "记录已存在,请检查！"
        assert not button.has_fail_message()

    @allure.story("修改对话框按钮代码禁用")
    # @pytest.mark.run(order=1)
    def test_button_updateenabled(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        before_name = 'Abutton1'
        button.wait_for_loading_to_disappear()
        button.select_input_button(before_name)
        sleep(1)
        button.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        button.click_all_button("编辑")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        sleep(1)
        ele = button.get_find_element_xpath(xpath_list[0])
        assert not ele.is_enabled()
        assert not button.has_fail_message()

    @allure.story("添加测试按钮成功")
    # @pytest.mark.run(order=1)
    def test_button_addsuccess1(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Abutton2'
        button.click_all_button("新增")
        xpath_list = [
            '//div[label[text()="按钮代码"]]//input',
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        add.click_button(xpath_list[2])
        add.click_button(xpath_list[3])
        button.click_confirm()
        message = button.get_find_message()
        button.select_input_button(name)
        sleep(1)
        eles = button.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert eles == name
        assert message == "新增成功！"
        assert not button.has_fail_message()

    @allure.story("修改按钮名称和图标成功")
    # @pytest.mark.run(order=1)
    def test_button_updatesuccess2(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        before_name = 'Abutton1'
        after_name = 'Abutton2'
        button.wait_for_loading_to_disappear()
        button.select_input_button(before_name)
        button.wait_for_loading_to_disappear()
        button.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        button.click_all_button("编辑")
        xpath_list = [
            '//div[label[text()="按钮名称"]]//input',
            '//div[label[text()="图标"]]//i[contains(@class,"ivu-ico")]',
            '(//div[@class="flex-wrap"])[2]/div[2]',
        ]
        add.batch_modify_input(xpath_list[:1], after_name)
        add.click_button(xpath_list[1])
        add.click_button(xpath_list[2])
        button.click_confirm()
        message = button.get_find_message()
        button.select_input_button(after_name)
        button.wait_for_loading_to_disappear()
        eles1 = button.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[3]').text
        assert eles1 == after_name
        assert message == "编辑成功！"
        assert not button.has_fail_message()

    @allure.story("查询按钮代码成功")
    # @pytest.mark.run(order=1)
    def test_button_selectsuccess(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "DownLoad"
        # 点击查询
        button.click_all_button("查询")
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
        button.click_button('//div[text()="按钮代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        button.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        button.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        button.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        button.click_select_button()
        # 定位第一行是否为name
        itemcode = button.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert itemcode == name and len(itemcode2) == 0
        assert not button.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_button_selectnodatasuccess(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        # 点击查询
        button.click_all_button("查询")
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
        button.click_button('//div[text()="按钮代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        button.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        button.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        button.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        button.click_select_button()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        assert len(itemcode) == 0
        assert not button.has_fail_message()

    @allure.story("查询按钮名称包含上传成功")
    # @pytest.mark.run(order=1)
    def test_button_selectnamesuccess(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "上传"
        # 点击查询
        button.click_all_button("查询")
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
        # 点击物料名称
        button.click_button('//div[text()="按钮名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        button.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        button.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        button.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        button.click_select_button()
        eles = button.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not button.has_fail_message()

    @allure.story("过滤查按钮代码成功")
    # @pytest.mark.run(order=1)
    def test_button_select1(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.wait_for_loading_to_disappear()
        name = "Sy"
        sleep(1)
        button.select_input_button(name)
        sleep(2)
        eles = button.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not button.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_button_select2(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.wait_for_loading_to_disappear()
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        eles = button.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            button.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            button.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//input')
        eles = button.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not button.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_button_select3(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.wait_for_loading_to_disappear()
        name = "Sy"
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        button.hover("包含")
        sleep(1)
        button.select_input_button(name)
        sleep(1)
        eles = button.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not button.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_button_select4(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "F"
        button.wait_for_loading_to_disappear()
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        button.hover("符合开头")
        sleep(1)
        button.select_input_button(name)
        sleep(1)
        eles = button.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not button.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_button_select5(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.wait_for_loading_to_disappear()
        name = "d"
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        button.hover("符合结尾")
        sleep(1)
        button.select_input_button(name)
        sleep(1)
        eles = button.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not button.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_button_clear(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        button.hover("包含")
        sleep(1)
        button.select_input_button(name)
        sleep(1)
        button.click_button('//div[p[text()="按钮代码"]]/following-sibling::div//i')
        button.hover("清除所有筛选条件")
        sleep(1)
        ele = button.get_find_element_xpath('//div[p[text()="按钮代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not button.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_button_delsuccess(self, login_to_button):
        driver = login_to_button  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        button.wait_for_loading_to_disappear()
        value = ['Abutton1', 'Abutton2']
        button.del_all(xpath='//div[p[text()="按钮代码"]]/following-sibling::div//input', value=value)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:1]
        ]
        button.del_layout(layout)
        sleep(3)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in itemdata)
        assert 0 == len(after_layout)
        assert not button.has_fail_message()