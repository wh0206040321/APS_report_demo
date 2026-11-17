import logging
import random
from datetime import date
from time import sleep
import re

import allure
import pytest
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.adds_page import AddsPages
from Pages.materialPage.materialcalendar_page import MaterialCalendar
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
        page.click_button('(//span[text()="物控管理"])[1]')  # 点击物控管理
        page.click_button('(//span[text()="物控基础数据"])[1]')  # 点击物控基础数据
        page.click_button('(//span[text()="收货日历"])[1]')  # 点击收货日历
        yield driver
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("收货日历表测试用例")
@pytest.mark.run(order=103)
class TestMaterialCalendarPage:
    @allure.story("添加收货日历信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addfail(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        layout = "测试布局A"
        calendar.add_layout(layout)
        name = calendar.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        calendar.click_add_button()
        # 点击确定
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        message = calendar.get_error_message()
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        # 检查元素是否包含子节点
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not calendar.has_fail_message()

    @allure.story("添加信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addfail1(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar

        calendar.click_add_button()
        calendar.enter_texts(
            "//div[span[text()=' 收货日历编码 ']]/following-sibling::div//input", "111"
        )
        # 点击确定
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        message = calendar.get_error_message()
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        # 检查元素是否包含子节点
        assert message == "收货区间不能为空"
        assert not calendar.has_fail_message()

    @allure.story("添加按天数据成功-收货时间点全天")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addDateSuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar

        name = '1测试A'

        calendar.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        calendar.enter_texts(
            "//div[span[text()=' 收货日历编码 ']]/following-sibling::div//input", name
        )
        calendar.receiving_calendar('按天')

        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', name)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]').text

        assert code == name and date == '按天' and time == '2028/09/15-2028/09/25' and deliveryTimes == '全天'
        assert not calendar.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addtest(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.click_ref_button()
        test_data = ["测试数据A", "测试数据B"]
        for supplier_code in test_data:
            # 检查数据是否已经存在
            rows = calendar.finds_elements(
                By.XPATH,
                f'//tr[./td[2][.//span[text()="{supplier_code}"]]]/td[2]'
            )
            # 不存在才新增
            if len(rows) == 0:
                calendar.click_add_button()
                # 输入框要修改的值
                calendar.enter_texts(
                    "//div[span[text()=' 收货日历编码 ']]/following-sibling::div//input", supplier_code
                )
                calendar.receiving_calendar('按天')

                calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
                calendar.get_find_message()
                calendar.select_input('收货日历编码', supplier_code)
                code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{supplier_code}"]]]/td[2]').text
                date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{supplier_code}"]]]/td[3]').text
                time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{supplier_code}"]]]/td[4]').text
                deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{supplier_code}"]]]/td[5]').text

                assert code == supplier_code and date == '按天' and time == '2028/09/15-2028/09/25' and deliveryTimes == '全天'

        # 检查页面是否出现失败提示
        assert not calendar.has_fail_message()

    @allure.story("添加按周数据成功-收货时间点休息")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addWeekSuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar

        name = '1测试B'

        calendar.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        calendar.enter_texts(
            "//div[span[text()=' 收货日历编码 ']]/following-sibling::div//input", name
        )
        calendar.receiving_calendar('按周')
        calendar.click_button('//label[text()=" 休息"]')

        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', name)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]').text

        assert code == name and date == '按周' and time == '星期一;星期二;星期三;星期四;星期五;星期六;星期日' and deliveryTimes == '休息'
        assert not calendar.has_fail_message()

    @allure.story("添加按月数据成功-收货时间点时间点")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addMonthSuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        name = '1测试C'
        time = [[1, 2], [111, 111]]

        calendar.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        calendar.enter_texts(
            "//div[span[text()=' 收货日历编码 ']]/following-sibling::div//input", name
        )
        calendar.receiving_calendar('按月')
        calendar.addtime(time)
        calendar.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', name)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]').text

        assert code == name and date == '按月' and time == '21;24;26' and deliveryTimes == '01:02;23:59'
        assert not calendar.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_addall(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        adds = AddsPages(driver)
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        input_value = '1测试全部数据'
        time = [[1, 2], [111, 111]]
        calendar.click_add_button()
        calendar.receiving_calendar('按月')
        calendar.addtime(time)
        calendar.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        custom_xpath_list = [
            f'//div[span[text()=" 自定义字符{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        text_list = [
            '//div[span[text()=" 收货日历编码 "]]/following-sibling::div//input',
            '//div[span[text()=" 备注 "]]/following-sibling::div//input',
        ]
        text_list.extend(custom_xpath_list)
        adds.batch_modify_input(text_list, input_value)

        input_num_value = '1'
        num_xpath_list1 = [
            f'//div[span[text()=" 自定义数值{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]

        num_list = [
            '//div[span[text()=" 优先级 "]]/following-sibling::div//input',
        ]
        num_list.extend(num_xpath_list1)
        adds.batch_modify_input(num_list, input_num_value)

        time_xpath_list = [
            f'//div[span[text()=" 自定义日期{i} "]]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        adds.batch_modify_input(time_xpath_list, '2026/09/16 00:00:00')

        all_value = text_list + num_list + time_xpath_list
        len_num = len(all_value)
        before_all_value = adds.batch_acquisition_input(all_value)
        calendar.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        driver.refresh()
        sleep(3)
        num = adds.go_settings_page()
        sleep(2)
        calendar.select_input('收货日历编码', input_value)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{input_value}"]]]/td[2]').text
        datetime = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{input_value}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{input_value}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{input_value}"]]]/td[5]').text
        sleep(1)
        calendar.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{input_value}"]]')
        sleep(1)
        calendar.click_edi_button()
        sleep(1)
        after_all_value = adds.batch_acquisition_input(all_value)
        username = calendar.get_find_element_xpath('//div[span[text()=" 更新者 "]]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = calendar.get_find_element_xpath(
            '//div[span[text()=" 更新时间 "]]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert code == input_value and datetime == '按月' and time == '21;24;26' and deliveryTimes == '01:02;23:59' and before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 5)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not calendar.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_delcancel(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar

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

    @allure.story("修改收货日历模式成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_editCalendarModesuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.right_refresh('收货日历')
        calendar.wait_for_loading_to_disappear()
        name = '1测试全部数据'
        calendar.select_input('收货日历编码', name)
        sleep(1)
        # 定位第一行
        calendar.click_button(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        )
        # 点击修改按钮
        calendar.click_edi_button()
        calendar.receiving_calendar('按周')
        calendar.click_button('//label[text()=" 休息"]')

        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        sleep(1)
        calendar.select_input('收货日历编码', name)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]').text
        assert code == name and date == '按周' and time == '星期一;星期二;星期三;星期四;星期五;星期六;星期日' and deliveryTimes == '休息'
        assert not calendar.has_fail_message()

    @allure.story("修改收货日历时间成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_editshiftsuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        name = '1测试全部数据'
        calendar.select_input('收货日历编码', name)
        sleep(1)
        # 定位第一行
        calendar.click_button(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        )
        # 点击修改按钮
        calendar.click_edi_button()
        time = [[1, 1], [1, 1], [1, 1]]

        # 输入框要修改的值
        calendar.receiving_calendar('按月')
        calendar.addtime(time)
        calendar.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', name)
        code = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]').text
        date = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]').text
        time = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]').text
        deliveryTimes = calendar.get_find_element_xpath(f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]').text
        assert code == name and date == '按月' and time == '21;24;26' and deliveryTimes == '01:01;11:11;23:59'
        assert not calendar.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_refreshsuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar

        calendar.select_input('收货日历编码', '123')
        calendar.click_ref_button()
        calendartext = calendar.get_find_element_xpath(
            '//div[div[span[text()=" 收货日历编码"]]]//input'
        ).text
        assert calendartext == "", f"预期{calendartext}"
        assert not calendar.has_fail_message()

    @allure.story("查询收货日历编码成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_selectcodesuccess(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
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
        calendar.click_button('//div[text()="收货日历编码" and contains(@optid,"opt_")]')
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
        calendar.right_refresh('收货日历')
        assert calendarcode == ele
        assert not calendar.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_select2(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = calendar.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            calendar.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            calendar.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//input')
        eles = calendar.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        calendar.right_refresh('收货日历')
        assert len(eles) == 0
        assert not calendar.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_select3(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        name = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        calendar.hover("包含")
        sleep(1)
        calendar.select_input('收货日历编码', first_char)
        sleep(1)
        eles = calendar.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        calendar.right_refresh('收货日历')
        assert all(first_char.lower() in text.lower() for text in list_)
        assert not calendar.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_select4(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.right_refresh('收货日历')
        name = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        if name == '*':
            for i in range(1, 10):
                name = calendar.get_find_element_xpath(
                    f'//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[{i}]//td[2]').get_attribute(
                    'innerText')
                if name != '*':
                    break
        first_char = name[:1] if name else ""
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        calendar.hover("符合开头")
        sleep(1)
        calendar.select_input('收货日历编码', first_char)
        sleep(1)
        eles = calendar.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).lower().startswith(first_char.lower()) for item in list_)
        calendar.right_refresh('收货日历')
        assert not calendar.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_select5(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.right_refresh('收货日历')
        name = calendar.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        if name == '*':
            for i in range(1, 10):
                name = calendar.get_find_element_xpath(
                    f'//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[{i}]//td[2]').get_attribute(
                    'innerText')
                if name != '*':
                    break
        last_char = name[-1:] if name else ""
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        calendar.hover("符合结尾")
        sleep(1)
        calendar.select_input('收货日历编码', last_char)
        sleep(1)
        eles = calendar.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).lower().endswith(last_char.lower()) for item in list_)
        calendar.right_refresh('收货日历')
        assert not calendar.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_clear(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.right_refresh('收货日历')
        name = "3"
        sleep(1)
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        calendar.hover("包含")
        sleep(1)
        calendar.select_input('收货日历编码', name)
        sleep(1)
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]')
        calendar.hover("清除所有筛选条件")
        sleep(1)
        ele = calendar.get_find_element_xpath(
            '//div[div[span[text()=" 收货日历编码"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        calendar.right_refresh('收货日历')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not calendar.has_fail_message()

    # @allure.story("模拟ctrl+i添加重复")
    # # @pytest.mark.run(order=1)
    # def test_materialcalendar_ctrlIrepeat(self, login_to_calendar):
    #     driver = login_to_calendar  # WebDriver 实例
    #     calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
    #     calendar.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
    #     ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
    #     ele1 = calendar.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
    #         "innerText")
    #     calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     message = calendar.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
    #     calendar.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
    #     calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
    #     assert message == '记录已存在,请检查！'
    #     assert not calendar.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_ctrlI(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        calendar.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        calendar.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = calendar.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', '1没有数据添加')
        ele2 = calendar.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not calendar.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_ctrlM(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        calendar.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        calendar.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = calendar.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', '1没有数据修改')
        ele2 = calendar.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        assert not calendar.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_ctrlC(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.right_refresh('收货日历')
        calendar.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = calendar.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        calendar.click_button('//div[div[span[text()=" 收货日历编码"]]]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = calendar.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        calendar.right_refresh('收货日历')
        assert all(before_data in ele for ele in eles)
        assert not calendar.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_shiftdel(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        calendar.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = calendar.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        sleep(1)
        calendar.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        calendar.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改1')
        calendar.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        calendar.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据修改12')
        sleep(1)
        ele1 = calendar.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
        ele2 = calendar.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        calendar.get_find_message()
        calendar.select_input('收货日历编码', '1没有数据修改1')
        ele11 = calendar.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        ele22 = calendar.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        calendar.select_input('收货日历编码', '1没有数据修改')
        sleep(1)
        before_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[2]']
        calendar.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = calendar.get_find_element_xpath(elements[2])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        calendar.click_del_button()
        calendar.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = calendar.get_find_message()
        calendar.wait_for_loading_to_disappear()
        after_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        calendar.select_input('收货日历编码', '1测试')
        sleep(1)
        before_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[4]//td[1])[2]']
        calendar.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = calendar.get_find_element_xpath(elements[3])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        calendar.click_del_button()
        calendar.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = calendar.get_find_message()
        calendar.wait_for_loading_to_disappear()
        after_data = calendar.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 4, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not calendar.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_shift(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        calendar.click_ref_button()
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        calendar.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = calendar.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = calendar.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not calendar.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_ctrls(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        calendar.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = calendar.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = calendar.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        calendar.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = calendar.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not calendar.has_fail_message()

    @allure.story("删除数据，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_materialcalendar_deletelayout(self, login_to_calendar):
        driver = login_to_calendar  # WebDriver 实例
        calendar = MaterialCalendar(driver)  # 用 driver 初始化 MaterialCalendar
        layout = "测试布局A"
        calendar.wait_for_loading_to_disappear()
        sleep(2)

        calendar.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not calendar.has_fail_message()
