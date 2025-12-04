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
def login_to_language():
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
        list_ = ["系统管理", "系统设置", "多语言资源"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("多语言资源页用例")
@pytest.mark.run(order=216)
class TestSLanguagePage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_language_addfail1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        language.add_layout(layout)
        # 获取布局名称的文本元素
        name = language.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        sleep(1)
        language.click_all_button("新增")
        sleep(1)
        language.click_confirm()
        message = language.get_error_message()
        assert layout == name
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not language.has_fail_message()

    @allure.story("新增只填写键值点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_language_addfail2(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Akey1'
        language.wait_for_loading_to_disappear()
        language.click_all_button("新增")
        xpath_list = [
            '//div[@id="ngv2ptwf-g6i7"]//input',
            '//div[@id="407yfa73-d3cx"]//input',
            '//div[@id="vr0fnkfs-s95j"]//input',
            '//div[@id="fhxti76o-86e4"]//input',
        ]
        add.batch_modify_input(xpath_list[:1], name)
        language.click_confirm()
        message = language.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not language.has_fail_message()

    @allure.story("新增填写key值和中英文点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_language_addfail3(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Akey1'
        language.click_all_button("新增")
        xpath_list = [
            '//div[@id="ngv2ptwf-g6i7"]//input',
            '//div[@id="407yfa73-d3cx"]//input',
            '//div[@id="vr0fnkfs-s95j"]//input',
            '//div[@id="fhxti76o-86e4"]//input',
        ]
        add.batch_modify_input(xpath_list[:3], name)
        language.click_confirm()
        message = language.get_error_message()
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not language.has_fail_message()

    @allure.story("添加多语言成功")
    # @pytest.mark.run(order=1)
    def test_language_addsuccess(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Akey1'
        language.click_all_button("新增")
        xpath_list = [
            '//div[@id="ngv2ptwf-g6i7"]//input',
            '//div[@id="407yfa73-d3cx"]//input',
            '//div[@id="vr0fnkfs-s95j"]//input',
            '//div[@id="fhxti76o-86e4"]//input',
        ]
        add.batch_modify_input(xpath_list[:4], name)
        language.click_confirm()
        message = language.get_find_message()
        language.wait_for_loading_to_disappear()
        language.select_input_language(name)
        sleep(1)
        eles = language.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert eles == name
        assert message == "新增成功！"
        assert not language.has_fail_message()

    @allure.story("添加重复key值不允许添加")
    # @pytest.mark.run(order=1)
    def test_language_addrepeat1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Akey1'
        language.click_all_button("新增")
        xpath_list = [
            '//div[@id="ngv2ptwf-g6i7"]//input',
            '//div[@id="407yfa73-d3cx"]//input',
            '//div[@id="vr0fnkfs-s95j"]//input',
            '//div[@id="fhxti76o-86e4"]//input',
        ]
        add.batch_modify_input(xpath_list[:4], name)
        language.click_confirm()
        sleep(1)
        message = language.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').text
        assert message == "记录已存在,请检查！"
        assert not language.has_fail_message()

    @allure.story("修改key值成功")
    # @pytest.mark.run(order=1)
    def test_language_updatesuccess1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        before_name = 'Akey1'
        after_name = 'Akey2'
        language.wait_for_loading_to_disappear()
        language.select_input_language(before_name)
        sleep(1)
        language.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        language.click_all_button("编辑")
        xpath_list = [
            '//div[@id="c7h1w27z-lgyo"]//input',
            '//div[@id="wzcyncq8-0i93"]//input',
            '//div[@id="kn72lcng-iorx"]//input',
            '//div[@id="a5cvq73h-aok8"]//input',
        ]
        add.batch_modify_input(xpath_list[:1], after_name)
        language.click_confirm()
        message = language.get_find_message()
        language.wait_for_loading_to_disappear()
        language.select_input_language(after_name)
        sleep(2)
        eles2 = language.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{after_name}"]').text
        assert eles2 == after_name
        assert message == "编辑成功！"
        assert not language.has_fail_message()

    @allure.story("添加测试数据多语言成功")
    # @pytest.mark.run(order=1)
    def test_language_addsuccess1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'Akey1'
        language.click_all_button("新增")
        xpath_list = [
            '//div[@id="ngv2ptwf-g6i7"]//input',
            '//div[@id="407yfa73-d3cx"]//input',
            '//div[@id="vr0fnkfs-s95j"]//input',
            '//div[@id="fhxti76o-86e4"]//input',
        ]
        add.batch_modify_input(xpath_list[:4], name)
        language.click_confirm()
        message = language.get_find_message()
        language.wait_for_loading_to_disappear()
        language.select_input_language(name)
        sleep(2)
        eles = language.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        assert eles == name
        assert message == "新增成功！"
        assert not language.has_fail_message()

    @allure.story("修改中英日值成功")
    # @pytest.mark.run(order=1)
    def test_language_updatesuccess2(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        before_name = 'Akey1'
        after_name = 'Akey2'
        language.wait_for_loading_to_disappear()
        language.select_input_language(before_name)
        sleep(1)
        language.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        language.click_all_button("编辑")
        xpath_list = [
            '//div[@id="wzcyncq8-0i93"]//input',
            '//div[@id="kn72lcng-iorx"]//input',
            '//div[@id="a5cvq73h-aok8"]//input',
        ]
        add.batch_modify_input(xpath_list[:3], after_name)
        language.click_confirm()
        message = language.get_find_message()
        language.wait_for_loading_to_disappear()
        language.select_input_language(before_name)
        sleep(2)
        eles1 = language.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[3]').text
        eles2 = language.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[4]').text
        eles3 = language.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[5]').text
        assert eles1 == eles2 == eles3 == after_name
        assert message == "编辑成功！"
        assert not language.has_fail_message()

    @allure.story("修改key值不允许重复")
    # @pytest.mark.run(order=1)
    def test_language_updaterepeat1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        before_name = 'Akey1'
        after_name = 'Akey2'
        language.wait_for_loading_to_disappear()
        language.select_input_language(before_name)
        sleep(1)
        language.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        language.click_all_button("编辑")
        xpath_list = [
            '//div[@id="c7h1w27z-lgyo"]//input',
            '//div[@id="wzcyncq8-0i93"]//input',
            '//div[@id="kn72lcng-iorx"]//input',
            '//div[@id="a5cvq73h-aok8"]//input',
        ]
        add.batch_modify_input(xpath_list[:1], after_name)
        language.click_confirm()
        message = language.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').text
        assert message == "记录已存在,请检查！"
        assert not language.has_fail_message()

    # @allure.story("查询key值成功")
    # # @pytest.mark.run(order=1)
    # def test_language_selectsuccess(self, login_to_language):
    #     driver = login_to_language  # WebDriver 实例
    #     language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
    #     name = "Item_Spec1Code"
    #     # 点击查询
    #     language.click_all_button("查询")
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
    #     language.click_button('//div[text()="键" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     language.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     language.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     language.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     language.click_button(
    #         '(//div[@class="demo-drawer-footer"])[2]/button[2]'
    #     )
    #     sleep(2)
    #     # 定位第一行是否为name
    #     itemcode = language.get_find_element_xpath(
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
    #     ).text
    #     # 定位第二行没有数据
    #     itemcode2 = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
    #     )
    #     assert itemcode == name and len(itemcode2) == 0
    #     assert not language.has_fail_message()
    #
    # @allure.story("没有数据时显示正常")
    # # @pytest.mark.run(order=1)
    # def test_language_selectnodatasuccess(self, login_to_language):
    #     driver = login_to_language  # WebDriver 实例
    #     language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     # 点击查询
    #     language.click_all_button("查询")
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
    #     language.click_button('//div[text()="键" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     language.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     language.click_button('//div[text()="=" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     language.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         "没有数据",
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     language.click_button(
    #         '(//div[@class="demo-drawer-footer"])[2]/button[2]'
    #     )
    #     sleep(2)
    #     itemcode = driver.find_elements(
    #         By.XPATH,
    #         '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
    #     )
    #     assert len(itemcode) == 0
    #     assert not language.has_fail_message()
    #
    # @allure.story("查询中文包含物料成功")
    # # @pytest.mark.run(order=1)
    # def test_language_selectnamesuccess(self, login_to_language):
    #     driver = login_to_language  # WebDriver 实例
    #     language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
    #
    #     name = "物料"
    #     # 点击查询
    #     language.click_all_button("查询")
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
    #     language.click_button('//div[text()="中文" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击比较关系框
    #     language.click_button(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
    #     )
    #     sleep(1)
    #     # 点击=
    #     language.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
    #     sleep(1)
    #     # 点击输入数值
    #     language.enter_texts(
    #         '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
    #         name,
    #     )
    #     sleep(1)
    #
    #     # 点击确认
    #     language.click_button(
    #         '(//div[@class="demo-drawer-footer"])[2]/button[2]'
    #     )
    #     sleep(2)
    #     eles = language.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
    #     assert len(eles) > 0
    #     assert all(name in ele for ele in eles)
    #     assert not language.has_fail_message()

    @allure.story("过滤查组件代码成功")
    # @pytest.mark.run(order=1)
    def test_language_select1(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        language.wait_for_loading_to_disappear()
        name = "Akey"
        sleep(1)
        language.select_input_language(name)
        sleep(2)
        eles = language.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not language.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_language_select2(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        language.wait_for_loading_to_disappear()
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        eles = language.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            language.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            language.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//input')
        eles = language.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not language.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_language_select3(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        language.wait_for_loading_to_disappear()
        name = "Akey"
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        language.hover("包含")
        sleep(1)
        language.select_input_language(name)
        sleep(1)
        eles = language.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not language.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_language_select4(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "Plan"
        language.wait_for_loading_to_disappear()
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        language.hover("符合开头")
        sleep(1)
        language.select_input_language(name)
        sleep(1)
        eles = language.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not language.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_language_select5(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        language.wait_for_loading_to_disappear()
        name = "ss"
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        language.hover("符合结尾")
        sleep(1)
        language.select_input_language(name)
        sleep(1)
        eles = language.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not language.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_language_clear(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        language.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        language.hover("包含")
        sleep(1)
        language.select_input_language(name)
        sleep(1)
        language.click_button('//div[div[span[text()=" 键"]]]/div[3]//i')
        language.hover("清除所有筛选条件")
        sleep(1)
        ele = language.get_find_element_xpath('//div[div[span[text()=" 键"]]]/div[3]//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not language.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_language_delsuccess(self, login_to_language):
        driver = login_to_language  # WebDriver 实例
        language = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        language.wait_for_loading_to_disappear()
        value = ['Akey1','Akey2']
        language.del_all(xpath='//div[div[span[text()=" 键"]]]/div[3]//input', value=value)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:1]
        ]
        language.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in itemdata)
        assert 0 == len(after_layout)
        assert not language.has_fail_message()