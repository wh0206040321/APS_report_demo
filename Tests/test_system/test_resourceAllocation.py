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
from Pages.itemsPage.resource_page import ResourcePage
from Pages.itemsPage.sched_page import SchedPage
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.systemPage.psi_page import PsiPage
from Pages.systemPage.resourceAllocation_page import ResourceAllocationPage
from Pages.systemPage.role_page import RolePage
from Pages.systemPage.synchronize_page import SynchronizePage
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.userRole_page import UserRolePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_resourceAllocation():
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
        list_ = ["系统管理", "单元设置", "资源分配"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("配置同步页用例")
@pytest.mark.run(order=210)
class TestResourceAllocationPage:

    @allure.story("添加新资源数据，后续使用")
    # @pytest.mark.run(order=1)
    def test_resourceAllocation_addresource(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        resource = ResourcePage(driver)
        list_ = ["计划管理", "计划基础数据", "资源"]
        resource_ = ['1测试资源同步数据1', '1测试资源同步数据2']
        for v in list_:
            allocation.click_button(f'(//span[text()="{v}"])[1]')
        resource.add_test_resource(f'{resource_[0]}')
        resource.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        resource.add_test_resource(f'{resource_[1]}')
        resource.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = allocation.get_find_message()
        assert message == "新增成功！"
        assert not allocation.has_fail_message()

    @allure.story("分配一个资源给另外一个用户成功")
    # @pytest.mark.run(order=1)
    def test_resourceAllocation_allocation1(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        user = '1user1'
        resource_ = '1测试资源同步数据1'
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        allocation.select_input('用户代码', user)
        allocation.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{user}"]')
        allocation.click_all_button("编辑")
        allocation.select_input('资源代码', resource_)
        allocation.wait_for_loading_to_disappear()
        allocation.click_button(f'//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{resource_}"]]/td[2]/div/span')
        allocation.click_all_button("保存")
        message = allocation.get_find_message()
        allocation.log_out(name="1user1", password="Qw123456", module="1测试A")
        ele = allocation.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{resource_}"]')
        assert message == "保存成功" and len(ele) == 1
        assert not allocation.has_fail_message()

    @allure.story("分配2个资源给另外一个用户成功")
    # @pytest.mark.run(order=1)
    def test_resourceAllocation_allocation2(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        user = '1user1'
        resource_ = ['1测试资源同步数据1', '1测试资源同步数据2']
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        allocation.select_input('用户代码', user)
        allocation.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{user}"]')
        allocation.click_all_button("编辑")
        allocation.select_input('资源代码', resource_[0])
        allocation.wait_for_loading_to_disappear()
        allocation.click_button(
            f'//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{resource_[0]}"]]/td[2]/div/span')
        allocation.select_input('资源代码', resource_[1])
        allocation.wait_for_loading_to_disappear()
        allocation.click_button(
            f'//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{resource_[1]}"]]/td[2]/div/span')
        allocation.click_all_button("保存")
        message = allocation.get_find_message()
        allocation.log_out(name="1user1", password="Qw123456", module="1测试A")
        ele1 = allocation.finds_elements(By.XPATH,
                                        f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{resource_[0]}"]')
        ele2 = allocation.finds_elements(By.XPATH,
                                         f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{resource_[1]}"]')
        assert message == "保存成功" and len(ele1) == 1 and len(ele2) == 1
        assert not allocation.has_fail_message()

    @allure.story("分配全部资源给另外一个用户成功")
    # @pytest.mark.run(order=1)
    def test_resourceAllocation_allocation3(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        user = '1user1'
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        allocation.select_input('用户代码', user)
        allocation.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{user}"]')
        allocation.click_all_button("编辑")
        allocation.wait_for_loading_to_disappear()
        allocation.click_button(
            f'//table[@class="vxe-table--header"]//tr/th[2]//span[@class="vxe-cell--title"]/span')
        allocation.click_all_button("保存")
        message = allocation.get_find_message()
        allocation.log_out(name="1user1", password="Qw123456", module="1测试A")
        ele = allocation.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[3]')
        assert message == "保存成功" and len(ele) >= 3
        assert not allocation.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_allocation_select1(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        name = "1测试资源同步数据1"
        allocation.select_input('资源代码', name)
        sleep(1)
        eles = allocation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[2]//tr//td[3]')
        list_ = [ele.text for ele in eles]
        assert all(text == name for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not allocation.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_allocation_select2(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        sleep(1)
        eles = allocation.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            allocation.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            allocation.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//input')
        eles = allocation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[2]//tr//td[3]')
        assert len(eles) == 0
        assert not allocation.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_allocation_select3(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        name = "2"
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        allocation.hover("包含")
        sleep(1)
        allocation.select_input('资源代码', name)
        sleep(1)
        eles = allocation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[2]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not allocation.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_allocation_select4(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        name = "1"
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        allocation.hover("符合开头")
        sleep(1)
        allocation.select_input('资源代码', name)
        sleep(1)
        eles = allocation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[2]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not allocation.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_allocation_select5(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        name = "2"
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        allocation.hover("符合结尾")
        sleep(1)
        allocation.select_input('资源代码', name)
        sleep(1)
        eles = allocation.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[2]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not allocation.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_allocation_clear(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        name = "3"
        sleep(1)
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        allocation.hover("包含")
        sleep(1)
        allocation.select_input('资源代码', name)
        sleep(1)
        allocation.click_button('//div[p[text()="资源代码"]]/following-sibling::div//i')
        allocation.hover("清除所有筛选条件")
        sleep(1)
        ele = allocation.get_find_element_xpath('//div[p[text()="资源代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not allocation.has_fail_message()

    @allure.story("删除增加的资源和用户成功")
    # @pytest.mark.run(order=1)
    def test_allocation_del(self, login_to_resourceAllocation):
        driver = login_to_resourceAllocation  # WebDriver 实例
        allocation = ResourceAllocationPage(driver)  # 用 driver 初始化 ResourceAllocationPage
        resource = ResourcePage(driver)
        unit = PlanUnitPage(driver)
        role = RolePage(driver)
        user = UserRolePage(driver)

        list_ = ["计划管理", "计划基础数据", "资源"]
        for v in list_:
            allocation.click_button(f'(//span[text()="{v}"])[1]')
        resource_ = ['1测试资源同步数据1', '1测试资源同步数据2']
        sleep(1)
        resource.del_all(value=resource_, xpath='//p[text()="资源代码"]/ancestor::div[2]//input')

        role_list = ["系统管理", "用户权限管理"]
        for v in role_list:
            allocation.click_button(f'(//span[text()="{v}"])[1]')

        names = ['1user1']
        user.del_(names)
        for name in names:
            xpath = f'(//table[@class="vxe-table--body"])[1]//tr/td[2]//span[text()="{name}"]'
            eles = user.finds_elements(By.XPATH, xpath)
            assert len(eles) == 0, f"用户 {name} 未成功删除"

        role_list = ["角色管理"]
        role_name = [
            "1测试角色代码1",
        ]
        for v in role_list:
            allocation.click_button(f'(//span[text()="{v}"])[1]')
        role.del_all(role_name, '//div[div[p[text()="角色代码"]]]//input')
        role.get_find_message()

        unit_list = ["计划单元"]
        unit_name = [
            "1测试A",
        ]
        for v in unit_list:
            allocation.click_button(f'(//span[text()="{v}"])[1]')
        unit.right_refresh()
        unit.del_all(unit_name, '//p[text()="计划单元"]/ancestor::div[2]//input')
        ele = allocation.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
