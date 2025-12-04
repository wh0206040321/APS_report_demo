import logging
import random
from datetime import date
from time import sleep
from datetime import datetime

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.systemPage.affairs_page import AffairsPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_affairs():
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
        page.click_button('(//span[text()="事务管理"])[1]')  # 点击事务管理
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("事务管理页用例")
@pytest.mark.run(order=202)
class TestAffairsPage:

    @allure.story("事务模版-新增模版失败，不输入事务名称，事务类型，配置参数不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(button=True)
        list_input = [
            '//div[label[text()="事务名称"]]//input',
            '//div[label[text()="事务类型"]]//input',
            '//div[label[text()="配置参数"]]//input',
        ]
        sleep(1)
        color_value = affairs.get_border_color(list_input)
        div_xpath_list = [item.replace("//input", '//div[@class="el-form-item__error"]') for item in list_input]
        value = affairs.batch_acquisition_text(div_xpath_list)
        assert all(color == "rgb(245, 108, 108)" for color in color_value)
        assert value == ['请输入事务名称', '请选择事务类型', '请输入配置参数']
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版失败，输入事务名称，不输入事务类型，配置参数不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(name="name", button=True)
        list_input = [
            '//div[label[text()="事务类型"]]//input',
            '//div[label[text()="配置参数"]]//input',
        ]
        sleep(1)
        color_value = affairs.get_border_color(list_input)
        div_xpath_list = [item.replace("//input", '//div[@class="el-form-item__error"]') for item in list_input]
        value = affairs.batch_acquisition_text(div_xpath_list)
        assert all(color == "rgb(245, 108, 108)" for color in color_value)
        assert value == ['请选择事务类型', '请输入配置参数']
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版失败，不输入事务名称，输入事务类型，配置参数不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(type="服务", button=False)
        affairs.click_button('//div[text()=" 自定义 "]')
        affairs.enter_texts('//div[p[text()="自定义服务:"]]//input', "https://")
        affairs.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        list_input = [
            '//div[label[text()="事务名称"]]//input',
        ]
        sleep(1)
        color_value = affairs.get_border_color(list_input)
        div_xpath_list = [item.replace("//input", '//div[@class="el-form-item__error"]') for item in list_input]
        value = affairs.batch_acquisition_text(div_xpath_list)
        assert all(color == "rgb(245, 108, 108)" for color in color_value)
        assert value == ['请输入事务名称']
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版失败，事务类型不填写点击确定,不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(name="测试事务模版1", type="服务", button=False)
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        mes = affairs.get_error_message()
        assert mes == "请把信息填写完整"
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为服务，填写计划计算成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版1"
        type = "服务"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[text()=" 计划计算 "]')
        affairs.click_button('//input[@placeholder="请选择计划单元"]')
        affairs.click_button('//li[text()="金属（演示）" and @class="ivu-select-item"]')
        sleep(1)
        affairs.click_button('//input[@placeholder="请选择计划方案"]')
        affairs.click_button('//li[text()="均衡排产" and @class="ivu-select-item"]')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为服务，填写物控计算成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版2"
        type = "服务"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[text()=" 物控计算 "]')
        affairs.click_button('//input[@placeholder="请选择计划单元"]')
        affairs.click_button('//li[text()="金属（演示）" and @class="ivu-select-item"]')
        sleep(1)
        affairs.click_button('//input[@placeholder="选择物控方案"]')
        affairs.click_button('//div[p[text()="物控方案名称:"]]//ul[@class="ivu-select-dropdown-list"]/li[1]')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版失败，事务类型为服务，填写自定义失败- 自定义值需以http或https开头")
    # @pytest.mark.run(order=1)
    def test_affairs_template_customizefail1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版2"
        type = "服务"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[text()=" 自定义 "]')
        affairs.enter_texts('//div[p[text()="自定义服务:"]]//input', "htt1")
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        mes = affairs.get_error_message()
        assert mes == '自定义值需以http或https开头'
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为服务，填写自定义成功- 自定义值以http开头")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版3"
        type = "服务"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[text()=" 自定义 "]')
        affairs.enter_texts('//div[p[text()="自定义服务:"]]//input', "http12ssc")
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.enter_texts('//div[label[text()="事务描述"]]//input', "自定义事务描述")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为服务，填写自定义成功- 自定义值以https开头")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版4"
        type = "服务"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[text()=" 自定义 "]')
        affairs.enter_texts('//div[p[text()="自定义服务:"]]//input', "https")
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.enter_texts('//div[label[text()="事务描述"]]//input', "自定义事务描述")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为存储过程不填写点击确定,不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(type="存储过程", button=False)
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        mes = affairs.get_error_message()
        assert mes == "请把信息填写完整"
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为存储过程输入名称不输入值,不允许提交")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addfail6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_add_affairs(type="存储过程", button=False)
        affairs.click_button('//div[p[text()="存储过程列表:"]]//i')
        affairs.click_button('//li[text()="APS_MP_Holiday"]')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        mes = affairs.get_error_message()
        assert mes == "请把信息填写完整"
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为存储过程，添加成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版5"
        type = "存储过程"
        affairs.click_add_affairs(name=name, type=type, button=False)
        affairs.click_button('//div[p[text()="存储过程列表:"]]//i')
        affairs.click_button('//li[text()="APS_MP_Holiday"]')
        num = len(driver.find_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr'))
        for i in range(1, 1+num):
            affairs.enter_texts(f'//table[@class="vxe-table--body"]//tr[{i}]/td[3]//input', "1")
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-新增模版成功，事务类型为接口，添加成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addsuccess6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        adds = AddsPages(driver)
        name = "测试事务模版6"
        type = "接口"
        affairs.click_add_affairs(name=name, type=type, button=False)
        select_list = [
            {"select": '(//div[@class="flex-1"])[2]//input', "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
            {"select": '(//div[@class="flex-1"])[3]//input', "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
        ]
        adds.batch_modify_select_input(select_list)
        affairs.click_button('(//table[@class="vxe-table--body"])[2]//tr[1]//span')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-添加模版数据重复")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addrepeat1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        adds = AddsPages(driver)
        name = "测试事务模版6"
        affairs.click_add_affairs(name=name, type="接口", button=False)
        select_list = [
            {"select": '(//div[@class="flex-1"])[2]//input',
             "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
            {"select": '(//div[@class="flex-1"])[3]//input',
             "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
        ]
        adds.batch_modify_select_input(select_list)
        affairs.click_button('(//table[@class="vxe-table--body"])[2]//tr[1]//span')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        mes = affairs.get_error_message()
        assert mes == "事务已存在"
        assert not affairs.has_fail_message()

    @allure.story("事务模版-添加全部成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addall(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        adds = AddsPages(driver)

        name = "添加全部模版成功"
        type = "接口"
        xpth_list = [
            '//div[label[text()="事务名称"]]//input',
            '//div[label[text()="事务类型"]]//input',
            '//div[label[text()="事务描述"]]//input',
            '//div[label[text()="配置参数"]]//input',
            '//div[label[text()="推送参数设置"]]//input',
        ]
        affairs.click_add_affairs(name=name, type=type, button=False)
        select_list = [
            {"select": '(//div[@class="flex-1"])[2]//input',
             "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
            {"select": '(//div[@class="flex-1"])[3]//input',
             "value": '(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]'},
        ]
        adds.batch_modify_select_input(select_list)

        affairs.click_button('(//table[@class="vxe-table--body"])[2]//tr[1]//span')
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        affairs.enter_texts('//div[label[text()="事务描述"]]//input', name)
        swich = affairs.get_find_element_xpath('//div[label[text()="推送"]]/div/div/span').get_attribute("class")
        sleep(1)
        if "ivu-switch-checked" not in swich:
            affairs.click_button('//div[label[text()="推送"]]/div/div/span')

        checked = affairs.get_find_element_xpath('//label[span[text()="站内"]]/span[1]').get_attribute("class")
        if checked == 'el-checkbox__input':
            affairs.click_button('//label[span[text()="站内"]]/span[1]')

        affairs.click_button('//div[label[text()="推送参数设置"]]//i[@class="ivu-icon ivu-icon-md-albums paramIcon"]')
        affairs.click_button('//div[text()=" 用户 "]')
        affairs.click_button('//div[span[text()="用户:"]]//i')
        affairs.click_button('(//ul[@class="el-scrollbar__view el-select-dropdown__list"])[last()]/li[1]')
        affairs.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]//span[text()="确定"]')
        sleep(1)
        before_list = affairs.batch_acquisition_input(xpth_list)
        before_swich = affairs.get_find_element_xpath('//div[label[text()="推送"]]/div/div/span').get_attribute("class")
        before_checked = affairs.get_find_element_xpath('//label[span[text()="站内"]]/span[1]').get_attribute("class")
        affairs.click_confirm_button()
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        affairs.right_refresh()
        element = affairs.get_find_element_xpath(f'//div[@class="template-card__title"]/div[text()="{name}"]/ancestor::div[3]/div[3]/div')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        affairs.hover(name=name, edi="编辑")
        after_list = affairs.batch_acquisition_input(xpth_list)
        after_swich = affairs.get_find_element_xpath('//div[label[text()="推送"]]/div/div/span').get_attribute(
            "class")
        after_checked = affairs.get_find_element_xpath('//label[span[text()="站内"]]/span[1]').get_attribute("class")
        assert len(ele) == 1 and value == type
        assert before_list == after_list and all(before_list)
        assert before_swich == after_swich
        assert before_checked == after_checked
        assert not affairs.has_fail_message()

    @allure.story("事务模版-查询事务名称成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_selectname(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "添加全部模版成功"
        eles = driver.find_elements(By.XPATH, '//div[@class="template-card__title"]/div')
        count = 0
        for ele in eles:
            if ele.text == name:
                count += 1
        affairs.input_text(name)
        sleep(3)
        elements = affairs.finds_elements(By.XPATH, '//div[@class="template-card__title"]/div')
        assert count == len(elements)
        assert not affairs.has_fail_message()

    @allure.story("事务模版-查询事务描述成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_selectdesc(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "自定义事务描述"
        eles = driver.find_elements(By.XPATH, '//div[@class="template-card__desc"]/div')
        count = 0
        for ele in eles:
            if name in ele.text:
                count += 1
        affairs.input_text(name)
        sleep(3)
        elements = affairs.finds_elements(By.XPATH, '//div[@class="template-card__desc"]/div')
        assert count == len(elements)
        assert not affairs.has_fail_message()

    @allure.story("事务模版-修改事务名称重复")
    # @pytest.mark.run(order=1)
    def test_affairs_template_updatnamerepe(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版6"
        affairs.hover(name=name, edi="编辑")
        affairs.get_find_element_xpath('//div[label[text()="事务名称"]]//input').clear()
        affairs.enter_texts('//div[label[text()="事务名称"]]//input', "测试事务模版5")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        mes = affairs.get_error_message()
        assert mes == "事务已存在"
        assert not affairs.has_fail_message()

    @allure.story("事务模版-修改事务名称成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_updatname(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        before_name = "测试事务模版6"
        after_name = "测试事务模版7"
        affairs.hover(name=before_name, edi="编辑")
        affairs.get_find_element_xpath('//div[label[text()="事务名称"]]//input').clear()
        affairs.enter_texts('//div[label[text()="事务名称"]]//input', after_name)
        type = affairs.get_find_element_xpath('//div[label[text()="事务类型"]]//input').get_attribute("value")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = affairs.get_find_message()
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{after_name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert message == "编辑成功！"
        assert len(ele) == 1 and value == type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-切换事务类型，修改配置参数成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_updattypesuccess(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版7"
        type = "存储过程"
        affairs.hover(name=name, edi="编辑")
        affairs.click_button('//div[label[text()="事务类型"]]//input')
        affairs.click_button(f'//span[text()="{type}"]')
        affairs.click_button('//div[@class="el-message-box__btns"]//span[contains(text(),"确定")]')
        sleep(1)
        affairs.click_button('//div[label[text()="配置参数"]]//i[@class="ivu-icon ivu-icon-md-albums paramIcon"]')
        affairs.click_button('//div[p[text()="存储过程列表:"]]//i')
        affairs.click_button('//li[text()="APS_MP_Holiday"]')
        num = len(driver.find_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr'))
        for i in range(1, 1 + num):
            affairs.enter_texts(f'//table[@class="vxe-table--body"]//tr[{i}]/td[3]//input', "1")
        affairs.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(3)
        type_ = affairs.get_find_element_xpath('//div[label[text()="事务类型"]]//input').get_attribute("value")
        sleep(2)
        before_parameter = affairs.get_find_element_xpath('//div[label[text()="配置参数"]]//input').get_attribute("value")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        affairs.get_find_message()
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert len(ele) == 1 and value == type_ and 'APS_MP_Holiday' in before_parameter
        assert not affairs.has_fail_message()

    @allure.story("事务模版-切换事务类型，配置参数刷新")
    # @pytest.mark.run(order=1)
    def test_affairs_template_updattype(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版7"
        type = "接口"
        affairs.hover(name=name, edi="编辑")
        type1 = affairs.get_find_element_xpath('//div[label[text()="事务类型"]]//input').get_attribute("value")
        affairs.click_button('//div[label[text()="事务类型"]]//input')
        affairs.click_button(f'//span[text()="{type}"]')
        affairs.click_button('//div[@class="el-message-box__btns"]//span[contains(text(),"取消")]')
        sleep(2)
        type2 = affairs.get_find_element_xpath('//div[label[text()="事务类型"]]//input').get_attribute("value")
        affairs.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        affairs.get_find_message()
        ele = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name}"]')
        value = ele[0].find_element(By.XPATH, './ancestor::div[3]/div[3]/div').text
        assert type1 == type2 ==value and value != type
        assert not affairs.has_fail_message()

    @allure.story("事务模版-循环删除模版成功")
    # @pytest.mark.run(order=1)
    def test_affairs_template_delsuccess(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试事务模版"
        affairs.del_cycle(name=name, edi="删除")
        eles = affairs.finds_elements(By.XPATH, f'//div[@class="template-card__title"]/div[contains(text(),"{name}")]')
        assert len(eles) == 0
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程什么都不填点击保存，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process()
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 3 and list_ == ['请填写名称', '请填写分类', '请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程只填写名称，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1")
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 2 and list_ == ['请填写分类', '请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程填写名称和分类，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务")
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为一次，不填写执行时间，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="一次")
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写执行时间']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，不填写间隔执行，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="每天")
        container = affairs.get_find_element_xpath(
            f'//div[@class="dis-flex"]/div[1]'
        )
        ActionChains(driver).move_to_element(container).perform()

        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//div[@class="dis-flex"]/div[1]/i[@class="el-input__icon el-range__close-icon el-icon-circle-close"]'
            ))
        )

        # 3️⃣ 再点击图标
        delete_icon.click()
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为周，不填写时间设置，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="周")
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写按周']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为月，不填写时间设置，不允许保存")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addfail7(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="月")
        affairs.click_save()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写按月']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为一次，填写时间设置，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addsuccess1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程1"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="一次", time="一次")
        affairs.click_save()
        message = affairs.get_find_message()
        ele = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        assert message == "新增成功！" and len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，执行顺序为每天执行一次，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addsuccess2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程2"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天", time="1")
        affairs.click_save()
        message = affairs.get_find_message()
        ele = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        assert message == "新增成功！" and len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，执行顺序为间隔执行，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addsuccess3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程3"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天", time="2")
        affairs.click_save()
        message = affairs.get_find_message()
        ele = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        assert message == "新增成功！" and len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为周，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addsuccess4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程4"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="周", time="周")
        affairs.click_save()
        message = affairs.get_find_message()
        ele = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        assert message == "新增成功！" and len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为月，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addsuccess5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程5"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="月", time="月")
        affairs.click_save()
        message = affairs.get_find_message()
        ele = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        assert message == "新增成功！" and len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-不填写数据点击下一步，不允许进入")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process()
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 3 and list_ == ['请填写名称', '请填写分类', '请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程只填写名称，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1")
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 2 and list_ == ['请填写分类', '请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程填写名称和分类，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务")
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为一次，不填写执行时间，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="一次")
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写执行时间']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，不填写间隔执行，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="每天")
        container = affairs.get_find_element_xpath(
            f'//div[@class="dis-flex"]/div[1]'
        )
        ActionChains(driver).move_to_element(container).perform()

        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//div[@class="dis-flex"]/div[1]/i[@class="el-input__icon el-range__close-icon el-icon-circle-close"]'
            ))
        )

        # 3️⃣ 再点击图标
        delete_icon.click()
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写间隔执行']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为周，不填写时间设置，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="周")
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写按周']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为月，不填写时间设置，不允许点击下一步")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextfail7(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process()
        affairs.add_process(name="测试流程1", type="服务", frequency="月")
        affairs.click_next()
        eles = affairs.finds_elements(By.XPATH, '//div[@class="el-form-item__error"]')
        list_ = [ele.text for ele in eles]
        assert len(list_) == 1 and list_ == ['请填写按月']
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，点击下一步，再返回上一步，数据没有清空")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextsuccess1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        xpth_list = [
            '//div[label[text()="名称"]]//input',
            '//div[label[text()="分类"]]//input',
            '//div[label[text()="频率"]]//input',
            '//div[label[text()="执行设置"]]//input',
            '//div[label[text()="间隔执行"]]//input',
        ]
        affairs.click_process()
        affairs.add_process(name="测试流程6", type="服务", frequency="每天")
        sleep(1)
        affairs.click_next()
        affairs.click_button('//button[span[text()="上一步"]]')
        list_ = affairs.batch_acquisition_input(xpth_list)
        assert all(list_)
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，下一步重新添加一个事务点击保存，保存成功,并且新添加的事务出现在事务模版中")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextsuccess2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程6"
        process_name = "添加事务模版1"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天")
        affairs.click_button('//div[label[text()="是否启用"]]/div/span')
        sleep(1)
        affairs.click_next()
        value = affairs.add_process_affairs(name=process_name, add=True)
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        ele1 = driver.find_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{process_name}"]')
        affairs.click_process()
        affairs.wait_for_el_loading_mask()
        ele2 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        ele3 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[1]//div[text()="{process_name}"]]')
        assert message == "新增成功！" and len(ele1) == 1 == len(ele2) == len(ele3) and value[1] == process_name
        assert not affairs.has_fail_message()

    @allure.story("我的流程-频率为每天，添加搜索事务,添加两个事务点击保存，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_nextsuccess3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程7"
        sel1 = "添加事务模版1"
        sel2 = "添加全部模版成功"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天")
        affairs.click_next()
        value1 = affairs.add_process_affairs(add=False, sel=sel1)
        value2 = affairs.add_process_affairs(add=False, sel=sel2)
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        affairs.wait_for_el_loading_mask()
        ele1 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        # 一次性获取所有匹配的元素
        elements = affairs.finds_elements(
            By.XPATH,
            f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]/td[1]//div[@class="flow-direction"]/div'
        )

        # 直接提取所有元素的文本到列表
        list_ = [element.text for element in elements]
        assert message == "新增成功！"
        assert len(ele1) == 1 and len(list_) == 2 and value1[1] == sel1 and value2[1] == sel2
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程名称点击保存提示重复")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addrepeats1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程1"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天")
        affairs.click_save()
        mes = affairs.get_error_message()
        assert mes == "流程名称不能重复"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加流程名称点击下一步提示重复")
    # @pytest.mark.run(order=1)
    def test_affairs_template_addrepeats2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程1"
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天")
        affairs.click_next()
        mes = affairs.get_error_message()
        assert mes == "流程名称不能重复"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-添加全部数据，保存成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_addall(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "添加全部成功"
        sel = "添加全部模版成功"
        xpth_list = [
            '//div[label[text()="名称"]]//input',
            '//div[label[text()="分类"]]//input',
            '//div[label[text()="频率"]]//input',
            '//div[label[text()="执行设置"]]//input',
            '//div[label[text()="间隔执行"]]//input',
            '//textarea[@prop="comments"]'
        ]
        affairs.click_process()
        affairs.add_process(name=name, type="服务", frequency="每天")
        affairs.enter_texts('//textarea[@prop="comments"]', name)
        affairs.click_next()
        value1 = affairs.add_process_affairs(add=False, sel=sel)
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        ele1 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]')
        affairs.click_process_update(name)
        sleep(1)
        list_ = affairs.batch_acquisition_input(xpth_list)
        assert message == "新增成功！"
        assert len(ele1) == 1 and all(list_) and value1[1] == sel
        assert not affairs.has_fail_message()

    @allure.story("我的流程-流程事务查询成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        template_name = "添加事务模版1"
        sleep(1)
        affairs.click_process()
        affairs.select_all(affairs=template_name)
        # 获取表格中所有行
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '(//table[@class="el-table__body"])[1]//tr')
            )
        )

        # 逐行检查（发现第一个失败立即终止）
        for index, row in enumerate(rows, start=1):
            div_text = row.find_element(
                By.XPATH,
                './td[1]//div[@class="flow-direction"]/div'
            ).text.strip()

            assert template_name == div_text, (
                f"验证失败！第 {index} 行不符合条件\n"
                f"期望值: '{template_name}'\n"
                f"实际值: '{div_text}'"
            )
        assert not affairs.has_fail_message()

    @allure.story("我的流程-是否启动查询为开启")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        enable = "开启"
        sleep(1)
        affairs.click_process()
        affairs.select_all(enable=enable)
        # 获取表格中所有行
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '(//table[@class="el-table__body"])[1]//tr')
            )
        )
        # 逐行检查（发现第一个失败立即终止）
        for index, row in enumerate(rows, start=1):
            div_class = row.find_element(
                By.XPATH,
                './td[6]/div/span'
            ).get_attribute("class")

            assert "ivu-switch-checked" in div_class, (
                f"验证失败！第 {index} 行不符合条件\n"
                f"期望值: '{enable}'\n"
                f"实际值: '{div_class}'"
            )
        assert not affairs.has_fail_message()

    @allure.story("我的流程-是否启动查询为关闭")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        enable = "关闭"
        sleep(1)
        affairs.click_process()
        affairs.select_all(enable=enable)
        # 获取表格中所有行
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '(//table[@class="el-table__body"])[1]//tr')
            )
        )
        # 逐行检查（发现第一个失败立即终止）
        for index, row in enumerate(rows, start=1):
            div_class = row.find_element(
                By.XPATH,
                './td[6]/div/span'
            ).get_attribute("class")

            assert "ivu-switch-checked" not in div_class, (
                f"验证失败！第 {index} 行不符合条件\n"
                f"期望值: '{enable}'\n"
                f"实际值: '{div_class}'"
            )
        assert not affairs.has_fail_message()

    @allure.story("我的流程-查询流程名称成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程7"
        sleep(1)
        affairs.click_process()
        affairs.select_all(process=name)
        # 获取表格中所有行
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '(//table[@class="el-table__body"])[1]//tr')
            )
        )

        # 逐行检查（发现第一个失败立即终止）
        for index, row in enumerate(rows, start=1):
            div_text = row.find_element(
                By.XPATH,
                './td[2]/div'
            ).text.strip()

            assert name == div_text, (
                f"验证失败！第 {index} 行不符合条件\n"
                f"期望值: '{name}'\n"
                f"实际值: '{div_text}'"
            )
        assert not affairs.has_fail_message()

    @allure.story("我的流程-查询事务流程，开关开启，流程名称成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        template_name = "添加全部模版成功"
        enable = "开启"
        name = "添加全部成功"
        sleep(1)
        affairs.click_process()
        affairs.select_all(template_name, enable, name)
        td1 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[1]//tr[1]/td[1]//div[@class="flow-direction"]/div').text
        td2 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[1]//tr[1]/td[2]/div').text
        td6 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[1]//tr[1]/td[6]/div/span').get_attribute("class")
        ele = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[1]//tr[2]')
        assert td1 == template_name and td2 == name and td6 == "ivu-switch ivu-switch-checked ivu-switch-default" and len(ele) == 0
        assert not affairs.has_fail_message()

    @allure.story("我的流程-查询事务流程，开关关闭，流程名称成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        template_name = "添加事务模版1"
        enable = "关闭"
        name = "测试流程6"
        sleep(1)
        affairs.click_process()
        affairs.select_all(template_name, enable, name)
        ele = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[1]//tr[1]')
        assert len(ele) == 1
        assert not affairs.has_fail_message()

    @allure.story("我的流程-点击重置按钮成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_select7(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        template_name = "添加全部模版成功"
        enable = "关闭"
        name = "添加全部成功"
        sleep(1)
        affairs.click_process()
        affairs.select_all(template_name, enable, name, button=False)
        ele1 = affairs.get_find_element_xpath('//div[label[text()="流程事务:"]]//input').get_attribute("value")
        ele2 = affairs.get_find_element_xpath('//div[label[text()="是否启用:"]]//input').get_attribute("value")
        ele3 = affairs.get_find_element_xpath('//div[label[text()="流程名称:"]]//input').get_attribute("value")
        assert ele1 == ele3 == "" and ele2 == "全部"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-修改名称分类成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程7"
        before_ = "测试流程8"
        affairs.click_process()
        affairs.click_process_update(name)
        affairs.enter_texts('//div[label[text()="名称"]]/div//input', before_)
        affairs.enter_texts('//div[label[text()="分类"]]/div//input', "修改分类")
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        affairs.click_process_update(before_)
        sleep(1)
        before_name = affairs.get_find_element_xpath('//div[label[text()="名称"]]/div//input').get_attribute("value")
        before_type = affairs.get_find_element_xpath('//div[label[text()="分类"]]/div//input').get_attribute("value")
        assert message == "编辑成功！"
        assert before_name == before_ and before_type == "修改分类"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-修改频率成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        affairs.click_process()
        affairs.click_process_update(name)
        affairs.click_button('//div[label[text()="频率"]]/div//i')
        affairs.click_button(f'//li[span[text()="一次"]]')
        affairs.click_button('//div[label[text()="执行时间"]]/div//input')
        affairs.click_button('//td[@class="available today"]//span')
        affairs.click_button('//div[@class="el-picker-panel__footer"]/button[2]')
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        affairs.click_process_update(name)
        sleep(1)
        before_ = affairs.get_find_element_xpath('//div[label[text()="频率"]]/div//input').get_attribute("value")
        assert before_ == "一次" and message == "编辑成功！"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-修改事务模版成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        aff = "添加事务模版"
        affairs.click_process()
        affairs.click_process_update(name)
        sleep(0.5)
        affairs.click_next()
        affairs.click_button('(//i[@class="el-icon-edit"])[1]')
        affairs.enter_texts('//div[label[text()="事务名称"]]//input', aff)
        affairs.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]/button[1]')
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        eles = affairs.finds_elements(By.XPATH, f'(//table[@class="el-table__body"])[1]//tr[td[2]/div[text()="{name}"]]//div[@class="flow-direction"]/div')
        list_ = [ele.text for ele in eles]
        assert message == '编辑成功！'
        assert aff in list_
        assert not affairs.has_fail_message()

    @allure.story("我的流程-修改事务模版重复")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        aff = "添加全部模版成功"
        affairs.click_process()
        affairs.click_process_update(name)
        sleep(0.5)
        affairs.click_next()
        affairs.click_button('(//i[@class="el-icon-edit"])[1]')
        affairs.enter_texts('//div[label[text()="事务名称"]]//input', aff)
        affairs.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]/button[1]')
        message = affairs.get_error_message()
        assert message == "事务已存在"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-删除流程中的事务成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        aff = "添加事务模版"
        affairs.click_process()
        affairs.click_process_update(name)
        sleep(0.5)
        affairs.click_next()
        affairs.click_button('(//i[@class="el-icon-delete"])[1]')
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        eles = affairs.finds_elements(By.XPATH,
                                      f'(//table[@class="el-table__body"])[1]//tr[td[2]/div[text()="{name}"]]//div[@class="flow-direction"]/div')
        list_ = [ele.text for ele in eles]
        assert message == '编辑成功！'
        assert aff not in list_
        assert not affairs.has_fail_message()

    @allure.story("我的流程-新增流程中一个事务成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        aff = "添加事务模版"
        affairs.click_process()
        affairs.click_process_update(name)
        sleep(0.5)
        affairs.click_next()
        affairs.add_process_affairs(add=False, sel=aff)
        affairs.click_save()
        message = affairs.get_find_message()
        affairs.right_refresh()
        affairs.click_process()
        eles = affairs.finds_elements(By.XPATH,
                                      f'(//table[@class="el-table__body"])[1]//tr[td[2]/div[text()="{name}"]]//div[@class="flow-direction"]/div')
        list_ = [ele.text for ele in eles]
        assert message == '编辑成功！'
        assert aff in list_
        assert not affairs.has_fail_message()

    @allure.story("我的流程-修改名称分类重复")
    # @pytest.mark.run(order=1)
    def test_affairs_process_update7(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "测试流程8"
        before_ = "测试流程6"
        affairs.click_process()
        affairs.click_process_update(name)
        affairs.enter_texts('//div[label[text()="名称"]]/div//input', before_)
        affairs.click_save()
        message = affairs.get_error_message()
        assert message == "流程名称不能重复"
        assert not affairs.has_fail_message()

    @allure.story("我的流程-复制流程成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_copy(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "添加全部成功"
        affairs.click_process()
        affairs.click_button(f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]/td[last()]//span[text()="复制"]')
        affairs.click_button('//div[@class="ivu-modal-confirm-footer"]/button[2]')
        sleep(1)
        ele = affairs.get_find_element_xpath('//table[@class="el-table__body"]//tr[1]/td[2]').text
        assert name + "_copy1" == ele
        assert not affairs.has_fail_message()

    @allure.story("我的流程-点击查看成功")
    # @pytest.mark.run(order=1)
    def test_affairs_process_view(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name = "添加全部成功"
        affairs.click_process()
        affairs.click_button(
            f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]/td[last()]//span[text()="查看"]')
        sleep(1)
        ele = affairs.get_find_element_xpath('//div[@class="log-info-title"]/div').text
        assert ele == name
        assert not affairs.has_fail_message()

    @allure.story("我的流程-删除流程数据")
    def test_affairs_process_delete(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name1 = "添加全部成功"
        name2 = "测试流程"
        affairs.click_process()
        affairs.del_process(name1)
        sleep(1)
        affairs.del_process(name2)
        ele1 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[contains(text(),"{name1}")]]]')
        ele2 = affairs.finds_elements(By.XPATH, f'//table[@class="el-table__body"]//tr[td[2][div[contains(text(),"{name2}")]]]')
        assert len(ele1) == len(ele2) == 0
        assert not affairs.has_fail_message()

    @allure.story("我的流程-删除测试事务模版数据")
    def test_affairs_process_deletett(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        name1 = "添加全部模版成功"
        name2 = "添加事务模版"
        affairs.hover(name1, "删除")
        affairs.click_button('//div[@class="el-message-box__btns"]/button[2]')
        affairs.get_find_message()
        affairs.hover(name2, "删除")
        affairs.click_button('//div[@class="el-message-box__btns"]/button[2]')
        ele1 = affairs.finds_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name1}"]')
        sleep(1)
        ele2 = affairs.finds_elements(By.XPATH, f'//div[@class="template-card__title"]/div[text()="{name2}"]')
        assert len(ele1) == 0 and len(ele2) == 0
        assert not affairs.has_fail_message()

    @allure.story("流程日志-执行时间搜索成功")
    def test_affairs_log_sel1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        affairs.click_process_log()
        num = 1000
        affairs.click_paging(num)
        sleep(1)
        time1, time2 = affairs.get_log_time()
        affairs.sel_log_all(time1=time1, time2=time2)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[5]')
        for cell in cells:
            list_.append(datetime.strptime(cell.text, "%Y/%m/%d %H:%M:%S"))

        time1_dt = datetime.strptime(time1, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        time2_dt = datetime.strptime(time2, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        assert all(time2_dt <= t <= time1_dt for t in list_), "存在不在范围内的时间"
        assert not affairs.has_fail_message()

    @allure.story("流程日志-执行执行状态执行成功搜索成功")
    def test_affairs_log_sel2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        ptype = "执行成功"
        num = 1000
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(ptype=ptype)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[1]')
        for cell in cells:
            list_.append(cell.text)
        assert all(ptype == t for t in list_)
        assert not affairs.has_fail_message()

    @allure.story("流程日志-执行执行状态执行成功搜索成功")
    def test_affairs_log_sel3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        ptype = "执行失败"
        num = 1000
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(ptype=ptype)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[1]')
        for cell in cells:
            list_.append(cell.text)
        assert all(ptype == t for t in list_)
        assert not affairs.has_fail_message()

    @allure.story("流程日志-流程ID搜索成功搜索成功")
    def test_affairs_log_sel4(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        num = 1000
        affairs.click_process_log()
        pid = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]//tr[2]/td[4]').text
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(pid=pid)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[4]')
        for cell in cells:
            list_.append(cell.text)
        assert all(pid == t for t in list_)
        assert not affairs.has_fail_message()

    @allure.story("流程日志-流程名称搜索成功")
    def test_affairs_log_sel5(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        num = 1000
        affairs.click_process_log()
        pname = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]//tr[2]/td[3]').text
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(pname=pname)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[3]')
        for cell in cells:
            list_.append(cell.text)
        assert all(pname == t for t in list_)
        assert not affairs.has_fail_message()

    @allure.story("流程日志-事务搜索成功")
    def test_affairs_log_sel6(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        sleep(1)
        num = 1000
        affairs.click_process_log()
        affairs_name = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]//tr[2]/td[2]').text
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(affairs_name=affairs_name)
        list_ = []
        cells = driver.find_elements(By.XPATH, '(//table[@class="el-table__body"])[2]//tr/td[2]')
        for cell in cells:
            list_.append(cell.text)
        assert list_ and all(t in affairs_name for t in list_)
        assert not affairs.has_fail_message()

    @allure.story("流程日志-全部条件搜索成功，关系为and")
    def test_affairs_log_sel7(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        sleep(1)
        num = 1000
        time1 = "2024-11-28 "
        time2 = "10:25:00"
        ptype = "执行失败"
        pid = "6009574425101246"
        pname = "21"
        affairs_name = "获取令牌"
        dt = datetime.strptime(time1.strip(), "%Y-%m-%d")
        time_slash = dt.strftime("%Y/%m/%d")
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(time1=time1, time2=time2, ptype=ptype, pid=pid, pname=pname, affairs_name=affairs_name)
        td1 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]/tbody/tr[1]/td[1]')
        td2 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]/tbody/tr[1]/td[2]')
        td3 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]/tbody/tr[1]/td[3]')
        td4 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]/tbody/tr[1]/td[4]')
        td5 = affairs.get_find_element_xpath('(//table[@class="el-table__body"])[2]/tbody/tr[1]/td[5]')
        tr2 = affairs.finds_elements(By.XPATH,'(//table[@class="el-table__body"])[2]/tbody/tr[2]')
        assert td1.text == ptype and td2.text == affairs_name and td3.text == pname and td4.text == pid and td5.text == time_slash+' '+time2
        assert len(tr2) == 0
        assert not affairs.has_fail_message()

    @allure.story("流程日志-全部条件搜索成功，没有数据的时候显示无数据")
    def test_affairs_log_sel8(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        sleep(1)
        num = 1000
        time1 = "2025-02-27 "
        time2 = "10:20:00"
        ptype = "执行失败"
        pid = "41183627842692411"
        pname = "每周"
        affairs_name = "获取令牌"
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(time1=time1, time2=time2, ptype=ptype, pid=pid, pname=pname, affairs_name=affairs_name)
        tr2 = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[2]/tbody/tr[1]')
        assert len(tr2) == 0
        assert not affairs.has_fail_message()

    @allure.story("流程日志-点击重置按钮成功")
    def test_affairs_log_sel9(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        sleep(1)
        num = 1000
        time1 = "2025-02-27 "
        time2 = "10:20:00"
        ptype = "执行失败"
        pid = "4118362784269241"
        pname = "每周"
        affairs_name = "获取令牌"
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(1)
        affairs.sel_log_all(time1=time1, time2=time2, ptype=ptype, pid=pid, pname=pname, affairs_name=affairs_name, button=False)
        input1 = affairs.get_find_element_xpath('(//input[@placeholder="开始日期"])[1]').get_attribute("value")
        input2 = affairs.get_find_element_xpath('//div[label[text()="执行状态:"]]//input').get_attribute("value")
        input3 = affairs.get_find_element_xpath('//input[@placeholder="请输入流程ID"]').get_attribute("value")
        input4 = affairs.get_find_element_xpath('//input[@placeholder="请输入流程名称"]').get_attribute("value")
        input5 = affairs.get_find_element_xpath('//div[label[text()="事务:"]]//input').get_attribute("value")
        assert input1 == input3 == input4 == input5 == "" and input2 == "全部"
        assert not affairs.has_fail_message()

    @allure.story("流程日志-设置分页为1000")
    def test_affairs_log_paging1(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        num = 1000
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(3)
        eles = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[2]/tbody/tr')
        assert 0 < len(eles) <= num
        assert not affairs.has_fail_message()

    @allure.story("流程日志-设置分页为10,点击最后一页有数据")
    def test_affairs_log_paging2(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        num = 10
        affairs.click_process_log()
        affairs.click_paging(num)
        sleep(3)
        affairs.click_button('//ul[@class="el-pager"]/li[last()]')
        sleep(1)
        eles = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[2]/tbody/tr')
        assert 0 < len(eles) <= num
        assert not affairs.has_fail_message()

    @allure.story("流程日志-前往第2页成功")
    def test_affairs_log_paging3(self, login_to_affairs):
        driver = login_to_affairs  # WebDriver 实例
        affairs = AffairsPage(driver)  # 用 driver 初始化 AffairsPage
        num = 2
        sleep(1)
        affairs.click_process_log()
        affairs.click_paging('10')
        affairs.wait_for_el_loading_mask()
        affairs.enter_texts('//span[@class="el-pagination__jump"]//input', num)
        affairs.click_button('//input[@placeholder="请输入流程名称"]')
        affairs.wait_for_el_loading_mask()
        eles = affairs.finds_elements(By.XPATH, '(//table[@class="el-table__body"])[2]/tbody/tr')
        class_ = affairs.get_find_element_xpath(f'//ul[@class="el-pager"]/li[text()="{num}"]').get_attribute("class")
        assert 0 < len(eles) and class_ == "number active"
        assert not affairs.has_fail_message()
