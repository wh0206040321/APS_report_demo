import logging
import random
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.shift_page import ShiftPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_shift():
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
        page.click_button('(//span[text()="班次"])[1]')  # 点击班次
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("班次表测试用例")
@pytest.mark.run(order=9)
class TestShiftPage:
    @allure.story("添加班次信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_shift_addfail(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        layout = "测试布局A"
        shift.add_layout(layout)
        # 获取布局名称的文本元素
        name = shift.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        shift.click_add_button()
        # 班次代码xpath
        input_box = shift.get_find_element_xpath(
            '(//label[text()="代码"])[1]/parent::div//input'
        )

        shift.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert name == layout
        assert not shift.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_shift_addnum(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 填写数字的第一个数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//input[1]', "e1.文字abc。？~1"
        )
        sleep(1)
        # 获取表示顺序数字框
        shiftnum = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//input[1]'
        ).get_attribute("value")
        assert shiftnum == "11", f"预期{shiftnum}"
        assert not shift.has_fail_message()

    @allure.story("第一个时间数字框超过23默认为23，第二个时间数字框超过24默认为24")
    # @pytest.mark.run(order=1)
    def test_shift_adddatenum(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 填写第一个日期数字的第一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[1]//input',
            "345",
        )

        # 填写第二个日期数字的第二个一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[4]//input',
            "345",
        )
        sleep(1)
        # 获取表示顺序数字框
        shiftnum1 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[1]//input'
        ).get_attribute("value")
        shiftnum2 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[4]//input'
        ).get_attribute("value")
        assert shiftnum1 == "23" and shiftnum2 == "24", f"预期{shiftnum1},{shiftnum2}"
        assert not shift.has_fail_message()

    @allure.story(
        "第一个时间数字框分钟和秒超过59默认为59，第二个时间数字框分钟和秒超过59默认为59"
    )
    # @pytest.mark.run(order=1)
    def test_shift_addminutesnum(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 填写第一个日期数字的第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[2]//input',
            "345",
        )
        # 填写第一个日期数字的第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[3]//input',
            "345",
        )

        # 填写第二个日期数字的第二个第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input',
            "345",
        )
        # 填写第二个日期数字的第二个第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[6]//input',
            "345",
        )
        shift.click_button(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input'
        )

        # 获取表示顺序数字框
        shiftnum1 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[2]//input'
        ).get_attribute("value")
        shiftnum2 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[3]//input'
        ).get_attribute("value")
        shiftnum3 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input'
        ).get_attribute("value")
        shiftnum4 = shift.get_find_element_xpath(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[6]//input'
        ).get_attribute("value")
        assert (
            shiftnum1 == "59"
            and shiftnum2 == "59"
            and shiftnum3 == "59"
            and shiftnum4 == "59"
        )
        assert not shift.has_fail_message()

    @allure.story("第一个时间数字框不允许超过第二个时间数字框 添加失败")
    # @pytest.mark.run(order=1)
    def test_shift_adddateminnum_comparison(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 填写第一个日期数字的第一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[1]//input',
            "23",
        )
        # 填写第一个日期数字的第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[2]//input',
            "30",
        )
        # 填写第一个日期数字的第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[3]//input',
            "30",
        )

        # 填写第二个日期数字的第二个一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[4]//input',
            "8",
        )
        # 填写第二个日期数字的第二个第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input',
            "0",
        )
        # 填写第二个日期数字的第二个第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[6]//input',
            "0",
        )
        shift.click_button(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/parent::div/div[2]/button'
        )
        message = shift.get_error_message()
        assert message == "开始时间不能大于、等于结束时间"
        assert not shift.has_fail_message()

    @allure.story("第一个时间数字框不允许超过第二个时间数字框  添加成功")
    # @pytest.mark.run(order=1)
    def test_shift_adddateminnum_successes(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 填写第一个日期数字的第一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[1]//input',
            "6",
        )
        # 填写第一个日期数字的第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[2]//input',
            "30",
        )
        # 填写第一个日期数字的第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[3]//input',
            "30",
        )

        # 填写第二个日期数字的第二个一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[4]//input',
            "12",
        )
        # 填写第二个日期数字的第二个第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input',
            "0",
        )
        # 填写第二个日期数字的第二个第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[6]//input',
            "0",
        )
        shift.click_button(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/parent::div/div[2]/button'
        )

        data = shift.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr[td[3]//button]/td[1]'
        )
        assert data.text == "1"
        assert not shift.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_shift_addsel(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 显示颜色下拉框
        shift.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        # 显示颜色
        shift.click_button('//span[text()="RGB(100,255,178)"]')
        # 获取下拉框数据
        shiftsel = shift.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text
        assert shiftsel == "RGB(100,255,178)", f"预期{shiftsel}"
        assert not shift.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_shift_textverify(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        shift.click_add_button()  # 检查点击添加
        # 输入班次代码
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', num)
        # 点击确定
        shift.click_confirm()
        adddata = shift.get_find_element_xpath(
            f'(//span[text()="{num}"])[1]/ancestor::tr[1]/td[2]'
        )
        assert adddata.text == num, f"预期数据是{num}，实际得到{adddata}"
        assert not shift.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_shift_addsuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "111"
        shift.click_add_button()  # 检查点击添加
        # 输入班次代码
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', {name})
        # 点击确定
        shift.click_confirm()
        adddata = shift.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        )
        assert adddata.text == name, f"预期数据是111，实际得到{adddata}"
        assert not shift.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_shift_addrepeat(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage

        shift.click_add_button()  # 检查点击添加
        # 输入班次代码
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', "111")
        # 点击确定
        shift.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 等待弹窗出现（最多等10秒）
        error_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                ("xpath", '//div[text()=" 记录已存在,请检查！ "]')
            )
        )
        assert (
            error_popup.text == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not shift.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_shift_delcancel(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "111"
        # 定位内容为‘111’的行
        shift.click_button(f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]')
        shift.click_del_button()  # 点击删除
        # 点击取消
        shift.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位内容为‘111’的行
        shiftdata = shift.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        )
        assert shiftdata.text == name, f"预期{shiftdata}"
        assert not shift.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_shift_addsuccess1(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        shift.click_add_button()  # 检查点击添加
        # 输入班次代码
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', name)

        # 填写第一个日期数字的第一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[1]//input',
            "6",
        )
        # 填写第一个日期数字的第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[2]//input',
            "30",
        )
        # 填写第一个日期数字的第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[3]//input',
            "30",
        )

        # 填写第二个日期数字的第二个一个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[4]//input',
            "12",
        )
        # 填写第二个日期数字的第二个第二个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[5]//input',
            "0",
        )
        # 填写第二个日期数字的第二个第三个时间数字框
        shift.enter_texts(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/div[6]//input',
            "0",
        )
        shift.click_button(
            '//label[text()="时间"]/ancestor::div[1]//div[@class="left"]/parent::div/div[2]/button'
        )

        timedata = shift.get_find_element_xpath(
            '(//span[text()="时间"])[1]/ancestor::table/parent::div/parent::div/div[2]/table//tr[1]//td[2]//span'
        ).text

        # 点击确定
        shift.click_confirm()
        adddata = shift.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        assert adddata == timedata
        assert not shift.has_fail_message()

    @allure.story("修改班次代码重复")
    # @pytest.mark.run(order=1)
    def test_shift_editrepeat(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        # 选中晚班班次代码
        shift.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        shift.click_edi_button()
        # 班次代码输入白班
        sleep(1)
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', "111")
        # 点击确定
        shift.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 等待弹窗出现（最多等10秒）
        error_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                ("xpath", '//div[text()=" 记录已存在,请检查！ "]')
            )
        )
        assert error_popup.text == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not shift.has_fail_message()

    @allure.story("修改班次代码成功")
    # @pytest.mark.run(order=1)
    def test_shift_editcodesuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        # 选中产包装班次代码
        shift.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        shift.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 班次代码输入
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', f"{text}")
        # 点击确定
        shift.click_confirm()
        # 定位表格内容
        shiftdata = shift.get_find_element_xpath(
            f'(//span[contains(text(),"{name}")])[1]'
        ).text
        assert shiftdata == text, f"预期{shiftdata}"
        assert not shift.has_fail_message()

    @allure.story("把修改后的班次代码改回来")
    # @pytest.mark.run(order=1)
    def test_shift_editcodesuccess2(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        # 选中修改代码班次代码
        shift.click_button(f'(//span[contains(text(),"{name}")])[1]')
        # 点击修改按钮
        shift.click_edi_button()
        # 班次代码输入
        shift.enter_texts('(//label[text()="代码"])[1]/parent::div//input', name)
        # 点击确定
        shift.click_confirm()
        # 定位表格内容
        shiftdata = shift.get_find_element_xpath('(//span[text()="1测试A"])[1]').text
        assert shiftdata == name, f"预期{shiftdata}"
        assert not shift.has_fail_message()

    @allure.story("修改时间成功")
    # @pytest.mark.run(order=1)
    def test_shift_edittimesuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        # 选中修改代码班次代码
        shift.click_button(f'(//span[contains(text(),"{name}")])[1]')
        # 点击修改按钮
        shift.click_edi_button()
        # 点击编辑按钮
        shift.click_button('//span[text()="编辑"]')
        time1 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[1]//input'
        )
        time1.send_keys(Keys.CONTROL, "a")
        time1.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[1]//input', "5"
        )

        time2 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[2]//input'
        )
        time2.send_keys(Keys.CONTROL, "a")
        time2.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[2]//input', "5"
        )

        time3 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[3]//input'
        )
        time3.send_keys(Keys.CONTROL, "a")
        time3.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[3]//input', "5"
        )

        time4 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[4]//input'
        )
        time4.send_keys(Keys.CONTROL, "a")
        time4.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[4]//input', "8"
        )

        time5 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[5]//input'
        )
        time5.send_keys(Keys.CONTROL, "a")
        time5.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[5]//input', "5"
        )

        time6 = shift.get_find_element_xpath(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[6]//input'
        )
        time6.send_keys(Keys.CONTROL, "a")
        time6.send_keys(Keys.BACK_SPACE)
        shift.enter_texts(
            '//div[@class="shift-time p-b-10 flex-j-c-between"]/div[6]//input', "5"
        )

        shift.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)

        timedata = shift.get_find_element_xpath(
            '(//span[text()="时间"])[1]/ancestor::table/parent::div/parent::div/div[2]/table//tr[1]//td[2]//span'
        ).text

        # 点击确定
        shift.click_confirm()
        adddata = shift.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        assert adddata == timedata and adddata == "05:05:05-08:05:05"
        assert not shift.has_fail_message()

    @allure.story("修改显示颜色成功")
    # @pytest.mark.run(order=1)
    def test_shift_editcolorsuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1测试A"
        # 选中班次代码
        shift.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        shift.click_edi_button()
        sleep(2)
        # 生成随机数
        random_int = random.randint(1, 10)

        # 显示颜色下拉框
        shift.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        # 显示颜色
        shift.click_button(f'//span[text()="{random_int}"]')
        # 获取下拉框数据
        shiftsel = shift.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text
        # 点击确定
        shift.click_confirm()
        shiftautoGenerateFlag = shift.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr/td[4]/div'
        ).text
        assert shiftautoGenerateFlag == shiftsel
        assert not shift.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_shift_refreshsuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        sleep(1)  # 等待页面加载
        # 班次代码筛选框输入123
        shift.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', "123"
        )
        shift.click_ref_button()
        shifttext = shift.get_find_element_xpath(
            '//p[text()="代码"]/ancestor::div[2]//input'
        ).text
        assert shifttext == "", f"预期{shifttext}"
        assert not shift.has_fail_message()

    @allure.story("查询代码包含1成功")
    # @pytest.mark.run(order=1)
    def test_shift_selectcodesuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        name = "1"
        # 点击查询
        shift.click_sel_button()
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
        # 点击班次代码
        shift.click_button('//div[text()="代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        shift.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        shift.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        shift.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        shift.click_select_button()
        eles = shift.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[2]')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not shift.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_shift_addall(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        data_list = ["11测试全部数据", "20"]
        shift.click_add_button()  # 检查点击添加
        shift.add_input_all(data_list[0], data_list[1])
        sleep(1)
        shift.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', data_list[0]
        )
        # 缩放到最小（例如 60%）
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{data_list[0]}"]]]'
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
        bef_text = [f'{data_list[0]}', '20:20:20-21:20:20', 'RGB(100,255,178)', f'{data_list[0]}', f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text), start=1):
            if i == 6:
                assert str(e) in str(a), f"第7项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not shift.has_fail_message()

    @allure.story("重新打开浏览器，数据还存在")
    # @pytest.mark.run(order=1)
    def test_shift_restart(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        code = '11测试全部数据'
        shift.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', code
        )
        # 缩放到最小（例如 60%）
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{code}"]]]'
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
        bef_text = [code, '20:20:20-21:20:20', 'RGB(100,255,178)', code, f'{DateDriver.username}', '2025']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text), start=1):
            if i == 6:
                assert str(e) in str(a), f"第7项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not shift.has_fail_message()

    @allure.story("删除数据成功,删除数据删除布局成功")
    # @pytest.mark.run(order=1)
    def test_shift_delsuccess(self, login_to_shift):
        driver = login_to_shift  # WebDriver 实例
        shift = ShiftPage(driver)  # 用 driver 初始化 ShiftPage
        layout = "测试布局A"

        value = ['11测试全部数据', '111', '1测试A', '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        shift.del_all(value)
        data = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        shift.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in data)
        assert 0 == len(after_layout)
        assert not shift.has_fail_message()
