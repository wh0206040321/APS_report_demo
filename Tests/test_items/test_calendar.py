import logging
import random
import re
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.calendar_page import Calendar
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_calendar():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        # 初始化 driver
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
        page.click_button('(//span[text()="计划管理"])[1]')  # 点击计划管理
        page.click_button('(//span[text()="计划基础数据"])[1]')  # 点击计划基础数据
        page.click_button('(//span[text()="生产日历"])[1]')  # 点击生产日历
        page.wait_for_loading_to_disappear()
        yield driver
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("生产日历表测试用例")
@pytest.mark.run(order=11)
class TestCalendarPage:
    @allure.story("添加生产日历信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_calendar_addfail(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        layout = "测试布局A"
        calendar.add_layout(layout)
        name = calendar.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        calendar.click_add_button()
        # 资源
        input_box = calendar.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )
        # 班次
        inputshift_box = calendar.get_find_element_xpath(
            '(//label[text()="班次"])[1]/parent::div//input'
        )
        calendar.click_confirm_button()
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputshift_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert layout == name
        assert not calendar.has_fail_message()

    @allure.story("添加生产日历信息 填写资源不填写班次 不允许提交")
    # @pytest.mark.run(order=1)
    def test_calendar_addresourcefail(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(2, 7)
        sleep(1)
        calendar.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
        sleep(1)
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 班次
        inputshift_box = calendar.get_find_element_xpath(
            '(//label[text()="班次"])[1]/parent::div//input'
        )
        calendar.click_confirm_button()
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        bordername_color = inputshift_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert bordername_color == expected_color, f"预期边框颜色为{bordername_color}"
        assert not calendar.has_fail_message()

    @allure.story("添加生产日历信息 填写班次不填写资源 不允许提交")
    # @pytest.mark.run(order=1)
    def test_calendar_addshiftfail(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()
        # 资源
        input_box = calendar.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )

        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        calendar.click_button(f'(//span[@class="vxe-cell--checkbox"])[1]')
        sleep(1)
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        calendar.click_confirm_button()
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        calendar.right_refresh('生产日历')
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not calendar.has_fail_message()

    @allure.story("添加生产日历信息 填写班次填写资源 不填写日期 不允许提交")
    # @pytest.mark.run(order=1)
    def test_calendar_addfails(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        calendar.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        sleep(1)
        random_int1 = random.randint(2, 10)
        calendar.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int1}]')
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        calendar.click_confirm_button()
        message = calendar.get_error_message()
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        calendar.right_refresh('生产日历')
        assert message == "请先填写表单"
        assert not calendar.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_calendar_addnum(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()  # 检查点击添加
        # 资源量
        resource = calendar.get_find_element_xpath(
            '//label[text()="资源量"]/ancestor::div[1]//input[1]'
        )
        # 删除资源量输入框
        resource.send_keys(Keys.BACK_SPACE, "a")
        # 输入文本
        calendar.enter_texts(
            '//label[text()="资源量"]/ancestor::div[1]//input[1]', "e1.文字abc。？~1++3"
        )
        sleep(1)
        # 获取表示顺序数字框
        calendarnum = calendar.get_find_element_xpath(
            '//label[text()="资源量"]/ancestor::div[1]//input[1]'
        ).get_attribute("value")
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        calendar.right_refresh('生产日历')
        assert calendarnum == "113", f"预期{calendarnum}"
        assert not calendar.has_fail_message()

    @allure.story("添加数据成功 - 星期")
    # @pytest.mark.run(order=1)
    def test_calendar_addweeksuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        calendar.click_button('//table[@class="vxe-table--header"]//th[2]//span[@class="vxe-cell--checkbox"]')
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1.5)
        # 获取勾选的资源代码
        resource = calendar.get_find_element_xpath(
            '//label[text()="资源"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox"])[{random_int1}]')
        sleep(1)
        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的班次
        resource1 = calendar.get_find_element_xpath(
            '//label[text()="班次"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        calendar.enter_texts('//div[label[text()="优先级"]]//input', "200")

        calendar.click_button('(//div[text()=" 星期 "])[1]')
        element = calendar.get_find_element_xpath(
            '(//div[@class="d-flex"])[1]/label//input'
        )
        # 强制点击
        driver.execute_script("arguments[0].click();", element)
        calendar.click_confirm_button()
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        adddata = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addshift = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        assert adddata == resource and addshift == resource1
        assert not calendar.has_fail_message()

    @allure.story("添加数据成功 - 日期")
    # @pytest.mark.run(order=1)
    def test_calendar_adddatesuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        calendar.click_add_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 5)
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = calendar.get_find_element_xpath(
            '//label[text()="资源"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox"])[{random_int1}]')

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的班次
        resource1 = calendar.get_find_element_xpath(
            '//label[text()="班次"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        # 点击第一个日期时间
        calendar.click_button('(//input[@placeholder="请选择时间"])[1]')

        calendar.click_button('(//em[text()="13"])[1]')
        # 点击第二个日期时间
        calendar.click_button('(//input[@placeholder="请选择时间"])[2]')

        calendar.click_button('(//em[text()="20"])[2]')

        # 点击添加按钮
        calendar.click_button('(//span[text()="添加"])[1]')

        calendar.click_confirm_button()

        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )

        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        adddata = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addshift = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        assert adddata == resource and addshift == resource1
        assert not calendar.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_calendar_numverify(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        calendar.click_add_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 5)
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = calendar.get_find_element_xpath(
            '//label[text()="资源"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        calendar.wait_for_loading_to_disappear()
        calendar.click_button(
            f'(//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox"])[{random_int1}]')

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的班次
        resource1 = calendar.get_find_element_xpath(
            '//label[text()="班次"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")
        calendar.enter_texts('//label[text()="资源量"]/parent::div/div[1]//input[1]', num)
        calendar.enter_texts('//label[text()="备注"]/parent::div/div[1]//input[1]', num)
        # 点击第一个日期时间
        calendar.click_button('(//input[@placeholder="请选择时间"])[1]')

        calendar.click_button('(//em[text()="13"])[1]')
        # 点击第二个日期时间
        calendar.click_button('(//input[@placeholder="请选择时间"])[2]')

        calendar.click_button('(//em[text()="20"])[2]')

        # 点击添加按钮
        calendar.click_button('(//span[text()="添加"])[1]')

        calendar.click_confirm_button()

        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )

        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        adddata = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addshift = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        addnum = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[6]'
        ).text
        addtext = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        assert adddata == resource and addshift == resource1 and addnum == '100000' and addtext == num
        assert not calendar.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_calendar_addall(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        # 清空之前的共享数据
        SharedDataUtil.clear_data()
        data_list = 20
        calendar.click_add_button()  # 检查点击添加
        resource, shift = calendar.add_input_all(data_list)
        # 保存数据
        SharedDataUtil.save_data(
            {"resource": resource, "shift": shift}
        )
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        # 缩放到最小（例如 60%）
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)

        row_xpath = '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = [f'{resource}', '*', f'{shift}', f'{data_list}', f'{data_list}', f'{data_list}', f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text), start=1):
            if i == 8:
                assert str(e) in str(a), f"第8项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not calendar.has_fail_message()

    @allure.story("重新打开浏览器，数据还存在")
    # @pytest.mark.run(order=1)
    def test_calendar_restart(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        data_list = "20"
        shared_data = SharedDataUtil.load_data()
        resource = shared_data.get("resource")
        shift = shared_data.get("shift")
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        # 缩放到最小（例如 60%）
        driver.execute_script("document.body.style.zoom='0.8'")
        sleep(1)

        row_xpath = '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = [f'{resource}', '*', f'{shift}', f'{data_list}', f'{data_list}', f'{data_list}', f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text), start=1):
            if i == 8:
                assert str(e) in str(a), f"第8项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not calendar.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_calendar_delcancel(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        # 定位第一行
        calendar.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[2]'
        )
        calendardata1 = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[2]'
        ).text
        calendar.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        calendar.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位第一行
        calendardata = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[2]'
        ).text
        assert (
                calendardata == calendardata1
        ), f"删除后的数据{calendardata}，删除前的数据{calendardata1}"
        assert not calendar.has_fail_message()

    @allure.story("修改生产日历资源成功")
    # @pytest.mark.run(order=1)
    def test_calendar_editcodesuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        # 定位第一行
        calendar.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[2]'
        )
        # 点击修改按钮
        calendar.click_edi_button()
        # 点击资源
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )

        # 勾选框
        random_int = random.randint(1, 6)
        sleep(1)
        calendar.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')
        sleep(1)

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = calendar.get_find_element_xpath(
            '//label[text()="资源"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        calendar.click_confirm_button()
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        adddata = calendar.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        assert adddata == resource
        assert not calendar.has_fail_message()

    @allure.story("修改生产日历班次成功")
    # @pytest.mark.run(order=1)
    def test_calendar_editshiftsuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        # 定位第一行
        calendar.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[2]'
        )
        # 点击修改按钮
        calendar.click_edi_button()
        # 点击班次
        calendar.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )

        # 勾选框
        random_int = random.randint(1, 2)
        sleep(1)
        calendar.click_button(
            '//span[@class="vxe-checkbox--icon iconfont icon-fuxuankuangdaiding"]'
        )
        sleep(1)
        calendar.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-checked-fill"])[1]'
        )
        calendar.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')
        sleep(1)

        calendar.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的班次代码
        shift = calendar.get_find_element_xpath(
            '//label[text()="班次"]/parent::div/div[1]//input[1]'
        ).get_attribute("value")

        calendar.click_confirm_button()
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        sleep(1)
        calendar.click_button(
            '//p[text()="更新时间"]/following-sibling::div'
        )
        adddata = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]/td[4]'
        ).text
        assert adddata == shift
        assert not calendar.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_calendar_refreshsuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar

        # 生产日历筛选框输入123
        calendar.enter_texts(
            '//p[text()="资源"]/ancestor::div[2]//input', "123"
        )
        calendar.click_ref_button()
        calendartext = calendar.get_find_element_xpath(
            '//p[text()="资源"]/ancestor::div[2]//input'
        ).text
        assert calendartext == "", f"预期{calendartext}"
        assert not calendar.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_calendar_selectcodesuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        calendar.wait_for_loading_to_disappear()
        ele = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).text
        # 点击查询
        calendar.click_sel_button()
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
        # 点击生产日历代码
        calendar.click_button('//div[text()="资源" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        calendar.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        calendar.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        calendar.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            ele,
        )
        sleep(1)

        # 点击确认
        calendar.click_select_button()
        # 定位第一行
        calendarcode = calendar.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        calendar.right_refresh('生产日历')
        assert calendarcode == ele
        assert not calendar.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_calendar_deletelayout(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = Calendar(driver)  # 用 driver 初始化 Calendar
        layout = "测试布局A"

        calendar.wait_for_loading_to_disappear()
        sleep(2)
        before_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())

        for i in range(4):
            calendar.click_flagdata()
            calendar.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
            calendar.click_del_button()
            calendar.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            calendar.get_find_message()
            calendar.right_refresh("生产日历")
            calendar.wait_for_loading_to_disappear()
            sleep(1)
        sleep(1)
        after_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert before_count - after_count == 4, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"

        calendar.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not calendar.has_fail_message()
