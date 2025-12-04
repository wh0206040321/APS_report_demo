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
from Pages.itemsPage.changeI_page import ChangeI
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_changeI():
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
        page.click_button('(//span[text()="物品切换"])[1]')  # 点击物品切换
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物品切换表测试用例")
@pytest.mark.run(order=12)
class TestChangeIPage:

    @allure.story("添加物品切换信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changeI_addfail(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        layout = "测试布局A"
        changeI.add_layout(layout)
        # 获取布局名称的文本元素
        name = changeI.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        changeI.click_add_button()
        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 资源
        inputresource_box = changeI.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )
        # 前品目
        inputitem_box1 = changeI.get_find_element_xpath(
            '(//label[text()="前品目"])[1]/parent::div//input'
        )
        # 后品目
        inputitem_box2 = changeI.get_find_element_xpath(
            '(//label[text()="后品目"])[1]/parent::div//input'
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
        assert layout == name
        assert not changeI.has_fail_message()

    @allure.story("添加物品切换信息 填写资源不填写前品目和后品目 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changeI_addresourcefail(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI

        changeI.click_add_button()
        # 点击资源
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 前品目
        inputitem_box1 = changeI.get_find_element_xpath(
            '(//label[text()="前品目"])[1]/parent::div//input'
        )
        # 后品目
        inputitem_box2 = changeI.get_find_element_xpath(
            '(//label[text()="后品目"])[1]/parent::div//input'
        )

        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        borderitem_color1 = inputitem_box1.value_of_css_property("border-color")
        borderitem_color2 = inputitem_box2.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert borderitem_color1 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert borderitem_color2 == expected_color, f"预期边框颜色为{borderitem_color1}"
        assert not changeI.has_fail_message()

    @allure.story("添加物品切换信息 填写前品目和后品目不填写资源 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changeI_additemfail(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI

        changeI.click_add_button()
        # 资源
        input_box = changeI.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        )

        # 点击前品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击确定
        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeI.has_fail_message()

    @allure.story("添加物品切换信息 填写资源，前品目和后品目 不填写切换时间 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changeI_addtimefails(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI

        changeI.click_add_button()
        # 点击资源
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除切换时间数字
        time = changeI.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div//input'
        )
        time.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = changeI.get_find_element_xpath(
            '(//label[text()="切换时间(分钟)"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeI.has_fail_message()

    @allure.story("添加物品切换信息 填写资源，前品目和后品目 不填写切换时间 不允许提交")
    # @pytest.mark.run(order=1)
    def test_changeI_addprioritizationfail(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI

        changeI.click_add_button()
        # 点击资源
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        # 勾选框
        random_int = random.randint(1, 6)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        # 勾选框
        random_int = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击后品目
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        # 勾选框
        random_int1 = random.randint(1, 4)
        sleep(1)
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[{random_int1}]')
        sleep(1)
        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        sleep(1)
        # 清除切换时间数字
        prioritization = changeI.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritization.send_keys(Keys.BACK_SPACE, "a")
        sleep(1)

        # 点击确定
        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        sleep(1)
        time = changeI.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div/div/div'
        )
        border_color = time.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert border_color == expected_color, f"预期边框颜色为{border_color}"
        assert not changeI.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_changeI_addnum(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI

        changeI.click_add_button()  # 检查点击添加
        # 切换时间
        time = changeI.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        )
        # 删除资源量输入框
        time.send_keys(Keys.BACK_SPACE, "a")
        # 输入文本
        changeI.enter_texts(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]',
            "e1文字abc。？~1+1-=3",
        )
        sleep(1)
        # 获取表示顺序数字框
        changeInum = changeI.get_find_element_xpath(
            '//label[text()="切换时间(分钟)"]/ancestor::div[1]//input[1]'
        ).get_attribute("value")
        assert changeInum == "1113", f"预期{changeInum}"
        assert not changeI.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_changeI_numverify(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 ChangeR
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        change.wait_for_loading_to_disappear()
        # 勾选框
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
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

        # 点击后品目
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
            '(//label[text()="前品目"])[1]/parent::div//input'
        ).get_attribute("value")
        # 获取后目录
        item2 = change.get_find_element_xpath(
            '(//label[text()="后品目"])[1]/parent::div//input'
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
    def test_changeI_delsuccess1(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 changeI
        change.wait_for_loading_to_disappear()
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
    def test_changeI_addweeksuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 ChangeR
        SharedDataUtil.load_data()
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        change.wait_for_loading_to_disappear()
        # 勾选框
        change.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[1]')
        change.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )

        # 点击前品目
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

        # 点击后品目
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
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
            '(//label[text()="前品目"])[1]/parent::div//input'
        ).get_attribute("value")
        sleep(1)
        # 获取后目录
        item2 = change.get_find_element_xpath(
            '(//label[text()="后品目"])[1]/parent::div//input'
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
    def test_changeI_addrepe(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 changeI
        code1 = SharedDataUtil.load_data().get("resource")
        code2 = SharedDataUtil.load_data().get("item1")
        code3 = SharedDataUtil.load_data().get("item2")
        change.click_add_button()
        # 点击资源
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )
        change.wait_for_loading_to_disappear()
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

        # 点击前目录
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
        )
        change.wait_for_loading_to_disappear()
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    '(//div[@class="vxe-table--body-wrapper body--wrapper"])[last()]//table//tr')
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
        # 点击后目录
        change.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[3]'
        )
        change.wait_for_loading_to_disappear()
        # 勾选框
        rows = driver.find_elements(By.XPATH,
                                    '(//div[@class="vxe-table--body-wrapper body--wrapper"])[last()]//table//tr')
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
        eles = driver.find_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        assert len(eles) == 1
        assert not change.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_changeI_delsuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 changeI
        code1 = SharedDataUtil.load_data().get("resource")
        code2 = SharedDataUtil.load_data().get("item1")
        change.click_flagdata()
        before_data = change.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        # 定位第一行
        change.click_button(
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{code1}"] and td[3]//span[text()="{code2}"]]//td[2]'
        )
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
                len(ele) == 0 and
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not change.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_changeI_delcancel(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        # 定位第一行
        changeI.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        changeIdata1 = changeI.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        changeI.click_del_button()  # 点击删除
        # 点击取消
        changeI.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位第一行
        changeIdata = changeI.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        ).text
        assert changeIdata1 == changeIdata, f"预期{changeIdata}"
        assert not changeI.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_changeI_refreshsuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        # 物品切换筛选框输入123
        changeI.enter_texts(
            '//p[text()="资源"]/ancestor::div[2]//input', "123"
        )
        changeI.click_ref_button()
        changeItext = changeI.get_find_element_xpath(
            '//p[text()="资源"]/ancestor::div[2]//input'
        ).text
        assert changeItext == "", f"预期{changeItext}"
        assert not changeI.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_changeI_addtt(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        change = ChangeI(driver)  # 用 driver 初始化 ChangeR
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

        # 点击前品目
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

        # 点击后品目
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

        # 点击前品目
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

        # 点击后品目
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

    @allure.story("修改物品切换资源成功")
    # @pytest.mark.run(order=1)
    def test_changeI_editcodesuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        # 定位第一行
        changeI.click_flagdata()
        changeI.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        changeI.click_edi_button()
        # 点击资源
        changeI.click_button(
            '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
        )

        # 勾选框
        changeI.click_button(
            '(//span[@class="vxe-checkbox--icon iconfont icon-fuxuankuangdaiding"])[2]'
        )
        changeI.wait_for_loading_to_disappear()
        changeI.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-checked-fill"])[2]'
        )
        changeI.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]/div/span/span)[3]')

        changeI.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = changeI.get_find_element_xpath(
            '(//label[text()="资源"])[1]/parent::div//input'
        ).get_attribute("value")

        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        changeI.wait_for_loading_to_disappear()
        changeI.click_flagdata()
        adddata = changeI.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        assert adddata == resource
        assert not changeI.has_fail_message()

    @allure.story("修改物品切换优先度成功")
    # @pytest.mark.run(order=1)
    def test_changeI_editprioritizationsuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        # 定位第一行
        changeI.click_flagdata()
        changeI.click_button(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[2]'
        )
        # 点击修改按钮
        changeI.click_edi_button()

        # 优先度
        random_int = random.randint(1, 100)
        prioritizationinput = changeI.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        )
        prioritizationinput.send_keys(Keys.CONTROL, "a")
        prioritizationinput.send_keys(Keys.BACK_SPACE)
        sleep(1)
        changeI.enter_texts(
            '(//label[text()="优先度"])[1]/parent::div//input', f"{random_int}"
        )
        prioritization = changeI.get_find_element_xpath(
            '(//label[text()="优先度"])[1]/parent::div//input'
        ).get_attribute("value")

        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        changeI.wait_for_loading_to_disappear()
        changeI.click_flagdata()
        adddata = changeI.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[1]//td[6]'
        ).text
        assert adddata == prioritization
        assert not changeI.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_changeI_selectcodesuccess(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        sleep(3)
        ele = changeI.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).text
        # 点击查询
        changeI.click_sel_button()
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
        # 点击物品切换代码
        changeI.click_button('//div[text()="资源" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        changeI.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        changeI.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        changeI.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            ele,
        )
        sleep(1)

        # 点击确认
        changeI.click_select_button()
        # 定位第一行
        changeIcode = changeI.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        assert changeIcode == ele
        assert not changeI.has_fail_message()

    @allure.story("删除数据")
    # @pytest.mark.run(order=1)
    def test_changeI_del1(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        sleep(1)
        before_data = changeI.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        changeI.del_data()
        changeI.click_ref_button()
        changeI.wait_for_loading_to_disappear()
        changeI.del_data()
        # 定位
        after_data = changeI.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not changeI.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_changeI_addall(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        changeI.click_add_button()
        text_list = [
            '//label[text()="备注"]/following-sibling::div//input',
        ]
        adds.batch_modify_input(text_list, input_value)

        value_bos = '(//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[2])[2]/div/span'
        box_list = [
            '//label[text()="资源"]/following-sibling::div//i',
            '//label[text()="前品目"]/following-sibling::div//i',
            '//label[text()="后品目"]/following-sibling::div//i',
        ]
        adds.batch_modify_dialog_box(box_list, value_bos)
        resource_value = changeI.get_find_element_xpath(
            '//label[text()="资源"]/following-sibling::div//input').get_attribute("value")

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
        changeI.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        changeI.get_find_message()
        driver.refresh()
        changeI.wait_for_loading_to_disappear()
        num = adds.go_settings_page()
        changeI.wait_for_loading_to_disappear()
        changeI.click_flagdata()
        changeI.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{resource_value}"]]')
        sleep(1)
        changeI.click_edi_button()
        after_all_value = adds.batch_acquisition_input(all_value)
        username = changeI.get_find_element_xpath(
            '//label[text()="更新者"]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = changeI.get_find_element_xpath(
            '//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not changeI.has_fail_message()

    @allure.story("删除全部数据功")
    # @pytest.mark.run(order=1)
    def test_changeI_deleteall(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        changeI.click_flagdata()
        before_data = changeI.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        changeI.del_data()
        # 定位
        after_data = changeI.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                before_data != after_data
        ), f"删除后的数据{after_data}，删除前的数据{before_data}"
        assert not changeI.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_changeI_delete(self, login_to_changeI):
        driver = login_to_changeI  # WebDriver 实例
        changeI = ChangeI(driver)  # 用 driver 初始化 ChangeI
        layout = "测试布局A"
        changeI.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not changeI.has_fail_message()
