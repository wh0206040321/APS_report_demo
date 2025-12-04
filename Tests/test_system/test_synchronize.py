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
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.systemPage.psi_page import PsiPage
from Pages.systemPage.role_page import RolePage
from Pages.systemPage.synchronize_page import SynchronizePage
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.userRole_page import UserRolePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_synchronize():
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
        list_ = ["系统管理", "单元设置", "配置同步"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("配置同步页用例")
@pytest.mark.run(order=208)
class TestSynchronizePage:

    @allure.story("不勾选单元点击同步弹出错误提示")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_numsel(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        synchronize.click_synchronize_button()
        message = synchronize.get_error_message()
        assert message == "请勾选当前和目的计划单元"
        assert not synchronize.has_fail_message()

    @allure.story("同步单个psi成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_psi(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi_names = [
            "1测试psi1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(psi_names, plan_names, "1")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 1)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("重复同步同一个psi不会报错，会继续同步")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_repeatpsi(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi_names = [
            "1测试psi1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(psi_names, plan_names, "1")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 1)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个psi到一个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_psis1(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi_names = [
            "1测试psi1",
            "1测试psi2",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(psi_names, plan_names, "1")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 1)

        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步1个psi到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_psis2(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi_names = [
            "1测试psi3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(psi_names, plan_names, "1")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 1)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 1, js=False)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个psi到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_psis3(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi_names = [
            "1测试psi1",
            "1测试psi2",
            "1测试psi3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(psi_names, plan_names, "1")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 1)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 1, js=False)
        for psi_name in psi_names:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{psi_name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个 PSI：{psi_name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步单个计划方案成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_plan(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "排产方案(订单级)同步1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "2")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 2)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("重复同步同一个计划方案不会报错，会继续同步")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_repeatplan(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "排产方案(订单级)同步1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "2")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 2)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个计划方案到一个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_plan1(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "排产方案(订单级)同步1",
            "排产方案(订单级)同步2",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "2")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 2)

        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步1个计划方案到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_plan2(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "排产方案(订单级)同步3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "2")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 2)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 2, js=False)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个计划方案到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_plan3(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "排产方案(订单级)同步1",
            "排产方案(订单级)同步2",
            "排产方案(订单级)同步3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "2")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 2)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 2, js=False)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//span[text()="{name}" and @class="ivu-tree-title"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步单个物控计划方案成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_materialplan(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "物控方案(订单级)同步1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "3")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 3)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("重复同步同一个计划方案不会报错，会继续同步")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_materialrepeatplan(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "物控方案(订单级)同步1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "3")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 3)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个计划方案到一个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_materialplan1(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "物控方案(订单级)同步1",
            "物控方案(订单级)同步2",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "3")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 3)

        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步1个计划方案到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_materialplan2(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "物控方案(订单级)同步3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "3")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 3)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 3, js=False)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个计划方案到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_materialplan3(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        plan_name = [
            "物控方案(订单级)同步1",
            "物控方案(订单级)同步2",
            "物控方案(订单级)同步3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(plan_name, plan_names, "3")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 3)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 3, js=False)
        for name in plan_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'//label[text()="{name}"]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步单个数据导入成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_import(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        import_name = [
            "1同步导入1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(import_name, plan_names, "4")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 4)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("重复同步同一个数据导入不会报错，会继续同步")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_repeatimport(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        import_name = [
            "1同步导入1",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(import_name, plan_names, "4")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 4)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个数据导入到一个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_import1(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        import_name = [
            "1同步导入1",
            "1同步导入2",
        ]
        plan_names = [
            "1测试计划单元标准",
        ]
        synchronize.click_checkbox_value(import_name, plan_names, "4")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 4)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步1个数据导入到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_import2(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        import_name = [
            "1同步导入3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(import_name, plan_names, "4")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 4)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 4, js=False)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("同步多个数据导入到多个计划单元成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_all_import3(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        import_name = [
            "1同步导入1",
            "1同步导入2",
            "1同步导入3",
        ]
        plan_names = [
            "1测试计划单元标准",
            "1测试A",
        ]
        synchronize.click_checkbox_value(import_name, plan_names, "4")
        synchronize.click_synchronize_button()
        synchronize.click_synchronize_pop(True)
        message = synchronize.get_find_message()
        synchronize.switch_plane(plan_names[0], 4)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        synchronize.click_button(f'//div[contains(text(),"{plan_names[0]}")]')
        synchronize.switch_plane(plan_names[1], 4, js=False)
        synchronize.click_button('//input[@class="ivu-select-input" and @placeholder="请选择"]')
        for name in import_name:
            elements = synchronize.finds_elements(
                By.XPATH,
                f'(//li[text()="{name}"])[1]'
            )
            assert len(elements) == 1, f"未找到或找到多个{name}"
        assert message == "同步成功"
        assert not synchronize.has_fail_message()

    @allure.story("删除psi，计划方案，导入设置，计划单元所有数据成功")
    # @pytest.mark.run(order=1)
    def test_synchronize_delall(self, login_to_synchronize):
        driver = login_to_synchronize  # WebDriver 实例
        synchronize = SynchronizePage(driver)  # 用 driver 初始化 SynchronizePage
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        imp = ImpPage(driver)
        sched = SchedPage(driver)
        unit = PlanUnitPage(driver)
        role = RolePage(driver)
        user = UserRolePage(driver)
        username = DateDriver().username
        synchronize.click_button('(//span[text()="PSI设置"])[1]')
        sleep(1)
        psi_name = ["1测试psi1", "1测试psi2", "1测试psi3"]
        psi.del_all(psi_name)
        for v in psi_name:
            eles = synchronize.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{v}"]')
            assert len(eles) == 0, f"未删除{v}"

        plan_list =["计划运行", "方案管理", "计划方案管理"]
        for v in plan_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')
        plan_name = [
            "排产方案(订单级)同步1",
            "排产方案(订单级)同步2",
            "排产方案(订单级)同步3",
        ]
        sched.del_all_sched(plan_name)
        for v in plan_name:
            eles = synchronize.finds_elements(By.XPATH, f'(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="{v}"]')
            assert len(eles) == 0, f"未删除{v}"

        plan_list = ["物控方案管理"]
        for v in plan_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')
        plan_name = [
            "物控方案(订单级)同步1",
            "物控方案(订单级)同步2",
            "物控方案(订单级)同步3",
        ]
        sched.del_all_sched(plan_name)
        for v in plan_name:
            eles = synchronize.finds_elements(By.XPATH,
                                              f'(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="{v}"]')
            assert len(eles) == 0, f"未删除{v}"

        import_list = ["数据接口底座", "DBLinK", "导入设置"]
        import_name = [
            "1同步导入1",
            "1同步导入2",
            "1同步导入3",
        ]
        for v in import_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')
        imp.del_all(import_name)
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        for v in import_list:
            eles = synchronize.finds_elements(By.XPATH,
                                              f'(//ul[@class="ivu-select-dropdown-list"])[1]/li[text()="{v}"]')
            assert len(eles) == 0, f"未删除{v}"
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')

        role_list = ["系统管理", "系统设置", "用户权限管理"]
        for v in role_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')

        names = ["1测试角色代码1", "1测试角色代码3"]
        # 取消当前用户选中的角色
        user.select_input(username)
        user.click_button(f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{username}"]')
        sleep(1)
        user.click_all_button("编辑")
        sleep(1)
        for name in names:
            xpath = '//div[div[p[text()="角色代码"]]]//input'
            ele = synchronize.get_find_element_xpath(xpath)
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.DELETE)
            user.enter_texts('//div[div[p[text()="角色代码"]]]//input', name)
            sleep(3)
            eles = synchronize.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox is--checked"]')
            if len(eles) == 1:
                synchronize.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox is--checked"]')

        user.click_all_button("保存")
        user.get_find_message()

        role_list = ["角色管理"]
        role_name = [
            "1测试角色代码3",
        ]
        for v in role_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')
        role.del_all(role_name)
        role.get_find_message()

        unit_list = ["计划单元"]

        unit_name = [
            "1测试计划单元标准",
        ]
        for v in unit_list:
            synchronize.click_button(f'(//span[text()="{v}"])[1]')
        unit.right_refresh()
        unit.del_all(unit_name)
        ele = synchronize.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not synchronize.has_fail_message()