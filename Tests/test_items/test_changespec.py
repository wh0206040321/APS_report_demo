import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.changeR_page import ChangeR
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_changespec():
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
        page.click_button('(//span[text()="计划切换定义"])[1]')  # 点击计划切换定义
        page.click_button('(//span[text()="生产特征1切换"])[1]')  # 点击生产特征1切换
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("生产特征切换表测试用例")
@pytest.mark.run(order=14)
class TestChangeSpecPage:
    @allure.story("添加生产特征切换信息 不填写数据点击确认 不允许提交，添加新布局，")
    # @pytest.mark.run(order=1)
    def test_changespec_addfail(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        layout = "测试布局A"
        change.add_layout(layout)
        # 获取布局名称的文本元素
        name = change.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        change.click_add_button()
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 资源
        inputresource_box = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )
        # 前生产特征
        inputitem_box1 = change.get_find_element_xpath(
            '(//label[text()="前生产特征"])[1]/parent::div//input'
        )
        # 后资源
        inputitem_box2 = change.get_find_element_xpath(
            '(//label[text()="后生产特征"])[1]/parent::div//input'
        )

        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        borderresource_color = inputresource_box.value_of_css_property("border-color")
        borderitem_color1 = inputitem_box1.value_of_css_property("border-color")
        borderitem_color2 = inputitem_box2.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            borderresource_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderresource_color}"
        assert (
            borderitem_color1 == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderitem_color1}"
        assert (
            borderitem_color2 == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderitem_color2}"
        assert name == layout
        assert not change.has_fail_message()

    @allure.story("添加生产特征切换信息 填写资源不填写前生产特征和后生产特征 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changespec_addresourcefail(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 前生产特征
        inputitem_box1 = change.get_find_element_xpath(
            '(//label[text()="前生产特征"])[1]/parent::div//input'
        )
        # 后生产特征
        inputitem_box2 = change.get_find_element_xpath(
            '(//label[text()="后生产特征"])[1]/parent::div//input'
        )

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        borderitem_color1 = inputitem_box1.value_of_css_property("border-color")
        borderitem_color2 = inputitem_box2.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert borderitem_color1 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert borderitem_color2 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert not change.has_fail_message()

    @allure.story("添加生产特征切换信息 填写前生产特征和后生产特征不填写资源 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changespec_additemfail(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        change.click_add_button()
        # 资源
        input_box = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )

        # 点击前生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击确定
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not change.has_fail_message()

    @allure.story("添加资源切换信息 填写资源，前生产特征和后生产特征 不填写切换时间 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changespec_addtimefails(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 2)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除切换时间数字
        time = change.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div//input'
        )
        time.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = change.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not change.has_fail_message()

    @allure.story("添加资源切换信息 填写资源，前生产特征和后生产特征，填写切换时间，不填写优先度 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changespec_addprioritizationfail(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 2)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        sleep(1)
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除优先度
        prioritization = change.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritization.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = change.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not change.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_changespec_addnum(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR

        change.click_add_button()  # 检查点击添加
        # 切换时间
        time = change.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        )
        # 删除资源量输入框
        time.send_keys(Keys.BACK_SPACE, "a")
        # 输入文本
        change.enter_texts(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]',
            "e1文字abc。？~1+1-=3",
        )
        sleep(1)
        # 获取表示顺序数字框
        changeRnum = change.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        ).get_attribute("value")
        assert changeRnum == "1113", f"预期{changeRnum}"
        assert not change.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_changespec_numverify(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 2)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后品目
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源
        resource = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")
        # 获取前目录
        item1 = change.get_find_element_xpath(
            '(//label[text()="前生产特征"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)
        # 获取后目录
        item2 = change.get_find_element_xpath(
            '(//label[text()="后生产特征"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)

        change.enter_texts('(//label[text()="优先度"])[1]/parent::div//input', num)
        change.enter_texts('(//label[text()="备注"])[1]/parent::div//input', num)

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        sleep(1)
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )

        addresource = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        additem1 = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        additem2 = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        num_ = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[6]'
        ).text
        text_ = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        assert addresource == resource and additem1 == item1 and additem2 == item2 and '9999999999' == num_ and text_ == num
        assert not change.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_delsuccess1(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        change.del_data()
        after_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_addweeksuccess(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        SharedDataUtil.load_data()
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 2)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后品目
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 2)
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源
        resource = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")
        # 获取前资源
        item1 = change.get_find_element_xpath(
            '(//label[text()="前生产特征"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)
        # 获取后资源
        item2 = change.get_find_element_xpath(
            '(//label[text()="后生产特征"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )

        # 保存数据
        SharedDataUtil.save_data(
            {"resource": resource, "item1": item1, "item2": item2}
        )

        addresource = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        additem1 = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        additem2 = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        assert addresource == resource and additem1 == item1 and additem2 == item2
        assert not change.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_changespec_addrepe(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        code1 = SharedDataUtil.load_data().get("resource")
        code2 = SharedDataUtil.load_data().get("item1")
        code3 = SharedDataUtil.load_data().get("item2")
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        sleep(1)
        # 勾选框
        rows = driver.find_elements(By.XPATH, f"//table[.//tr[td[3]//span[text()='{code1}']]]//tr")
        for index, row in enumerate(rows, start=1):
            td3_text = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
            if f"{code1}" == td3_text:
                print(f"✅ 找到匹配行，行号为：{index}")

                # 3. 使用这个行号 idx 构造另一个 XPath
                target_xpath = f'(//table[.//tr[{index}]/td[2][contains(@class,"col--checkbox")]])[2]//tr[{index}]/td[2]/div/span'
                target_element = change.get_find_element_xpath(target_xpath)

                # 4. 操作目标元素
                target_element.click()
                break  # 如果只处理第一个匹配行，可以 break
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        sleep(1)
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    f'//div[@class="h-0px flex-grow1"]//table[@class="vxe-table--body" and .//tr[td[3] and .//span[text()="{code2}"]]]//tr')
        for index, row in enumerate(rows, start=1):
            td3_text = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
            if f"{code2}" == td3_text:
                print(f"✅ 找到匹配行，行号为：{index}")

                # 3. 使用这个行号 idx 构造另一个 XPath
                target_xpath = f'//div[@class="h-0px flex-grow1"]//table[@class="vxe-table--body"]//tr[{index}]/td[2]//div/span'
                # 点击前重新获取元素，防止 stale
                try:
                    target_element = change.get_find_element_xpath(target_xpath)
                    target_element.click()
                except StaleElementReferenceException:
                    print("⚠️ 元素过期，重新获取一次")
                    target_element = change.get_find_element_xpath(target_xpath)
                    target_element.click()

        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后生产特征
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        sleep(1)
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    f'//div[@class="h-0px flex-grow1"]//table[@class="vxe-table--body" and .//tr[td[3] and .//span[text()="{code2}"]]]//tr')
        for index, row in enumerate(rows, start=1):
            td3_text = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
            if f"{code3}" == td3_text:
                print(f"✅ 找到匹配行，行号为：{index}")

                # 3. 使用这个行号 idx 构造另一个 XPath
                target_xpath = f'//div[@class="h-0px flex-grow1"]//table[@class="vxe-table--body"]//tr[{index}]/td[2]//div/span'
                # 点击前重新获取元素，防止 stale
                try:
                    target_element = change.get_find_element_xpath(target_xpath)
                    target_element.click()
                except StaleElementReferenceException:
                    print("⚠️ 元素过期，重新获取一次")
                    target_element = change.get_find_element_xpath(target_xpath)
                    target_element.click()

        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        eles = driver.find_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        assert len(eles) == 1
        assert not change.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_delsuccess2(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        code1 = SharedDataUtil.load_data().get("resource")
        code2 = SharedDataUtil.load_data().get("item1")
        change.click_flagdata()
        # 定位第一行
        change.click_button(
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{code1}"] and td[3]//span[text()="{code2}"]]//td[2]'
        )
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        change.click_del_button()  # 点击删除
        change.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        change.wait_for_loading_to_disappear()
        ele = driver.find_elements(
            By.XPATH,
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{code1}"] and td[3]//span[text()="{code2}"]]//td[2]'
        )
        # 定位
        after_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data and
                len(ele) == 0
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_changespec_delcancel(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        # 定位第一行
        change.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        changedata1 = change.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        change.click_del_button()  # 点击删除
        # 点击取消
        change.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位第一行
        changedata = change.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        assert changedata1 == changedata, f"预期{changedata}"
        assert not change.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_changespec_refreshsuccess(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        # 资源切换筛选框输入123
        change.enter_texts(
            '//p[text()="资源"]/ancestor::div[2]//input', "123"
        )
        change.click_ref_button()
        changeRtext = change.get_find_element_xpath(
            '//p[text()="资源"]/ancestor::div[2]//input'
        ).text
        assert changeRtext == "", f"预期{changeRtext}"
        assert not change.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_addtt(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )

        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[2]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        assert not change.has_fail_message()

    @allure.story("修改资源切换资源成功")
    # @pytest.mark.run(order=1)
    def test_changespec_editcodesuccess(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        change.click_flagdata()
        sleep(1)
        # 定位第一行
        change.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        change.click_edi_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )

        # 勾选框
        change.click_button(
            '(//span[@class="vxe-checkbox--icon iconfont icon-fuxuankuangdaiding"])[2]'
        )
        change.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-checked-fill"])[2]'
        )
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[3]')

        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        adddata = change.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        assert adddata == resource
        assert not change.has_fail_message()

    @allure.story("修改切换优先度成功")
    # @pytest.mark.run(order=1)
    def test_changespec_editprioritizationsuccess(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        change.click_flagdata()
        sleep(1)
        # 定位第一行
        change.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        change.click_edi_button()

        # 优先度
        random_int = random.randint(1, 100)
        prioritizationinput = change.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritizationinput.send_keys(Keys.CONTROL, "a")
        prioritizationinput.send_keys(Keys.BACK_SPACE)
        sleep(1)
        change.enter_texts(
            '(//label[text()="优先度"])[1]/parent::div//input', f"{random_int}"
        )
        prioritization = change.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        ).get_attribute("value")

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        change.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        adddata = change.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[6]'
        ).text
        assert adddata == prioritization
        assert not change.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_changespec_selectcodesuccess(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        sleep(2)
        after = change.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]'
        ).text
        # 点击查询
        change.click_sel_button()
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
        # 点击资源切换代码
        change.click_button('//div[text()="资源" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        change.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        change.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        change.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            f"{after}",
        )
        sleep(1)

        # 点击确认
        change.click_select_button()
        # 定位第一行是否为开料
        changeRcode = change.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        )
        assert changeRcode.text == after
        assert not change.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_delsuccess3(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        change.del_data()
        after_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changespec_delsuccess4(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        change.del_data()
        after_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_changespec_addall(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        change.click_add_button()
        text_list = [
            '//label[text()="备注"]/following-sibling::div//input',
        ]
        adds.batch_modify_input(text_list, input_value)

        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[2])[2]/div/span'
        box_list = [
            '//label[text()="资源"]/following-sibling::div//i',
            '//label[text()="前生产特征"]/following-sibling::div//i',
            '//label[text()="后生产特征"]/following-sibling::div//i',
        ]
        adds.batch_modify_dialog_box(box_list, value_bos)
        resource_value = change.get_find_element_xpath('//label[text()="资源"]/following-sibling::div//input').get_attribute("value")

        code_value = '//span[text()="AdvanceAlongResourceWorkingTime"]'
        code_list = [
            '//label[text()="切换时间调整表达式"]/following-sibling::div//i',
        ]
        adds.batch_modify_code_box(code_list, code_value)

        input_num_value = '1'
        num_list = [
            '//label[text()="优先度"]/following-sibling::div//input',
            '//label[text()="切换时间(分钟)"]/following-sibling::div//input',
        ]
        adds.batch_modify_input(num_list, input_num_value)

        box_input_list = [xpath.replace("//i", "//input") for xpath in box_list]
        code_input_list = [xpath.replace("//i", "//input") for xpath in code_list]
        all_value = text_list + box_input_list + code_input_list + num_list
        len_num = len(all_value)
        before_all_value = adds.batch_acquisition_input(all_value)
        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        change.get_find_message()
        driver.refresh()
        change.wait_for_loading_to_disappear()
        num = adds.go_settings_page()
        change.wait_for_loading_to_disappear()
        change.click_flagdata()
        change.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{resource_value}"]]')
        sleep(1)
        change.click_edi_button()
        after_all_value = adds.batch_acquisition_input(all_value)
        username = change.get_find_element_xpath(
            '//label[text()="更新者"]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = change.get_find_element_xpath(
            '//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not change.has_fail_message()

    @allure.story("删除全部数据功")
    # @pytest.mark.run(order=1)
    def test_changespec_deleteall(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        change.click_flagdata()
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        change.wait_for_loading_to_disappear()
        change.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]')
        change.click_del_button()  # 点击删除
        change.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        change.wait_for_loading_to_disappear()
        # 定位
        after_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_changespec_delsuccesslayout(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        layout = "测试布局A"
        change.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not change.has_fail_message()

    @allure.story("生产特征2切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec2(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征22', '1测试生产特征2']
        after_name = '1修改生产特征22'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(2)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征3切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec3(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征33', '1测试生产特征3']
        after_name = '1修改生产特征33'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(3)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征4切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec4(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征44', '1测试生产特征4']
        after_name = '1修改生产特征44'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(4)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征5切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec5(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征55', '1测试生产特征5']
        after_name = '1修改生产特征55'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(5)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征6切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec6(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征66', '1测试生产特征6']
        after_name = '1修改生产特征66'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(6)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征7切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec7(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征77', '1测试生产特征7']
        after_name = '1修改生产特征77'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(7)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征8切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec8(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征88', '1测试生产特征8']
        after_name = '1修改生产特征88'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(8)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征9切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec9(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征99', '1测试生产特征9']
        after_name = '1修改生产特征99'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(9)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征10切换增删查改")
    # @pytest.mark.run(order=1)
    def test_changespec_changespec10(self, login_to_changespec):
        driver = login_to_changespec  # WebDriver 实例
        spec = ChangeR(driver)  # 用 driver 初始化 ChangeR
        list_name = ['1测试生产特征100', '1测试生产特征10']
        after_name = '1修改生产特征10'
        spec.click_button('//div[text()=" 生产特征1切换 "]')
        spec.click_button('//div[div[text()=" 生产特征1切换 "]]/span')
        spec.click_changespec_num(10)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_changespec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_changespec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_changespec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_changespec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_changespec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

