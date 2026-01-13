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
from Pages.itemsPage.personal_page import PersonalPage
from Pages.systemPage.environment_page import EnvironmentPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")   # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_environment():
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
        page.click_button('(//span[text()="环境设置"])[1]')  # 点击环境设置
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("环境设置页用例")
@pytest.mark.run(order=201)
class TestEnvironmentPage:

    @allure.story("全体页面-所有复选框都点击取消勾选，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_all_checkbox1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        xpth_list = [
            '//div[label[text()="品目资源时序:"]]/div//input',
            '//div[label[text()="物料同步检查:"]]/div//input',
            '//div[label[text()="资源同步检查:"]]/div//input',
            '//div[label[text()="订单同步检查:"]]/div//input',
            '//div[label[text()="变更使用时间:"]]/div//input',
            '//div[label[text()="内部函数基于日期和日境界时刻进行计算:"]]/div//input',
            '//div[label[text()="工作表移动后全固定:"]]/div//input',
        ]
        environment.update_checkbox(xpth_list, new_value=False)
        before_value = environment.get_checkbox_value(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        after_value = environment.get_checkbox_value(xpth_list)
        assert before_value == after_value and message == "保存成功"
        assert not all(after_value)
        assert not environment.has_fail_message()

    @allure.story("全体页面-所有复选框都勾选，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_all_checkbox2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        xpth_list = [
            '//div[label[text()="品目资源时序:"]]/div//input',
            '//div[label[text()="物料同步检查:"]]/div//input',
            '//div[label[text()="资源同步检查:"]]/div//input',
            '//div[label[text()="订单同步检查:"]]/div//input',
            '//div[label[text()="变更使用时间:"]]/div//input',
            '//div[label[text()="内部函数基于日期和日境界时刻进行计算:"]]/div//input',
            '//div[label[text()="工作表移动后全固定:"]]/div//input',
        ]
        environment.update_checkbox(xpth_list, new_value=True)
        before_value = environment.get_checkbox_value(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        after_value = environment.get_checkbox_value(xpth_list)
        assert before_value == after_value and message == "保存成功"
        assert all(after_value)
        assert not environment.has_fail_message()

    @allure.story("全体页面-修改全部下拉框，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_all_select1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        select_list = [
            {"select": '//div[label[text()="用鼠标移动工作方法:"]]/div//i', "value": '//li[text()="无限能力"]'},
            {"select": '//div[label[text()="制造时间计算:"]]/div//i', "value": '//li[text()="最长时间的资源"]'},
        ]
        environment.batch_modify_select_input(select_list)
        select_input_list = [item["select"].replace("//i", "//span") for item in select_list]
        before_value = environment.batch_acquisition_text(select_input_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        after_value = environment.batch_acquisition_text(select_input_list)
        assert before_value == after_value and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("全体页面-修改全部下拉框，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_all_select2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        select_list = [
            {"select": '//div[label[text()="用鼠标移动工作方法:"]]/div//i', "value": '//li[text()="插入(右推)"]'},
            {"select": '//div[label[text()="制造时间计算:"]]/div//i', "value": '//li[text()="基于主资源"]'},
        ]
        environment.batch_modify_select_input(select_list)
        select_input_list = [item["select"].replace("//i", "//span") for item in select_list]
        before_value = environment.batch_acquisition_text(select_input_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        after_value = environment.batch_acquisition_text(select_input_list)
        assert before_value == after_value and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("周期页面-校验所有数字输入框-不输入不允许保存，输入框颜色改变")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_numinput1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        value = " "
        xpth_list = [
            '//div[label[text()="分派开始时间:"]]//input',
            '//div[label[text()="分派结束时间:"]]//input',
            '//div[label[text()="生产指令结束时间:"]]//input',
            '//div[label[text()="显示开始时间:"]]//input',
            '//div[label[text()="显示结束时间:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        div_xpth_list = [item.replace("//input", "//input/ancestor::div[2]") for item in xpth_list]
        environment.click_save_button()
        message = environment.get_error_message()
        before_value = environment.get_border_color(div_xpth_list)
        assert all(color == "rgb(237, 64, 20)" for color in before_value) and message == "请填写信息"
        assert not environment.has_fail_message()

    @allure.story("周期页面-校验所有数字输入框-超过最大值为9999999999")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_numinput2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        value = "11111111111111111111111111"
        xpth_list = [
            '//div[label[text()="分派开始时间:"]]//input',
            '//div[label[text()="分派结束时间:"]]//input',
            '//div[label[text()="生产指令结束时间:"]]//input',
            '//div[label[text()="显示开始时间:"]]//input',
            '//div[label[text()="显示结束时间:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        before_value = environment.batch_acquisition_input(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_cycle()
        after_value = environment.batch_acquisition_input(xpth_list)
        num_ = "999999999999999"
        assert all(num_ == v for v in after_value) and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("周期页面-校验所有数字输入框-只允许输入数字")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_numinput3(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        value = "QAseE1@!><?+_+=-33."
        xpth_list = [
            '//div[label[text()="分派开始时间:"]]//input',
            '//div[label[text()="分派结束时间:"]]//input',
            '//div[label[text()="生产指令结束时间:"]]//input',
            '//div[label[text()="显示开始时间:"]]//input',
            '//div[label[text()="显示结束时间:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        environment.click_button('//div[label[text()="分派开始时间:"]]//input')
        before_value = environment.batch_acquisition_input(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_cycle()
        after_value = environment.batch_acquisition_input(xpth_list)
        assert before_value == after_value and message == "保存成功"
        assert all(value == "133" for value in before_value)
        assert not environment.has_fail_message()

    @allure.story("周期页面-工作日的起始时间-不输入不允许保存，输入框颜色改变")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_time1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        ele = environment.get_find_element_xpath('//div[label[text()="工作日的起始时间:"]]//input')
        ActionChains(environment.driver).move_to_element(ele).perform()
        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(environment.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//i[@class="ivu-icon ivu-icon-ios-close-circle"]'
            ))
        )
        delete_icon.click()
        environment.click_save_button()
        message = environment.get_error_message()
        before_value = environment.get_find_element_xpath('//div[label[text()="工作日的起始时间:"]]//input').value_of_css_property("border-color")
        environment.right_refresh()
        assert before_value == "rgb(237, 64, 20)" and message == "请填写信息"
        assert not environment.has_fail_message()

    @allure.story("周期页面-输入工作日的起始时间和计划基准时间-保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_time2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        before_ele11 = environment.get_find_element_xpath('//div[label[text()="工作日的起始时间:"]]//input')
        before_ele22 = environment.get_find_element_xpath('//div[label[text()="计划基准时间:"]]//input')
        before_ele1 = before_ele11.get_attribute("value")
        before_ele2 = before_ele22.get_attribute("value")
        ActionChains(environment.driver).move_to_element(before_ele11).perform()
        # 2️⃣ 等待图标可见
        delete_icon1 = WebDriverWait(environment.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//i[@class="ivu-icon ivu-icon-ios-close-circle"]'
            ))
        )
        delete_icon1.click()
        ActionChains(environment.driver).move_to_element(before_ele22).perform()
        # 2️⃣ 等待图标可见
        delete_icon2 = WebDriverWait(environment.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//i[@class="ivu-icon ivu-icon-ios-close-circle"]'
            ))
        )
        delete_icon2.click()
        environment.enter_texts('//div[label[text()="工作日的起始时间:"]]//input', before_ele2)
        environment.enter_texts('//div[label[text()="计划基准时间:"]]//input', before_ele1)
        environment.click_save_button()
        message = environment.get_find_message()
        after_ele1 = environment.get_find_element_xpath('//div[label[text()="工作日的起始时间:"]]//input').get_attribute("value")
        after_ele2 = environment.get_find_element_xpath('//div[label[text()="计划基准时间:"]]//input').get_attribute("value")
        assert before_ele1 == after_ele2 and before_ele2 == after_ele1 and message == "保存成功"
        assert not environment.has_fail_message()

    @allure.story("周期页面-计划基准日期，选择固定日期，保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_data1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        check = environment.get_find_element_xpath('//div[label[text()="计划基准日期:"]]/div/div/div[1]/label/span')
        if check.get_attribute("class") == "ivu-radio":
            check.click()

        environment.click_button('//div[label[text()="计划基准日期:"]]/div/div/div[1]/div//input')
        environment.click_button('//span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"]')
        data1 = environment.get_find_element_xpath('//div[label[text()="计划基准日期:"]]/div/div/div[1]/div//input').get_attribute("value")
        current_date = datetime.now()
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_cycle()
        data2 = current_date.strftime("%Y/%m/%d")
        environment.right_refresh()
        assert data1 == data2 and message == "保存成功"
        assert not environment.has_fail_message()

    @allure.story("周期页面-设置系统载入日期，保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_cycle_data2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_cycle()
        check = environment.get_find_element_xpath('//div[label[text()="计划基准日期:"]]/div/div/div[2]/label/span')
        if check.get_attribute("class") == "ivu-radio":
            check.click()
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_cycle()
        check2 = environment.get_find_element_xpath('//div[label[text()="计划基准日期:"]]/div/div/div[2]/label/span').get_attribute("class")
        environment.right_refresh()
        assert check2 == "ivu-radio ivu-radio-checked" and message == "保存成功"
        assert not environment.has_fail_message()

    @allure.story("排程页面-校验所有数字输入框-不输入不允许保存，输入框颜色改变")
    # @pytest.mark.run(order=1)
    def test_environment_plan_num(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        value = " "
        xpth_list = [
            '//div[label[text()="制造效率:"]]//input',
            '//div[label[text()="分派侯补数的上限:"]]//input',
            '//div[label[text()="自动补充制造订单序列号:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        div_xpth_list = [item.replace("//input", "//input/ancestor::div[2]") for item in xpth_list]
        environment.click_save_button()
        message = environment.get_error_message()
        before_value = environment.get_border_color(div_xpth_list)
        environment.right_refresh()
        assert all(color == "rgb(237, 64, 20)" for color in before_value) and message == "请填写信息"
        assert not environment.has_fail_message()

    @allure.story("排程页面-校验所有数字输入框-超过最大值为9999999999")
    # @pytest.mark.run(order=1)
    def test_environment_plan_numinput2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        value = "11111111111111111111111111"
        xpth_list = [
            '//div[label[text()="制造效率:"]]//input',
            '//div[label[text()="分派侯补数的上限:"]]//input',
            '//div[label[text()="自动补充制造订单序列号:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        before_value = environment.batch_acquisition_input(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(xpth_list)
        num_ = "9999999999"
        print(v for v in after_value)
        environment.right_refresh()
        assert all(num_ == v for v in after_value) and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("排程页面-校验所有数字输入框-只允许输入数字")
    # @pytest.mark.run(order=1)
    def test_environment_plan_numinput3(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        value = "QAseE1@!><?+_+=-33."
        xpth_list = [
            '//div[label[text()="制造效率:"]]//input',
            '//div[label[text()="分派侯补数的上限:"]]//input',
            '//div[label[text()="自动补充制造订单序列号:"]]//input',
        ]
        environment.batch_modify_input(xpth_list, value)
        environment.click_button('//div[label[text()="制造效率:"]]//input')
        before_value = environment.batch_acquisition_input(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(xpth_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(value == "133" for value in before_value)
        assert not environment.has_fail_message()

    @allure.story("排程页面-修改全部下拉框，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_select1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        select_list = [
            {"select": '//div[label[text()="设置时间计算方法:"]]/div//i', "value": '//li[text()="最大值(出现顺序)"]'},
            {"select": '//div[label[text()="消息级别:"]]/div//i', "value": '//li[text()="错误信息"]'},
        ]
        environment.batch_modify_select_input(select_list)
        select_input_list = [item["select"].replace("//i", "//input") for item in select_list]
        before_value = environment.batch_acquisition_input(select_input_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(select_input_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("排程页面-修改全部下拉框，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_select2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        select_list = [
            {"select": '//div[label[text()="设置时间计算方法:"]]/div//i', "value": '//li[text()="最大值(所有资源)"]'},
            {"select": '//div[label[text()="消息级别:"]]/div//i', "value": '//li[text()="详细"]'},
        ]
        environment.batch_modify_select_input(select_list)
        select_input_list = [item["select"].replace("//i", "//input") for item in select_list]
        before_value = environment.batch_acquisition_input(select_input_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(select_input_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(after_value), "列表中存在为空或为假值的元素！"
        assert not environment.has_fail_message()

    @allure.story("排程页面-所有复选框都点击取消勾选，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_checkbox1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        xpth_list = [
            '//div[label[text()="相同品目的设置时间为零:"]]/div//input',
            '//div[label[text()="同一分割作业的设置时间为零:"]]/div//input',
            '//div[label[text()="启用移动时间MAX:"]]/div//input',
            '//div[label[text()="启用资源锁定:"]]/div//input',
            '//div[label[text()="保存计划消息:"]]/div//input',
            '//div[label[text()="显示计划评估:"]]/div//input',
        ]
        environment.update_checkbox(xpth_list, new_value=False)
        before_value = environment.get_checkbox_value(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.get_checkbox_value(xpth_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert not all(after_value)
        assert not environment.has_fail_message()

    @allure.story("排程页面-所有复选框都勾选，并且保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_checkbox2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        xpth_list = [
            '//div[label[text()="相同品目的设置时间为零:"]]/div//input',
            '//div[label[text()="同一分割作业的设置时间为零:"]]/div//input',
            '//div[label[text()="启用移动时间MAX:"]]/div//input',
            '//div[label[text()="启用资源锁定:"]]/div//input',
            '//div[label[text()="保存计划消息:"]]/div//input',
            '//div[label[text()="显示计划评估:"]]/div//input',
        ]
        environment.update_checkbox(xpth_list, new_value=True)
        before_value = environment.get_checkbox_value(xpth_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.get_checkbox_value(xpth_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(after_value)
        assert not environment.has_fail_message()

    @allure.story("排程页面-文本输入框全部输入，保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_input1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        value = "QAseE1@!><?+_+=-33."
        xpath_list = [
            f'//label[text()="备注{i}:"]/following-sibling::div//input'
            for i in range(1, 5)
        ]
        environment.batch_modify_input(xpath_list, value)
        before_value = environment.batch_acquisition_input(xpath_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(xpath_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(value == "QAseE1@!><?+_+=-33." for value in before_value)
        assert not environment.has_fail_message()

    @allure.story("排程页面-文本输入框全部输入，保存成功")
    # @pytest.mark.run(order=1)
    def test_environment_plan_input2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_plan()
        value = "全部-="
        xpath_list = [
            f'//label[text()="备注{i}:"]/following-sibling::div//input'
            for i in range(1, 5)
        ]
        environment.batch_modify_input(xpath_list, value)
        before_value = environment.batch_acquisition_input(xpath_list)
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        environment.click_plan()
        after_value = environment.batch_acquisition_input(xpath_list)
        environment.right_refresh()
        assert before_value == after_value and message == "保存成功"
        assert all(value == "全部-=" for value in before_value)
        assert not environment.has_fail_message()

    @allure.story("标识页面-设置商标成功")
    # @pytest.mark.run(order=1)
    def test_environment_trademark_input1(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_trademark()
        ele = environment.get_find_element_xpath('//p[text()=" 商标名称: "]/following-sibling::div//input')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        environment.enter_texts('//p[text()=" 商标名称: "]/following-sibling::div//input', "测试")
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        text = environment.get_find_element_xpath('//div[@class="navTop"]/div/span').get_attribute("innerText")
        environment.right_refresh()
        assert message == "保存成功" and text == "测试"
        assert not environment.has_fail_message()

    @allure.story("标识页面-设置商标成功")
    # @pytest.mark.run(order=1)
    def test_environment_trademark_input2(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        environment.click_trademark()
        ele = environment.get_find_element_xpath('//p[text()=" 商标名称: "]/following-sibling::div//input')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        environment.enter_texts('//p[text()=" 商标名称: "]/following-sibling::div//input', "Elligent SCP")
        environment.click_save_button()
        message = environment.get_find_message()
        environment.right_refresh()
        text = environment.get_find_element_xpath('//div[@class="navTop"]/div/span').get_attribute("innerText")
        environment.right_refresh()
        assert message == "保存成功" and text == "Elligent SCP"
        assert not environment.has_fail_message()

    @allure.story("恢复默认设置")
    # @pytest.mark.run(order=1)
    def test_environment_restore_default_settings(self, login_to_environment):
        driver = login_to_environment  # WebDriver 实例
        environment = EnvironmentPage(driver)  # 用 driver 初始化 EnvironmentPage
        check1 = environment.get_find_element_xpath('//div[label[text()="变更使用时间:"]]/div//span').get_attribute("class")
        if check1 == "ivu-checkbox ivu-checkbox-checked":
            environment.click_button('//div[label[text()="变更使用时间:"]]/div//span')
        select_list = [
            {"select": '//div[label[text()="用鼠标移动工作方法:"]]/div//i', "value": '//li[text()="无限能力"]'},
        ]
        environment.batch_modify_select_input(select_list)

        environment.click_cycle()
        xpath_value_map = {
            '//div[label[text()="分派开始时间:"]]//input': "0",
            '//div[label[text()="分派结束时间:"]]//input': "90",
            '//div[label[text()="生产指令结束时间:"]]//input': "0",
            '//div[label[text()="显示开始时间:"]]//input': "-3",
            '//div[label[text()="显示结束时间:"]]//input': "100",
        }
        environment.batch_modify_inputs(xpath_value_map)

        environment.click_plan()
        xpath_value_map1 = {
            '//div[label[text()="制造效率:"]]//input': "1",
            '//div[label[text()="分派侯补数的上限:"]]//input': "1000",
            '//div[label[text()="自动补充制造订单序列号:"]]//input': "1",
        }
        environment.batch_modify_inputs(xpath_value_map1)

        check2 = environment.get_find_element_xpath('//div[label[text()="启用资源锁定:"]]/div//input').get_attribute("class")
        if check2 == "ivu-checkbox ivu-checkbox-checked":
            environment.click_button('//div[label[text()="变更使用时间:"]]/div//span')

        sleep(2)
        environment.click_save_button()
        assert environment.get_find_message() == "保存成功"
        assert not environment.has_fail_message()



