import logging
import os
from datetime import datetime
from time import sleep
from datetime import date
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
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.other_page import OtherPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_interfaceexecution():
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
        list_ = ["数据接口底座", "WebAPI", "接口执行"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("接口执行页用例")
@pytest.mark.run(order=229)
class TestsInterfaceExecutionPage:

    @allure.story("不勾选数据点击执行弹出提示")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_addfail(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.click_button('//button[span[text()="接口执行"]]')
        message = interface.get_error_message()
        assert message == "请选择执行的接口"
        assert not interface.has_fail_message()

    @allure.story("勾选数据点击执行成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_addsuccess(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        wait = WebDriverWait(driver, 120)  # 最长等待 120 秒
        interface.wait_for_loading_to_disappear()
        interface.click_button('//table[@class="vxe-table--header"]//th[2]/div/span[@class="vxe-cell--title"]')
        sleep(1)
        interface.click_button('//button[span[text()="接口执行"]]')
        wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="vxe-modal--wrapper type--modal is--animat lock--view is--resize is--mask is--visible is--active"]')
            )
        )
        ele = interface.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not interface.has_fail_message()

    # @allure.story("点击导出不报错")
    # # @pytest.mark.run(order=1)
    # def test_interfaceexecution_export(self, login_to_interfaceexecution):
    #     driver = login_to_interfaceexecution  # WebDriver 实例
    #     interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
    #     interface.wait_for_loading_to_disappear()
    #     interface.click_button('//button[span[text()="导出"]]')
    #     ele = interface.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
    #     assert len(ele) == 0
    #     assert not interface.has_fail_message()

    @allure.story("点击接口参数成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_parameter(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        interface.mover_right()
        interface.click_button('//button[span[text()="接口参数"]]')
        text = interface.finds_elements(By.XPATH, '//div[text()="接口参数编辑"]')
        ele = interface.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0 and len(text) == 1
        assert not interface.has_fail_message()

    @allure.story("点击接口数据查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_data(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        interface.mover_right()
        interface.click_button('//button[span[text()="接口数据"]]')
        interface.click_button('//button[span[text()="查询"]]')
        interface.wait_for_loading_to_disappear()
        ele = interface.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not interface.has_fail_message()

    @allure.story("点击接口运行日志查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_log(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        interface.mover_right()
        interface.click_button('//button[span[text()="运行日志"]]')
        interface.click_button('//button[span[text()="查询"]]')
        interface.wait_for_loading_to_disappear()
        ele = interface.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not interface.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_select1(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        sleep(1)
        eles = interface.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            interface.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            interface.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//input')
        eles = interface.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not interface.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_select2(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        name = "1测试"
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interface.hover("包含")
        sleep(1)
        interface.select_input(name)
        sleep(1)
        eles = interface.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert len(list_) > 0
        assert all(text == '' or name in text for text in list_)
        assert not interface.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_select3(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        name = "1"
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interface.hover("符合开头")
        sleep(1)
        interface.select_input(name)
        sleep(1)
        eles = interface.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert len(list_) > 0
        assert all(item == '' or str(item).startswith(name) for item in list_)
        assert not interface.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_select4(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        name = "2"
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interface.hover("符合结尾")
        sleep(1)
        interface.select_input(name)
        sleep(1)
        eles = interface.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[5]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert len(list_) > 0
        assert all(item == '' or str(item).endswith(name) for item in list_)
        assert not interface.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_clear(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interface.hover("包含")
        sleep(1)
        interface.select_input(name)
        sleep(1)
        interface.click_button('//div[p[text()="接口名称"]]/following-sibling::div//i')
        interface.hover("清除所有筛选条件")
        sleep(1)
        ele = interface.get_find_element_xpath('//div[p[text()="接口名称"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not interface.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_interfaceexecution_del(self, login_to_interfaceexecution):
        driver = login_to_interfaceexecution  # WebDriver 实例
        interface = ImpPage(driver)  # 用 driver 初始化 ImpPage
        interface.click_button('(//span[text()="接口配置分发"])[1]')
        sleep(1)
        list_ = ['测试数据22', '11测试全部数据']
        for name in list_:
            xpath = '//p[text()="接口名称"]/ancestor::div[2]//input'
            interface.enter_texts(xpath, name)
            sleep(0.5)
            interface.click_button(f'//table[@class="vxe-table--body"]//tr/td[4]//span[text()="{name}"]')
            interface.click_all_button('删除')
            interface.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            message = interface.get_find_message()
            ele = interface.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[4]//span[text()="{name}"]')
            assert len(ele) == 0
            assert message == "删除成功！"
            interface.right_refresh('接口配置分发')
        assert not interface.has_fail_message()