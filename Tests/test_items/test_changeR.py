import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException, TimeoutException
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


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_changeR():
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
        page.click_button('(//span[text()="资源切换"])[1]')  # 点击资源切换
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("资源切换表测试用例")
@pytest.mark.run(order=13)
class TestChangeRPage:
    @allure.story("添加资源切换信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changer_addfail(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        layout = "测试布局A"
        changeR.add_layout(layout)
        # 获取布局名称的文本元素
        name = changeR.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        changeR.click_add_button()
        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 资源
        inputresource_box = changeR.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )
        # 前资源
        inputitem_box1 = changeR.get_find_element_xpath(
            '(//label[text()="前资源"])[1]/parent::div//input'
        )
        # 后资源
        inputitem_box2 = changeR.get_find_element_xpath(
            '(//label[text()="后资源"])[1]/parent::div//input'
        )

        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        borderresource_color = inputresource_box.value_of_css_property("border-color")
        borderitem_color1 = inputitem_box1.value_of_css_property("border-color")
        borderitem_color2 = inputitem_box2.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert (
            borderresource_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderresource_color}"
        assert (
            borderitem_color1 == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderitem_color1}"
        assert (
            borderitem_color2 == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{borderitem_color2}"
        assert layout == name
        assert not changeR.has_fail_message()

    @allure.story("添加资源切换信息 填写资源不填写前资源和后资源 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changer_addresourcefail(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR

        changeR.click_add_button()
        # 点击资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 前资源
        inputitem_box1 = changeR.get_find_element_xpath(
            '(//label[text()="前资源"])[1]/parent::div//input'
        )
        # 后资源
        inputitem_box2 = changeR.get_find_element_xpath(
            '(//label[text()="后资源"])[1]/parent::div//input'
        )

        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        borderitem_color1 = inputitem_box1.value_of_css_property("border-color")
        borderitem_color2 = inputitem_box2.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert borderitem_color1 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert borderitem_color2 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert not changeR.has_fail_message()

    @allure.story("添加资源切换信息 填写前资源和后资源不填写资源 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changer_additemfail(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR

        changeR.click_add_button()
        # 资源
        input_box = changeR.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )

        # 点击前资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击确定
        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeR.has_fail_message()

    @allure.story("添加资源切换信息 填写资源，前资源和后资源 不填写切换时间 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changer_addtimefails(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR

        changeR.click_add_button()
        # 点击资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        changeR.wait_for_loading_to_disappear()
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除切换时间数字
        time = changeR.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div//input'
        )
        time.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = changeR.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeR.has_fail_message()

    @allure.story("添加资源切换信息 填写资源，前资源和后资源，填写切换时间，不填写优先度 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changer_addprioritizationfail(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR

        changeR.click_add_button()
        # 点击资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        sleep(1)
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        sleep(1)
        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除优先度
        prioritization = changeR.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritization.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = changeR.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeR.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_changer_addnum(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR

        changeR.click_add_button()  # 检查点击添加
        # 切换时间
        time = changeR.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        )
        # 删除资源量输入框
        time.send_keys(Keys.BACK_SPACE, "a")
        # 输入文本
        changeR.enter_texts(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]',
            "e1文字abc。？~1+1-=3",
        )
        sleep(1)
        # 获取表示顺序数字框
        changeRnum = changeR.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        ).get_attribute("value")
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        changeR.right_refresh('资源切换')
        assert changeRnum == "1113", f"预期{changeRnum}"
        assert not changeR.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_changeR_numverify(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
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
        sleep(1)
        # 获取勾选的资源
        resource = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")
        # 获取前目录
        item1 = change.get_find_element_xpath(
            '(//label[text()="前资源"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)
        # 获取后目录
        item2 = change.get_find_element_xpath(
            '(//label[text()="后资源"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)

        change.enter_texts('(//label[text()="优先度"])[1]/parent::div//input', num)
        change.enter_texts('(//label[text()="备注"])[1]/parent::div//input', num)

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        change.click_flagdata()

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
    def test_changeR_delsuccess1(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        change.click_flagdata()
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
    def test_changeR_addweeksuccess(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        SharedDataUtil.load_data()
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
        sleep(2)
        # 获取勾选的资源
        resource = change.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")
        # 获取前资源
        item1 = change.get_find_element_xpath(
            '(//label[text()="前资源"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)
        # 获取后资源
        item2 = change.get_find_element_xpath(
            '(//label[text()="后资源"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)

        change.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        change.wait_for_loading_to_disappear()
        change.click_flagdata()
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
    def test_changeR_addrepeat(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        change = ChangeR(driver)  # 用 driver 初始化 ChangeR
        code1 = SharedDataUtil.load_data().get("resource")
        code2 = SharedDataUtil.load_data().get("item1")
        code3 = SharedDataUtil.load_data().get("item2")
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
        rows = driver.find_elements(By.XPATH, f"//table[.//tr[td[2][contains(@class,'col--checkbox')]]]//tr")
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
        sleep(3)
        change.wait_for_loading_to_disappear()
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    f'(//div[@class="vxe-table--body-wrapper body--wrapper" and .//table[.//tr[td[3]//span[text()="{code2}"]]]])[2]//table//tr')
        for index, row in enumerate(rows, start=1):
            td3_text = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
            if f"{code2}" == td3_text:
                print(f"✅ 找到匹配行，行号为：{index}")

                # 3. 使用这个行号 idx 构造另一个 XPath
                target_xpath = f'(//table[.//tr[{index}]/td[2][contains(@class,"col--checkbox")]])[2]//tr[{index}]/td[.//span[@class="vxe-cell--checkbox"]]//div/span'
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
        sleep(3)
        change.wait_for_loading_to_disappear()
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    f'(//div[@class="vxe-table--body-wrapper body--wrapper" and .//table[.//tr[td[3]//span[text()="{code2}"]]]])[2]//table//tr')
        for index, row in enumerate(rows, start=1):
            td3_text = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
            if f"{code3}" == td3_text:
                print(f"✅ 找到匹配行，行号为：{index}")

                # 3. 使用这个行号 idx 构造另一个 XPath
                target_xpath = f'(//table[.//tr[{index}]/td[2][contains(@class,"col--checkbox")]])[2]//tr[{index}]/td[.//span[@class="vxe-cell--checkbox"]]//div/span'
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
        error_popup = change.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
        change.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        change.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！"
        assert not change.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_changer_delcancel(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        # 定位第一行
        changeR.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        changeRdata1 = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        changeR.click_del_button()  # 点击删除
        # 点击取消
        changeR.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位第一行
        changeRdata = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        assert changeRdata1 == changeRdata, f"预期{changeRdata}"
        assert not changeR.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changeR_delsuccess2(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
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
        sleep(1)
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

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_changer_refreshsuccess(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        # 资源切换筛选框输入123
        changeR.enter_texts(
            '//p[text()="资源"]/ancestor::div[2]//input', "123"
        )
        changeR.click_ref_button()
        changeRtext = changeR.get_find_element_xpath(
            '//p[text()="资源"]/ancestor::div[2]//input'
        ).text
        assert changeRtext == "", f"预期{changeRtext}"
        assert not changeR.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_changeR_addtt(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
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
        change.wait_for_loading_to_disappear()
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        change.wait_for_loading_to_disappear()
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
    def test_changer_editcodesuccess(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_flagdata()
        # 定位第一行
        changeR.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        changeR.click_edi_button()
        # 点击资源
        changeR.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )

        # 勾选框
        changeR.click_button(
            '(//span[@class="vxe-checkbox--icon iconfont icon-fuxuankuangdaiding"])[2]'
        )
        changeR.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-checked-fill"])[2]'
        )
        changeR.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[3]')

        changeR.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = changeR.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")

        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        changeR.wait_for_loading_to_disappear()
        changeR.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        changeR.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        adddata = changeR.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        assert adddata == resource
        assert not changeR.has_fail_message()

    @allure.story("修改资源切换优先度成功")
    # @pytest.mark.run(order=1)
    def test_changer_editprioritizationsuccess(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_flagdata()
        # 定位第一行
        changeR.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        changeR.click_edi_button()

        # 优先度
        random_int = random.randint(1, 100)
        prioritizationinput = changeR.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritizationinput.send_keys(Keys.CONTROL, "a")
        prioritizationinput.send_keys(Keys.BACK_SPACE)
        sleep(1)
        changeR.enter_texts(
            '(//label[text()="优先度"])[1]/parent::div//input', f"{random_int}"
        )
        prioritization = changeR.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        ).get_attribute("value")

        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        changeR.wait_for_loading_to_disappear()
        changeR.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        changeR.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        adddata = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[6]'
        ).text
        assert adddata == prioritization
        assert not changeR.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_changer_selectcodesuccess(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        ele = changeR.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr[2]/td[2]'
        ).text
        # 点击查询
        changeR.click_sel_button()
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
        # 点击资源切换代码
        changeR.click_button('//div[text()="资源" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        changeR.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        changeR.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        changeR.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            ele,
        )
        sleep(1)

        # 点击确认
        changeR.click_select_button()
        # 定位第一行
        changeRcode = changeR.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).get_attribute('innerText')
        assert changeRcode == ele
        assert not changeR.has_fail_message()

    @allure.story("删除数据")
    # @pytest.mark.run(order=1)
    def test_changeR_del1(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.right_refresh('资源切换')
        before_data = changeR.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        changeR.del_data()
        changeR.click_ref_button()
        changeR.wait_for_loading_to_disappear()
        changeR.del_data()
        # 定位
        after_data = changeR.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not changeR.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_changeR_addall(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        changeR.click_add_button()
        text_list = [
            '//label[text()="备注"]/following-sibling::div//input',
        ]
        adds.batch_modify_input(text_list, input_value)

        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[2])[2]/div/span'
        box_list = [
            '//label[text()="资源"]/following-sibling::div//i',
            '//label[text()="前资源"]/following-sibling::div//i',
            '//label[text()="后资源"]/following-sibling::div//i',
        ]
        adds.batch_modify_dialog_box(box_list, value_bos)
        resource_value = changeR.get_find_element_xpath('//label[text()="资源"]/following-sibling::div//input').get_attribute("value")

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
        changeR.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        changeR.get_find_message()
        driver.refresh()
        changeR.wait_for_loading_to_disappear()
        num = adds.go_settings_page()
        changeR.wait_for_loading_to_disappear()
        changeR.click_flagdata()
        changeR.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{resource_value}"]]')
        sleep(1)
        changeR.click_edi_button()
        after_all_value = adds.batch_acquisition_input(all_value)
        username = changeR.get_find_element_xpath('//label[text()="更新者"]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = changeR.get_find_element_xpath(
            '//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not changeR.has_fail_message()

    @allure.story("删除全部数据功")
    # @pytest.mark.run(order=1)
    def test_changeR_deleteall(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_flagdata()
        sleep(1)
        before_data = changeR.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        changeR.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]')
        changeR.click_del_button()
        changeR.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        changeR.wait_for_loading_to_disappear()
        # 定位
        after_data = changeR.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not changeR.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_changeR_select2(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = changeR.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            changeR.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            changeR.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//input')
        eles = changeR.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        changeR.right_refresh('资源切换')
        assert len(eles) == 0
        assert not changeR.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_changeR_select3(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        name = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        changeR.hover("包含")
        sleep(1)
        changeR.select_input(first_char)
        sleep(1)
        eles = changeR.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        changeR.right_refresh('资源切换')
        assert all(first_char in text for text in list_)
        assert not changeR.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_changeR_select4(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        name = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        changeR.hover("符合开头")
        sleep(1)
        changeR.select_input(first_char)
        sleep(1)
        eles = changeR.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        changeR.right_refresh('资源切换')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not changeR.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_changeR_select5(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        name = changeR.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        changeR.hover("符合结尾")
        sleep(1)
        changeR.select_input(last_char)
        sleep(1)
        eles = changeR.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        changeR.right_refresh('资源切换')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not changeR.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_changeR_clear(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        name = "3"
        sleep(1)
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        changeR.hover("包含")
        sleep(1)
        changeR.select_input(name)
        sleep(1)
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]/div[3]//i')
        changeR.hover("清除所有筛选条件")
        sleep(1)
        ele = changeR.get_find_element_xpath('//p[text()="资源"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        changeR.right_refresh('资源切换')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not changeR.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_changeR_ctrlIrepeat(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = changeR.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = changeR.get_error_message()
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not changeR.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_changeR_ctrlI(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        changeR.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        changeR.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = changeR.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        changeR.get_find_message()
        changeR.click_flagdata()
        ele2 = changeR.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not changeR.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_changeR_ctrlM(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        changeR.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        changeR.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = changeR.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        changeR.get_find_message()
        changeR.click_flagdata()
        ele2 = changeR.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        changeR.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        changeR.click_del_button()
        changeR.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = changeR.get_find_message()
        assert message == "删除成功！"
        assert not changeR.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_changeR_ctrlC(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        changeR.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = changeR.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        changeR.click_button('//p[text()="资源"]/ancestor::div[2]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = changeR.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        changeR.right_refresh('资源切换')
        assert all(before_data in ele for ele in eles)
        assert not changeR.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_changeR_shift(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]']
        changeR.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = changeR.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = changeR.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not changeR.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_changeR_ctrls(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]']
        changeR.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = changeR.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = changeR.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        changeR.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = changeR.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not changeR.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_changeR_delete(self, login_to_changeR):
        driver = login_to_changeR  # WebDriver 实例
        changeR = ChangeR(driver)  # 用 driver 初始化 ChangeR
        layout = "测试布局A"
        changeR.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not changeR.has_fail_message()
