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
from Pages.systemPage.other_page import OtherPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_modeldesign():
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
        list_ = ["系统管理", "系统设置", "模型设计"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("模型设计页用例")
@pytest.mark.run(order=223)
class TestSModelDesignPage:

    @allure.story("新增模型不填写数据，不允许新增")
    # @pytest.mark.run(order=1)
    def test_modeldesign_add1(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        sleep(2)
        model.click_modeldesign_button("新增模型")
        model.click_confirm()
        message = model.get_error_message()
        assert message == "请填写名称"
        assert not model.has_fail_message()

    @allure.story("新增模型成功")
    # @pytest.mark.run(order=1)
    def test_modeldesign_add2(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = '1测试模型'
        sleep(2)
        model.click_modeldesign_button("新增模型")
        model.enter_texts('//div[label[text()="模型名称"]]//input', name)
        model.click_confirm()
        message = model.get_find_message()
        sy = model.get_find_element_xpath(f'(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]').get_attribute('class')
        if 'expanded' not in sy:
            model.click_button('(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]')
        sleep(1)
        ele = model.finds_elements(By.XPATH, f'//div[@class="content-siadeNav"]//div[@role="treeitem"]//span[text()=" {name} "]')
        assert message == "新增成功！"
        assert len(ele) == 1
        assert not model.has_fail_message()

    @allure.story("新增测试数据成功")
    # @pytest.mark.run(order=1)
    def test_modeldesign_add3(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = '2测试模型'
        sleep(2)
        model.click_modeldesign_button("新增模型")
        model.enter_texts('//div[label[text()="模型名称"]]//input', name)
        model.click_confirm()
        message = model.get_find_message()
        sy = model.get_find_element_xpath(
            f'(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]').get_attribute(
            'class')
        if 'expanded' not in sy:
            model.click_button(
                '(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]')
        sleep(1)
        ele = model.finds_elements(By.XPATH,
                                   f'//div[@class="content-siadeNav"]//div[@role="treeitem"]//span[text()=" {name} "]')
        assert message == "新增成功！"
        assert len(ele) == 1
        assert not model.has_fail_message()

    @allure.story("新增重复模型不允许添加")
    # @pytest.mark.run(order=1)
    def test_modeldesign_addrepeat(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = '1测试模型'
        sleep(2)
        model.click_modeldesign_button("新增模型")
        model.enter_texts('//div[label[text()="模型名称"]]//input', name)
        model.click_confirm()
        message = model.get_find_message()
        assert message == "重复命名"
        assert not model.has_fail_message()

    @allure.story("查询模型成功")
    # @pytest.mark.run(order=1)
    def test_modeldesign_select(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = '1测试模型'
        sleep(2)
        ele1 = model.finds_elements(By.XPATH, f'//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[2]/div')
        model.enter_texts('//div[@class="content-siadeNav"]//input[@placeholder="请输入"]', name)
        sleep(2)
        ele2 = model.finds_elements(By.XPATH, f'//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[2]/div')
        assert len(ele1) != len(ele2)
        assert len(ele2) == 1
        assert not model.has_fail_message()

    @allure.story("修改名称成功")
    # @pytest.mark.run(order=1)
    def test_modeldesign_update(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        before_name = '1测试模型'
        after_name = '3测试模型'
        sleep(2)
        model.click_button(f'//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[2]/div//span[text()=" {before_name} "]')
        model.click_modeldesign_button("模型重命名")
        model.enter_texts('//div[label[text()="模型名称"]]//input', after_name)
        model.click_confirm()
        message = model.get_find_message()
        sy = model.get_find_element_xpath(
            f'(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]').get_attribute(
            'class')
        if 'expanded' not in sy:
            model.click_button(
                '(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]')
        sleep(1)
        ele1 = model.finds_elements(By.XPATH,
                                   f'//div[@class="content-siadeNav"]//div[@role="treeitem"]//span[text()=" {after_name} "]')
        ele2 = model.finds_elements(By.XPATH,
                                    f'//div[@class="content-siadeNav"]//div[@role="treeitem"]//span[text()=" {before_name} "]')
        assert message == "编辑成功！"
        assert len(ele1) == 1 and len(ele2) == 0
        assert not model.has_fail_message()

    @allure.story("点击保存 不报错")
    # @pytest.mark.run(order=1)
    def test_modeldesign_save(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        name = '3测试模型'
        sleep(2)
        model.click_button(
            f'//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[2]/div//span[text()=" {name} "]')
        model.click_modeldesign_button("保存")
        model.click_del_confirm()
        message = model.get_find_message()
        ele = model.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert message == "保存成功！"
        assert len(ele) == 0
        assert not model.has_fail_message()

    @allure.story("删除模型成功")
    # @pytest.mark.run(order=1)
    def test_modeldesign_del(self, login_to_modeldesign):
        driver = login_to_modeldesign  # WebDriver 实例
        model = OtherPage(driver)  # 用 driver 初始化 OtherPage
        list_name = ['2测试模型', '3测试模型']
        sleep(2)
        for name in list_name:
            model.click_button(
                f'//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[2]/div//span[text()=" {name} "]')
            model.click_modeldesign_button("删除模型")
            model.click_del_confirm()
            message = model.get_find_message()
            sy = model.get_find_element_xpath(
                f'(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]').get_attribute(
                'class')
            if 'expanded' not in sy:
                model.click_button(
                    '(//div[@class="content-siadeNav"]//div[@role="treeitem"][1]/div[1]/span[contains(@class,"el-tree-node__expand-icon")])[1]')
            sleep(1)
            ele = model.finds_elements(By.XPATH,
                                        f'//div[@class="content-siadeNav"]//div[@role="treeitem"]//span[text()=" {name} "]')
            assert message == "删除成功！"
            assert len(ele) == 0
        assert not model.has_fail_message()
