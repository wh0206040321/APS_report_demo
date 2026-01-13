import logging
from datetime import datetime
from itertools import chain
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
from Pages.systemPage.psi_page import PsiPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_psi():
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
        page.click_button('(//span[text()="系统管理"])[1]')  # 点击系统管理
        page.click_button('(//span[text()="单元设置"])[1]')  # 点击单元设置
        page.click_button('(//span[text()="PSI设置"])[1]')  # 点击PSI设置
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("PSI设置用例")
@pytest.mark.run(order=203)
class TestPSIPage:

    @allure.story("不输入值，点击增加不允许添加")
    # @pytest.mark.run(order=1)
    def test_psi_addfail1(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        psi.click_button_psi("新增")
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "请填写完整的信息才能提交"
        assert not psi.has_fail_message()

    @allure.story("只输入名称，点击增加不允许添加")
    # @pytest.mark.run(order=1)
    def test_psi_addfail2(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.add_psi(name=name, condition=False,method=False)
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "请填写完整的信息才能提交"
        assert not psi.has_fail_message()

    @allure.story("只输入名称和收集条件，点击增加不允许添加")
    # @pytest.mark.run(order=1)
    def test_psi_addfail3(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.add_psi(name=name, method=False)
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "请填写完整的信息才能提交"
        assert not psi.has_fail_message()

    @allure.story("输入名称和筛选方法，点击增加不允许添加")
    # @pytest.mark.run(order=1)
    def test_psi_addfail4(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.add_psi(name=name, condition=False)
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "请填写完整的信息才能提交"
        assert not psi.has_fail_message()

    @allure.story("输入名称和收集条件和筛选方法，添加成功")
    # @pytest.mark.run(order=1)
    def test_psi_addsuccess(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.add_psi(name=name)
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        eles = psi.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.right_refresh()
        assert message == "保存成功" and len(eles) == 1
        assert not psi.has_fail_message()

    @allure.story("添加全部成功")
    # @pytest.mark.run(order=1)
    def test_psi_addall(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "添加全部"
        list_update = [
            '//div[label[text()="标签"]]//input',
            '//div[label[text()="显示内容"]]//input',
            '//div[label[text()="初始值"]]//input',
            '//div[label[text()="文字颜色表达式"]]//input',
            '//div[label[text()="背景颜色表达式"]]//input',
            '//div[label[text()="限制0的数值"]]//input',
        ]
        list_group = [
            '//div[p[text()=" 标签: "]]//input',
            '//div[p[text()=" 组化键: "]]//input',
            '//div[p[text()=" 显示空数据: "]]//input',
            '//div[@class="vxe-modal--box"]//table[@class="vxe-table--body"]//tr/td[2]//input',
        ]

        list_ = [
            '//div[p[text()="PSI名称: "]]//input',
            '//div[p[text()="最上位行收集条件: "]]//input',
            '//div[p[text()="筛选方法: "]]//input',
        ]
        psi.add_psi(name=name)
        psi.click_data(num=1, name="表行")
        psi.enter_group_setting(name)
        psi.enter_group_update(name)
        before_v1 = psi.batch_acquisition_input(list_update)
        psi.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        before_v2 = psi.batch_acquisition_input(list_group)
        psi.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
        before_v3 = psi.batch_acquisition_input(list_)
        before_input1 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]').get_attribute("value")

        psi.click_data(num=2, name="表列")
        psi.enter_group_setting(name)
        psi.enter_group_update(name)
        before_v21 = psi.batch_acquisition_input(list_update)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        before_v22 = psi.batch_acquisition_input(list_group)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
        before_input2 = psi.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]').get_attribute("value")

        psi.click_data(num=3, name="内容")
        psi.enter_group_update(name)
        before_v32 = psi.batch_acquisition_input(list_update)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]//span[text()="确定"]')
        before_input3 = psi.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]').get_attribute("value")

        before_list = list(chain(before_v1, before_v2, before_v3, before_v21, before_v22, before_v32, [before_input1], [before_input2], [before_input3]))
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        eles = psi.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')

        psi.right_refresh()
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")

        psi.click_button('(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]')
        psi.click_button('(//i[@class="ivu-icon ivu-icon-ios-build"])[1]')
        psi.click_button('//div[@class="vxe-modal--box"]//table[@class="vxe-table--body"]//tr/td[2]//input')
        psi.click_button('//div[@class="vxe-modal--box"]//i[@class="ivu-icon ivu-icon-ios-build"]')
        after_v1 = psi.batch_acquisition_input(list_update)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        after_v2 = psi.batch_acquisition_input(list_group)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')
        after_v3 = psi.batch_acquisition_input(list_)
        after_input1 = psi.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]').get_attribute("value")

        psi.click_button('//div[text()=" 透视数据表列 "]')
        psi.click_button('(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]')
        psi.click_button('(//i[@class="ivu-icon ivu-icon-ios-build"])[2]')
        psi.click_button('//div[@class="vxe-modal--box"]//table[@class="vxe-table--body"]//tr/td[2]//input')
        psi.click_button('//div[@class="vxe-modal--box"]//i[@class="ivu-icon ivu-icon-ios-build"]')
        after_v21 = psi.batch_acquisition_input(list_update)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        after_v22 = psi.batch_acquisition_input(list_group)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')
        after_input2 = psi.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]').get_attribute("value")

        psi.click_button('//div[text()=" 透视数据内容 "]')
        psi.click_button('(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]')
        psi.click_button('(//i[@class="ivu-icon ivu-icon-ios-build"])[3]')
        after_v32 = psi.batch_acquisition_input(list_update)
        psi.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
        after_input3 = psi.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]').get_attribute("value")

        after_list = list(chain(after_v1, after_v2, after_v3, after_v21, after_v22, after_v32, [after_input1], [after_input2], [after_input3]))
        psi.right_refresh()
        assert before_list == after_list and all(after_list)
        assert message == "保存成功" and len(eles) == 1
        assert not psi.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_psi_addsuccess1(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi3"
        psi.add_psi(name=name)
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        eles = psi.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.right_refresh()
        assert message == "保存成功" and len(eles) == 1
        assert not psi.has_fail_message()

    @allure.story("添加名称重复")
    # @pytest.mark.run(order=1)
    def test_psi_addrepeat(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.add_psi(name=name)
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "名称不能重复"
        assert not psi.has_fail_message()

    @allure.story("修改表行，表列，数据内容名称成功")
    # @pytest.mark.run(order=1)
    def test_psi_update1(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "添加全部"
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        psi.enter_texts('(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]', "1")
        before_v1 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]').get_attribute("value")
        psi.click_button('//div[text()=" 透视数据表列 "]')
        psi.enter_texts('(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]', "2")
        before_v2 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]').get_attribute("value")
        psi.click_button('//div[text()=" 透视数据内容 "]')
        psi.enter_texts('(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]', "3")
        before_v3 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]').get_attribute("value")
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        psi.right_refresh()
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        after_v1 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]').get_attribute("value")
        psi.click_button('//div[text()=" 透视数据表列 "]')
        after_v2 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[2]').get_attribute("value")
        psi.click_button('//div[text()=" 透视数据内容 "]')
        after_v3 = psi.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr/td[2]//input)[3]').get_attribute("value")
        psi.right_refresh()
        assert message == "保存成功"
        assert before_v1 == after_v1 and before_v2 == after_v2 and before_v3 == after_v3
        assert not psi.has_fail_message()

    @allure.story("修改psi名称重复")
    # @pytest.mark.run(order=1)
    def test_psi_updaterepeat(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "添加全部"
        name1 = "1测试psi1"
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        psi.enter_text(By.XPATH, '//div[p[text()="PSI名称: "]]//input', name1)
        psi.click_button_psi("保存")
        message = psi.get_error_message()
        psi.right_refresh()
        assert message == "名称不能重复"
        assert not psi.has_fail_message()

    @allure.story("修改psi名称,最上位行收集条件,筛选方法成功")
    # @pytest.mark.run(order=1)
    def test_psi_update2(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "添加全部"
        name1 = "1测试psi2"
        list_ = [
            '//div[p[text()="PSI名称: "]]//input',
            '//div[p[text()="最上位行收集条件: "]]//input',
            '//div[p[text()="筛选方法: "]]//input',
        ]
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        psi.batch_modify_input(list_, name1)
        before_list = psi.batch_acquisition_input(list_)
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        psi.right_refresh()
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name1}"]')
        psi.click_button_psi("编辑")
        after_list = psi.batch_acquisition_input(list_)
        psi.right_refresh()
        assert message == "保存成功"
        assert before_list == after_list and all(after_list)
        assert not psi.has_fail_message()

    @allure.story("查询1测试psi1成功")
    # @pytest.mark.run(order=1)
    def test_psi_select1(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        psi.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', name)
        sleep(1)
        eles = psi.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        psi.right_refresh()
        assert all(text == name for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not psi.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_psi_select2(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        # psi.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label[contains(text(),"全选")]//input')
        sleep(1)
        eles = psi.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute("class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            psi.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            psi.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//input')
        eles = psi.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        psi.right_refresh()
        assert len(eles) == 0
        assert not psi.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_psi_select3(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试"
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        psi.hover("包含")
        sleep(1)
        psi.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', name)
        sleep(1)
        eles = psi.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        psi.right_refresh()
        assert all(name in text for text in list_)
        assert not psi.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_psi_select4(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试"
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        psi.hover("符合开头")
        sleep(1)
        psi.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', name)
        sleep(1)
        eles = psi.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        psi.right_refresh()
        assert all(str(item).startswith(name) for item in list_)
        assert not psi.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_psi_select5(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "2"
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        psi.hover("符合结尾")
        sleep(1)
        psi.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', name)
        sleep(1)
        eles = psi.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[1]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        psi.right_refresh()
        assert all(str(item).endswith(name) for item in list_)
        assert not psi.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_psi_clear(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        psi.wait_for_loading_to_disappear()
        name = "3"
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        psi.hover("包含")
        sleep(1)
        psi.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', name)
        sleep(1)
        psi.click_button('//div[p[text()="PSI名称"]]/following-sibling::div//i')
        psi.hover("清除所有筛选条件")
        sleep(1)
        ele = psi.get_find_element_xpath('//div[p[text()="PSI名称"]]/following-sibling::div//i').get_attribute(
            "class")
        psi.right_refresh()
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not psi.has_fail_message()

    @allure.story("点击取消不会修改数据")
    # @pytest.mark.run(order=1)
    def test_psi_cancel(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi1"
        name1 = "11"
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        sleep(1)
        psi.enter_text(By.XPATH, '//div[p[text()="PSI名称: "]]//input', name1)
        psi.click_button_psi("取消")
        psi.right_refresh()
        eles = psi.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.right_refresh()
        assert len(eles) == 1
        assert not psi.has_fail_message()

    @allure.story("删除透视数据，表行，表列，数据内容成功")
    # @pytest.mark.run(order=1)
    def test_psi_deldata(self, login_to_psi):
        driver = login_to_psi  # WebDriver 实例
        psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
        name = "1测试psi2"
        list_ = [
            '//div[text()=" 透视数据表行 "]',
            '//div[text()=" 透视数据表列 "]',
            '//div[text()=" 透视数据内容 "]',
        ]
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        psi.del_data(list_)
        psi.click_button_psi("保存")
        message = psi.get_find_message()
        psi.right_refresh()
        psi.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        psi.click_button_psi("编辑")
        ele = psi.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[2]//input')
        psi.right_refresh()
        assert len(ele) == 0
        assert message == "保存成功"
        assert not psi.has_fail_message()

    # @allure.story("删除数据成功")
    # # @pytest.mark.run(order=1)
    # def test_psi_del(self, login_to_psi):
    #     driver = login_to_psi  # WebDriver 实例
    #     psi = PsiPage(driver)  # 用 driver 初始化 PsiPage
    #     list_ = ["1测试psi1", "1测试psi2", "1测试psi3"]
    #     psi.del_all(list_)
    #     message = psi.get_find_message()
    #     psi.right_refresh()
    #     eles2 = psi.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr/td[2]//span[text()="1测试psi2"]')
    #     assert not eles2
    #     assert message == "删除成功！"
    #     assert not psi.has_fail_message()