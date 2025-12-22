import logging
import os
import pyautogui
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
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.systemPage.userRole_page import UserRolePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_imp():
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
        list_ = ["数据接口底座", "DBLinK", "导入设置"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("导入设置页用例")
@pytest.mark.run(order=207)
class TestImpPage:

    @allure.story("点击新增不输入数据点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_addfail1(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        imp.click_impall_button("新增")
        imp.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = imp.get_error_message()
        assert message == "请输入方案且不能与其他方案相同"
        assert not imp.has_fail_message()

    @allure.story("点击新增方案成功")
    # @pytest.mark.run(order=1)
    def test_imp_addsuccess(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        imp.add_imp(name)
        message = imp.get_find_message()
        sleep(2)
        value = imp.get_find_element_xpath('//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        assert message == "新增成功！" and value.get_attribute("value") == name
        assert not imp.has_fail_message()

    @allure.story("文本框的校验")
    # @pytest.mark.run(order=1)
    def test_imp_textverify(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        imp.add_imp(name)
        message = imp.get_find_message()
        sleep(2)
        value = imp.get_find_element_xpath(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        assert message == "新增成功！" and value.get_attribute("value") == name
        assert not imp.has_fail_message()

    @allure.story("添加重复方案，提示重复")
    # @pytest.mark.run(order=1)
    def test_imp_addrepeat(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        imp.add_imp(name)
        message = imp.get_error_message()
        assert message == "请输入方案且不能与其他方案相同"
        assert not imp.has_fail_message()

    @allure.story("不勾选任何，点击保存不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_addrepeat(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//ul/li[text()="{name}"]'))).click()
        imp.click_button('//ul[@class="ivu-tree-children"]//span[text()="导入"]')
        imp.click_impall_button("编辑")
        sleep(1)
        imp.click_impall_button("保存")
        message = imp.get_error_message()
        assert message == "请选择导入节点"
        assert not imp.has_fail_message()

    @allure.story("设置导入方案勾选工序成功")
    # @pytest.mark.run(order=1)
    def test_imp_ticksuccess1(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        kh = "客户"
        imp.click_button('//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//ul/li[text()="{name}"]'))).click()
        imp.click_button('//ul[@class="ivu-tree-children"]//span[text()="导入"]')
        imp.click_impall_button("编辑")
        sleep(1)
        imp.click_button(f'//ul[@class="ivu-tree-children"]//span[text()="{kh}"]/ancestor::ul[1]//label/span')
        ele = imp.get_find_element_xpath(f'//ul[@class="ivu-tree-children"]//span[text()="{kh}"]')
        ActionChains(driver).context_click(ele).perform()
        imp.click_button('//li[text()="映射编辑"]')
        sleep(1)
        imp.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        imp.click_impall_button("保存")
        message = imp.get_find_message()
        eles = imp.finds_elements(By.XPATH, f'//ul[@class="ivu-tree-children"]//span[@class="valueSpan" and text()="{kh}"]')
        assert message == "保存成功" and len(eles) == 1
        assert not imp.has_fail_message()

    @allure.story("点击执行方案没有报服务器端错误")
    # @pytest.mark.run(order=1)
    def test_imp_clickexecute(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//ul/li[text()="{name}"]'))).click()
        imp.click_button('//span[text()=" 执行方案"]')
        imp.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        eles = imp.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(eles) == 0
        assert not imp.has_fail_message()

    @allure.story("编辑方案成功，取消勾选客户，勾选工序成功。右键映射点击确定不报错，点击方案不报错")
    # @pytest.mark.run(order=1)
    def test_imp_update(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        dir_ = 'Process'
        name = "1导入设置方案"
        kh = "客户"
        gx = "工序"
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//ul/li[text()="{name}"]'))).click()
        imp.click_button('//ul[@class="ivu-tree-children"]//span[text()="导入"]')
        imp.click_impall_button("编辑")
        sleep(1)
        imp.click_button(f'//ul[@class="ivu-tree-children"]//span[text()="{kh}"]/ancestor::ul[1]//label/span')
        imp.click_button(f'//ul[@class="ivu-tree-children"]//span[text()="{gx}"]/ancestor::ul[1]//label/span')
        ele = imp.get_find_element_xpath(f'//ul[@class="ivu-tree-children"]//span[text()="{gx}"]')
        ActionChains(driver).context_click(ele).perform()
        imp.click_button('//li[text()="映射编辑"]')
        imp.click_button('//button[span[text()="浏览文件"]]')

        # 清理 .crdownload 文件，避免上传未完成的文件
        current_dir = os.path.dirname(__file__)
        download_path = os.path.join(current_dir, "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)
        # 1. 准备上传文件路径
        upload_file = os.path.join(download_path, f"{dir_}.xls")
        assert os.path.isfile(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        imp.get_find_element_xpath('(//input[@type="file"])[3]')
        pyautogui.write(upload_file)
        sleep(3)
        pyautogui.press('enter')
        sleep(1)
        pyautogui.press('enter')
        sleep(1)
        imp.click_button('//div[text()=" 字段映射 "]')
        imp.wait_for_el_loading_mask()
        num = len(imp.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr'))
        for i in range(1, num + 1):
            imp.click_button(
                f'(//table[@class="vxe-table--body"])[1]//tr[{i}]/td[3]')
            sleep(0.5)
            imp.click_button(
                f'(//div[@class="vxe-select-option--wrapper"])[{i}]/div[{i}]')
            sleep(1)

        imp.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        imp.click_impall_button("保存")
        message = imp.get_find_message()
        imp.click_button('//span[text()=" 执行方案"]')
        imp.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        imp.get_find_message()
        imp.wait_for_el_loading_mask()
        eles1 = imp.finds_elements(By.XPATH,
                                   f'//ul[@class="ivu-tree-children"]//span[@class="valueSpan" and text()="{kh}"]')
        eles2 = imp.finds_elements(By.XPATH,
                                   f'//ul[@class="ivu-tree-children"]//span[@class="valueSpan" and text()="{gx}"]')
        eles = imp.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(eles) == 0
        assert message == "保存成功" and len(eles1) == 0 and len(eles2) == 1
        assert not imp.has_fail_message()

    @allure.story("点击复制方案，不输入数据，不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_copy1(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        add = AddsPages(driver)
        name = "1导入设置方案"
        copyname = '1同步导入1'
        imp.copy_()
        sleep(1)
        list_ = ['//div[label[text()="源方案"]]//div[@class="ivu-select-selection"]', '//div[label[text()="目的方案"]]//input[@type="text"]']
        box_color = add.get_border_color(list_)
        assert all(color == "rgb(237, 64, 20)" for color in box_color), f"预期{box_color}"
        assert not imp.has_fail_message()

    @allure.story("点击复制方案，只输入源方案，不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_copy2(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        add = AddsPages(driver)
        name = "1导入设置方案"
        copyname = '1同步导入1'
        imp.copy_(name=name)
        sleep(1)
        list_ = ['//div[label[text()="目的方案"]]//input[@type="text"]']
        box_color = add.get_border_color(list_)
        assert all(color == "rgb(237, 64, 20)" for color in box_color), f"预期{box_color}"
        assert not imp.has_fail_message()

    @allure.story("点击复制方案，只输入目的方案，不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_copy3(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        add = AddsPages(driver)
        name = "1导入设置方案"
        copyname = '1同步导入1'
        imp.copy_(copy_name=copyname)
        sleep(1)
        list_ = ['//div[label[text()="源方案"]]//div[@class="ivu-select-selection"]']
        box_color = add.get_border_color(list_)
        assert all(color == "rgb(237, 64, 20)" for color in box_color), f"预期{box_color}"
        assert not imp.has_fail_message()

    @allure.story("输入重复名称，不允许保存")
    # @pytest.mark.run(order=1)
    def test_imp_copy4(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        imp.copy_(name=name, copy_name=name)
        message = imp.get_error_message()
        assert message == '名称不能重复'
        assert not imp.has_fail_message()

    @allure.story("复制名称成功")
    # @pytest.mark.run(order=1)
    def test_imp_copy5(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        name = "1导入设置方案"
        copyname = '1同步导入1'
        imp.copy_(name=name, copy_name=copyname)
        message = imp.get_find_message()
        imp.copy_(name=name, copy_name='1同步导入2')
        message = imp.get_find_message()
        imp.copy_(name=name, copy_name='1同步导入3')
        message = imp.get_find_message()
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        ele = imp.finds_elements(By.XPATH, f'//ul/li[text()="{copyname}"]')
        assert message == '复制成功' and len(ele) == 2
        assert not imp.has_fail_message()

    @allure.story("删除方案成功")
    # @pytest.mark.run(order=1)
    def test_imp_del(self, login_to_imp):
        driver = login_to_imp  # WebDriver 实例
        imp = ImpPage(driver)  # 用 driver 初始化 ImpPage
        import_name = [
            "1导入设置方案",
            "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111",
        ]
        imp.del_all(import_name)
        imp.click_button(
            '//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
        ele1 = imp.finds_elements(By.XPATH, f'//ul/li[text()="{import_name[0]}"]')
        ele2 = imp.finds_elements(By.XPATH, f'//ul/li[text()="{import_name[1]}"]')
        assert len(ele1) == 0 and len(ele2) == 0
        assert not imp.has_fail_message()

