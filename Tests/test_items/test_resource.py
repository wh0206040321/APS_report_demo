import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.resource_page import ResourcePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_resource():
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
        page.click_button('(//span[text()="资源"])[1]')  # 点击资源
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("资源表测试用例")
@pytest.mark.run(order=6)
class TestResourcePage:
    @allure.story("添加资源信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_resource_addfail(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        layout = "测试布局A"
        resource.add_layout(layout)
        # 获取布局名称的文本元素
        name = resource.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        resource.click_add_button()
        # 资源代码xpath
        input_box = resource.get_find_element_xpath(
            '(//label[text()="资源代码"])[1]/parent::div//input'
        )
        # 资源名称xpath
        inputname_box = resource.get_find_element_xpath(
            '(//label[text()="资源名称"])[1]/parent::div//input'
        )
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert name == layout
        assert not resource.has_fail_message()

    @allure.story("添加资源信息，只填写资源代码，不填写资源名称，不允许提交")
    # @pytest.mark.run(order=2)
    def test_resource_addcodefail(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        resource.click_add_button()
        resource.enter_texts(
            '(//label[text()="资源代码"])[1]/parent::div//input', "text1231"
        )
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = resource.get_find_element_xpath(
            '(//label[text()="资源名称"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not resource.has_fail_message()

    @allure.story("添加资源信息，只填写资源名称，不填写资源代码，不允许提交")
    # @pytest.mark.run(order=3)
    def test_resource_addnamefail(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        resource.click_add_button()
        resource.enter_texts(
            '(//label[text()="资源名称"])[1]/parent::div//input', "text1231"
        )
        sleep(1)
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = resource.get_find_element_xpath(
            '(//label[text()="资源代码"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not resource.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_resource_addnum(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        resource.click_add_button()  # 检查点击添加
        # 数值特征数字框输入文字字母符号数字
        resource.enter_texts(
            '(//label[text()="数值特征1MAX"])[1]/parent::div//input',
            "e1.文字abc。？~1_2+3",
        )
        sleep(1)
        # 获取数值特征数字框
        resourcenum = resource.get_find_element_xpath(
            '(//label[text()="数值特征1MAX"])[1]/parent::div//input'
        ).get_attribute("value")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert resourcenum == "1123", f"预期{resourcenum}"
        assert not resource.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_resource_addsel(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        resource.click_add_button()  # 检查点击添加
        # 资源量制约下拉框
        resource.click_button(
            '(//label[text()="资源量制约"])[1]/parent::div//input[@class="ivu-select-input"]'
        )
        # 自动补充标志选择是(是库存+1对1制造)
        resource.click_button('//li[text()="按资源量分派"]')
        # 获取资源量制约下拉框
        resourcesel = resource.get_find_element_xpath(
            '(//label[text()="资源量制约"])[1]/parent::div//input[@class="ivu-select-input"]'
        ).get_attribute("value")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert resourcesel == "按资源量分派", f"预期{resourcesel}"
        assert not resource.has_fail_message()

    @allure.story("代码设计器选择成功，并且没有乱码")
    # @pytest.mark.run(order=1)
    def test_resource_addcodebox(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        resource.click_add_button()  # 检查点击添加
        # 点击代码设计器
        resource.click_button('(//label[text()="分割条件式"])[1]/parent::div//i')
        # 点击标准登录
        resource.click_button('(//div[text()=" 标准登录 "])[1]')
        # 首先，定位到你想要双击的元素
        element_to_double_click = driver.find_element(
            By.XPATH, '(//span[text()="分割数量在10以上，且中断时间超过1小时"])[1]'
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        # 点击确认
        resource.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        # 获取分割条件式代码设计器文本框
        sleep(1)
        resourcecode = resource.get_find_element_xpath(
            '(//label[text()="分割条件式"])[1]/parent::div//input'
        ).get_attribute("value")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert (
            resourcecode
            == "ME.AssignedQty>=10&&1h<ME.SuspendEndTime[0]-ME.SuspendStartTime[0]"
        ), f"预期{resourcecode}"
        assert not resource.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_resource_addsuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "111"
        resource.add_test_resource(name)
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        adddata = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        ).get_attribute("innerText")
        assert adddata == name, f"预期数据是111，实际得到{adddata}"
        assert not resource.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_resource_addrepeat(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        name = "111"
        resource.add_test_resource(name)
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = resource.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute("innerText")
        resource.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not resource.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_resource_delcancel(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "111"
        # 定位内容为‘111’的行
        resource.click_button('(//span[text()="111"])[1]/ancestor::tr[1]/td[2]')
        resource.click_del_button()  # 点击删除
        resource.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        resourcedata = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        ).get_attribute("innerText")
        assert resourcedata == name, f"预期{resourcedata}"
        assert not resource.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_resource_textverify(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        resource.add_test_resource(name)
        resource.enter_texts('(//label[text()="显示顺序"])[1]/parent::div//input', name)
        # 点击确定
        resource.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        adddata = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        ).get_attribute("innerText")
        num_ = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[9]'
        ).get_attribute("innerText")
        assert adddata == name and num_ == '9999999999', f"预期数据是{name}，实际得到{adddata}"
        assert not resource.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_resource_addsuccess1(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1测试A"
        resource.add_test_resource(name)
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        adddata = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr[1]/td[2]'
        ).get_attribute("innerText")
        assert adddata == name, f"预期数据是1测试A，实际得到{adddata}"
        assert not resource.has_fail_message()

    @allure.story("修改资源代码重复")
    # @pytest.mark.run(order=1)
    def test_resource_editrepeat(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1测试A"
        # 选中1测试A代码
        resource.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        resource.click_edi_button()
        # 资源代码输入111
        resource.enter_texts(
            '(//label[text()="资源代码"])[1]/parent::div//input', "111"
        )
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = resource.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute("innerText")
        resource.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not resource.has_fail_message()

    @allure.story("修改资源代码成功")
    # @pytest.mark.run(order=1)
    def test_resource_editcodesuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1测试A"
        resource.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        resource.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 资源代码输入
        resource.enter_texts(
            '(//label[text()="资源代码"])[1]/parent::div//input', f"{text}"
        )
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        # 定位表格内容
        resourcedata = resource.get_find_element_xpath(
            f'(//span[contains(text(),"{name}")])[1]'
        ).get_attribute("innerText")
        assert resourcedata == text, f"预期{resourcedata}"
        assert not resource.has_fail_message()

    @allure.story("把修改后的资源代码改回来")
    # @pytest.mark.run(order=1)
    def test_resource_editcodesuccess2(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1测试A"
        # 选中资源代码
        resource.click_button(f'(//span[contains(text(),"{name}")])[1]')
        # 点击修改按钮
        resource.click_edi_button()
        # 资源代码输入
        resource.enter_texts(
            '(//label[text()="资源代码"])[1]/parent::div//input', name
        )
        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        # 定位表格内容
        resourcedata = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]'
        ).get_attribute("innerText")
        assert resourcedata == name, f"预期{resourcedata}"
        assert not resource.has_fail_message()

    @allure.story("修改资源名称，资源量制约")
    # @pytest.mark.run(order=1)
    def test_resource_editnamesuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1测试A"
        # 选中资源代码
        resource.click_button(f'(//span[text()="{name}"])[1]')
        # 点击修改按钮
        resource.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = "包装机" + f"{random_int}"
        # 输入修改的资源名称
        resource.enter_texts(
            '(//label[text()="资源名称"])[1]/parent::div//input', f"{text}"
        )
        # 获取修改好的值
        editname = resource.get_find_element_xpath(
            '(//label[text()="资源名称"])[1]/parent::div//input'
        ).get_attribute("value")

        # 资源量制约下拉框
        resource.click_button(
            '(//label[text()="资源量制约"])[1]/parent::div//input[@class="ivu-select-input"]'
        )
        # 资源量制约选择(不制约)
        resource.click_button('//li[text()="不制约"]')
        # 获取资源量制约下拉框的值
        resourcesel = resource.get_find_element_xpath(
            '(//label[text()="资源量制约"])[1]/parent::div//input[@class="ivu-select-input"]'
        ).get_attribute("value")

        # 点击确定
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        resource.wait_for_loading_to_disappear()
        # 定位表格内容
        resourcename = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr/td[3]/div'
        ).get_attribute("innerText")
        resourceautoGenerateFlag = resource.get_find_element_xpath(
            f'(//span[text()="{name}"])[1]/ancestor::tr/td[7]/div'
        ).get_attribute("innerText")
        assert resourcename == editname and resourceautoGenerateFlag == resourcesel
        assert not resource.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_resource_refreshsuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        # 资源代码筛选框输入123
        resource.enter_texts(
            '//p[text()="资源代码"]/ancestor::div[2]//input', "123"
        )
        resource.click_ref_button()
        resourcetext = resource.get_find_element_xpath(
            '//p[text()="资源代码"]/ancestor::div[2]//input'
        ).text
        assert resourcetext == "", f"预期{resourcetext}"
        assert not resource.has_fail_message()

    @allure.story("查询资源代码成功")
    # @pytest.mark.run(order=1)
    def test_resource_selectcodesuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        # 点击查询
        resource.click_sel_button()
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
        # 点击资源代码
        resource.click_button('//div[text()="资源代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        resource.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "111",
        )
        sleep(1)

        # 点击确认
        resource.click_select_button()
        # 定位第一行是否为111
        resourcecode = resource.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).get_attribute("innerText")
        # 定位第二行没有数据
        resourcecode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        resource.right_refresh('资源')
        assert resourcecode == "111" and len(resourcecode2) == 0
        assert not resource.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_resource_selectnodatasuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        # 点击查询
        resource.click_sel_button()
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
        # 点击资源代码
        resource.click_button('//div[text()="资源代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        resource.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        resource.click_select_button()
        resourcecode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        resource.right_refresh('资源')
        assert len(resourcecode) == 0
        assert not resource.has_fail_message()

    @allure.story("查询资源名字成功")
    # @pytest.mark.run(order=1)
    def test_resource_selectnamesuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "111"
        # 点击查询
        resource.click_sel_button()
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
        # 点击资源名称
        resource.click_button('//div[text()="资源名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        resource.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        resource.click_select_button()
        eles = resource.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        resource.right_refresh('资源')
        assert len(eles) > 0
        assert all(name == ele for ele in eles)
        assert not resource.has_fail_message()

    @allure.story("显示顺序大于>5")
    # @pytest.mark.run(order=1)
    def test_resource_selectsuccess1(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        # 点击查询
        resource.click_sel_button()
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
        # 点击数值特征1MAX
        resource.click_button(
            '//div[text()="显示顺序" and contains(@optid,"opt_")]'
        )
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        resource.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "5",
        )
        sleep(1)

        # 点击确认
        resource.click_select_button()
        eles = resource.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[9]')
        resource.right_refresh('资源')
        assert len(eles) > 0
        assert all(int(ele) > 5 for ele in eles)
        assert not resource.has_fail_message()

    @allure.story("查询资源组包含C并且显示顺序>5")
    # @pytest.mark.run(order=1)
    def test_resource_selectsuccess2(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage

        # 点击查询
        resource.click_sel_button()
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
        # 点击资源名称
        resource.click_button('//div[text()="资源组" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        resource.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        resource.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "C",
        )

        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        resource.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
        )
        # 双击命令
        sleep(1)
        actions.double_click(double_click).perform()
        # 定义and元素的XPath
        and_xpath = '//div[text()="and" and contains(@optid,"opt_")]'

        try:
            # 首先尝试直接查找并点击and元素
            and_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, and_xpath))
            )
            and_element.click()
        except:
            # 如果直接查找失败，进入循环双击操作
            max_attempts = 5
            attempt = 0
            and_found = False

            while attempt < max_attempts and not and_found:
                try:
                    # 执行双击操作
                    actions.double_click(double_click).perform()
                    sleep(1)

                    # 再次尝试查找and元素
                    and_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, and_xpath))
                    )
                    and_element.click()
                    and_found = True
                except:
                    attempt += 1
                    sleep(1)

            if not and_found:
                raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'and'元素")

        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        resource.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击资源优先度
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        resource.click_button(
            '//div[text()="显示顺序" and contains(@optid,"opt_")]'
        )
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        resource.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            "5",
        )
        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        resource.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        resource.click_select_button()
        ele1 = resource.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[9]')
        ele2 = resource.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[4]')
        resource.right_refresh('资源')
        assert len(ele1) > 0 and len(ele2) > 0
        assert all(int(ele) > 5 for ele in ele1) and all(
            "C" in ele for ele in ele2
        )
        assert not resource.has_fail_message()

    @allure.story("查询资源名称包含1或显示顺序>5")
    # @pytest.mark.run(order=1)
    def test_resource_selectsuccess3(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        name = "1"
        num = 5
        # 点击查询
        resource.click_sel_button()
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
        # 点击名称
        resource.click_button('//div[text()="资源名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        resource.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        resource.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        resource.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)
        double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
        )
        # 双击命令
        sleep(1)
        actions.double_click(double_click).perform()
        # 定义or元素的XPath
        or_xpath = '//div[text()="or" and contains(@optid,"opt_")]'

        try:
            # 首先尝试直接查找并点击or元素
            and_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, or_xpath))
            )
            and_element.click()
        except:
            # 如果直接查找失败，进入循环双击操作
            max_attempts = 5
            attempt = 0
            or_found = False

            while attempt < max_attempts and not or_found:
                try:
                    # 执行双击操作
                    actions.double_click(double_click).perform()
                    sleep(1)

                    # 再次尝试查找or元素
                    or_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, or_xpath))
                    )
                    or_element.click()
                    or_found = True
                except:
                    attempt += 1
                    sleep(1)

            if not or_found:
                raise Exception(f"在{max_attempts}次尝试后仍未找到并点击到'or'元素")

        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        resource.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击显示顺序
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        resource.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        resource.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值5
        resource.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        resource.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        resource.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        resource.click_select_button()
        # 获取目标表格第2个 vxe 表格中的所有数据行
        xpath_rows = '(//table[contains(@class, "vxe-table--body")])[2]//tr[contains(@class,"vxe-body--row")]'

        # 先拿到总行数
        base_rows = driver.find_elements(By.XPATH, xpath_rows)
        total = len(base_rows)

        valid_count = 0
        for idx in range(total):
            try:
                # 每次都按索引重新定位这一行
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td9_raw = tds[8].text.strip()
                td9_raw = int(td9_raw) if td9_raw else 0

                assert name in td3 or td9_raw > num, f"第 {idx + 1} 行不符合：td3={td3}, td8={td9_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td9_raw = tds[8].text.strip()
                td9_raw = int(td9_raw) if td9_raw else 0
                assert name in td3 or td9_raw > num, f"第 {idx + 1} 行不符合：td3={td3}, td5={td9_raw}"
                valid_count += 1
        resource.right_refresh('资源')
        assert not resource.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_resource_addall(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        resource.click_add_button()
        custom_xpath_list = [
            f'//label[text()="自定义字符{i}"]/following-sibling::div//input'
            for i in range(1, 21)
        ]
        text_list = [
            '//label[text()="资源代码"]/following-sibling::div//input',
            '//label[text()="资源名称"]/following-sibling::div//input',
            '//label[text()="制造中断时间MAX"]/following-sibling::div//input',
            '//label[text()="前设置中断时间MAX"]/following-sibling::div//input',
            '//label[text()="后设置中断时间MAX"]/following-sibling::div//input',
            '//label[text()="前设置和制造之间中断时间MAX"]/following-sibling::div//input',
            '//label[text()="后设置和制造之间中断时间MAX"]/following-sibling::div//input',
            '//label[text()="分割工作中断时间MAX"]/following-sibling::div//input',
            '//label[text()="自动确定期间结束时间"]/following-sibling::div//input',
            '//label[text()="备注"]/following-sibling::div//input',
            '//label[text()="制造任务可开工日期"]/following-sibling::div//input',
            '//label[text()="制造任务可开工时间段"]/following-sibling::div//input',
            '//label[text()="区间控制-共同考虑约束的资源"]/following-sibling::div//input',
            '//label[text()="事件控制-计数方法"]/following-sibling::div//input',
            '//label[text()="事件控制-计算起始时间"]/following-sibling::div//input',
        ]
        text_list.extend(custom_xpath_list)
        adds.batch_modify_input(text_list, input_value)

        value_bos = '//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3]'
        spe_xpath_list = [
            f'//label[text()="生产特征{i}"]/following-sibling::div//i'
            for i in range(1, 11)
        ]
        box_list = [
            '//label[text()="资源组"]/following-sibling::div//i',
            '//label[text()="后资源"]/following-sibling::div//i',
        ]
        box_list.extend(spe_xpath_list)
        adds.batch_modify_dialog_box(box_list, value_bos)

        code_value = '//span[text()="AdvanceAlongResourceWorkingTime"]'
        code_list = [
            '//label[text()="分割条件式"]/following-sibling::div//i',
            '//label[text()="分派有效条件表达式"]/following-sibling::div//i',
            '//label[text()="炉有效条件表达式"]/following-sibling::div//i',
            '//label[text()="区间控制-例外的工作"]/following-sibling::div//i',
            '//label[text()="区间控制-关联相同内容"]/following-sibling::div//i',
            '//label[text()="区间控制-关联相同内容计划量上限"]/following-sibling::div//i',
            '//label[text()="区间控制-关联相同内容+资源计划量上限"]/following-sibling::div//i',
        ]
        adds.batch_modify_code_box(code_list, code_value)

        select_list = [
            {"select": '//label[text()="资源区分"]/following-sibling::div//i', "value": '//li[text()="复合资源"]'},
            {"select": '//label[text()="资源种类"]/following-sibling::div//i', "value": '//li[text()="副资源"]'},
            {"select": '//label[text()="资源量制约"]/following-sibling::div//i',
             "value": '//li[text()="按资源量分派"]'},
            {"select": '//label[text()="分派资源量标志"]/following-sibling::div//i', "value": '//li[text()="与制造数量成比例"]'},
            {"select": '//label[text()="显示颜色"]/following-sibling::div//i',
             "value": '//span[text()="RGB(128,128,255)"]'},
            {"select": '//label[text()="瓶颈资源"]/following-sibling::div//i', "value": '//li[text()="瓶颈资源"]'},
            {"select": '//label[text()="严格遵守后资源制约"]/following-sibling::div//i',
             "value": '//label[text()="严格遵守后资源制约"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="是"]'},
            {"select": '//label[text()="资源锁定禁止相同资源"]/following-sibling::div//i',
             "value": '//label[text()="资源锁定禁止相同资源"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="否"]'},
            {"select": '//label[text()="实绩输入标志"]/following-sibling::div//i', "value": '//li[text()="可选项"]'},
            {"select": '//label[text()="制造任务贴近下一个任务"]/following-sibling::div//i',
             "value": '//label[text()="制造任务贴近下一个任务"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="否"]'},
            {"select": '//label[text()="跨其它工作分派"]/following-sibling::div//i',
             "value": '//label[text()="跨其它工作分派"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="是"]'},
            {"select": '//label[text()="保证工作的最后分派顺序"]/following-sibling::div//i',
             "value": '//label[text()="保证工作的最后分派顺序"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="是"]'},
            {"select": '//label[text()="区间控制-制约类型"]/following-sibling::div//i', "value": '//li[text()="类型个数"]'},
            {"select": '//label[text()="区间控制-制约区间"]/following-sibling::div//i',
             "value": '//label[text()="区间控制-制约区间"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="班次"]'},
        ]
        adds.batch_modify_select_input(select_list)

        input_num_value = '1'
        num_xpath_list1 = [
            f'//label[text()="数值特征{i}{suffix}"]/following-sibling::div//input'
            for i in range(1, 6)
            for suffix in ["MAX", "MIN"]
        ]
        num_xpath_list2 = [
            f'//label[text()="自定义数字{i}"]/following-sibling::div//input'
            for i in range(1, 21)
        ]
        num_xpath_list3 = [
            f'//label[text()="技能{i}"]/following-sibling::div//input'
            for i in range(1, 5)
        ]

        num_list = [
            '//label[text()="显示顺序"]/following-sibling::div//input',
            '//label[text()="制造效率"]/following-sibling::div//input',
            '//label[text()="前设置时间效率"]/following-sibling::div//input',
            '//label[text()="资源制造批量MIN"]/following-sibling::div//input',
            '//label[text()="资源制造批量MAX"]/following-sibling::div//input',
            '//label[text()="资源制造单位"]/following-sibling::div//input',
            '//label[text()="区间控制-资源制约最大量"]/following-sibling::div//input',
            '//label[text()="区间控制-关联资源制约最大量"]/following-sibling::div//input',
            '//label[text()="事件控制-计数初值"]/following-sibling::div//input',
            '//label[text()="事件控制-计数循环累计值"]/following-sibling::div//input',
            '//label[text()="事件控制-控制阈值"]/following-sibling::div//input',
            '//label[text()="事件控制-资源产生保养时长"]/following-sibling::div//input',
            '//label[text()="事件控制-计数累计值"]/following-sibling::div//input',
            '//label[text()="事件控制-资源生命周期"]/following-sibling::div//input',
            '//label[text()="按资源量分派的任务"]/following-sibling::div//input',
        ]
        num_list.extend(num_xpath_list1 + num_xpath_list2 + num_xpath_list3)
        adds.batch_modify_input(num_list, input_num_value)

        time_xpath_list = [
            f'//label[text()="自定义日期{i}"]/following-sibling::div//input'
            for i in range(1, 11)
        ]
        adds.batch_modify_time_input(time_xpath_list)

        box_input_list = [xpath.replace("//i", "//input") for xpath in box_list]
        code_input_list = [xpath.replace("//i", "//input") for xpath in code_list]
        select_input_list = [item["select"].replace("//i", "//input") for item in select_list]
        checked = resource.get_find_element_xpath('//label[text()="无效资源"]/following-sibling::div//label/span')
        if checked.get_attribute("class") == "ivu-checkbox":
            checked.click()
        before_checked = resource.get_find_element_xpath('//label[text()="无效资源"]/following-sibling::div//label/span').get_attribute("class")
        all_value = text_list + box_input_list + code_input_list + select_input_list + num_list + time_xpath_list
        len_num = len(all_value)
        before_all_value = adds.batch_acquisition_input(all_value)
        resource.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        resource.get_find_message()
        driver.refresh()
        sleep(2)
        resource.wait_for_loading_to_disappear()
        num = adds.go_settings_page()
        resource.wait_for_loading_to_disappear()
        resource.enter_texts(
            '//p[text()="资源代码"]/ancestor::div[2]//input', input_value
        )
        sleep(1)
        resource.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{input_value}"]]')
        sleep(1)
        resource.click_edi_button()
        after_all_value = adds.batch_acquisition_input(all_value)
        username = resource.get_find_element_xpath('//label[text()="更新者"]/following-sibling::div//input').get_attribute(
            "value")
        updatatime = resource.get_find_element_xpath(
            '//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        after_checked = resource.get_find_element_xpath(
            '//label[text()="无效资源"]/following-sibling::div//label/span').get_attribute("class")
        today_str = date.today().strftime('%Y/%m/%d')
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        resource.right_refresh('资源')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(
            num) == (int(len_num) + 3) and before_checked == after_checked
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not resource.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_resource_select2(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        driver.execute_script("document.body.style.zoom='1'")
        resource.right_refresh('资源')
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = resource.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            resource.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            resource.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]//input')
        eles = resource.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        resource.right_refresh('资源')
        assert len(eles) == 0
        assert not resource.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_resource_select3(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        name = resource.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        resource.hover("包含")
        sleep(1)
        resource.select_input_resource(first_char)
        sleep(1)
        eles = resource.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        resource.right_refresh('资源')
        assert all(first_char in text for text in list_)
        assert not resource.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_resource_select4(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        name = resource.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        resource.hover("符合开头")
        sleep(1)
        resource.select_input_resource(first_char)
        sleep(1)
        eles = resource.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        resource.right_refresh('资源')
        assert all(str(resource).startswith(first_char) for resource in list_)
        assert not resource.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_resource_select5(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        name = resource.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        resource.hover("符合结尾")
        sleep(1)
        resource.select_input_resource(last_char)
        sleep(1)
        eles = resource.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        resource.right_refresh('资源')
        assert all(str(resource).endswith(last_char) for resource in list_)
        assert not resource.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_resource_clear(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        name = "3"
        sleep(1)
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        resource.hover("包含")
        sleep(1)
        resource.select_input_resource(name)
        sleep(1)
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        resource.hover("清除所有筛选条件")
        sleep(1)
        ele = resource.get_find_element_xpath('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        resource.right_refresh('资源')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not resource.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_resource_ctrlIrepeat(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        resource.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = resource.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = resource.get_error_message()
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not resource.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_resource_ctrlI(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        resource.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        resource.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        resource.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = resource.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        resource.get_find_message()
        resource.select_input_resource('1没有数据添加')
        ele2 = resource.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not resource.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_resource_ctrlM(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        resource.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        resource.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        resource.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = resource.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        resource.get_find_message()
        resource.select_input_resource('1没有数据修改')
        ele2 = resource.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        resource.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        resource.click_del_button()
        resource.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = resource.get_find_message()
        resource.right_refresh('资源')
        assert message == "删除成功！"
        assert not resource.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_resource_ctrlC(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        resource.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = resource.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        resource.click_button('//p[text()="资源代码"]/ancestor::div[2]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = resource.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        resource.right_refresh('资源')
        assert all(before_data in ele for ele in eles)
        assert not resource.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_resource_shift(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        resource.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = resource.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = resource.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not resource.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_resource_ctrls(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 ResourcePage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        resource.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = resource.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = resource.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        resource.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = resource.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not resource.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_resource_delsuccess(self, login_to_resource):
        driver = login_to_resource  # WebDriver 实例
        resource = ResourcePage(driver)  # 用 driver 初始化 resourcePage
        layout = "测试布局A"

        value = ['111', '11测试全部数据', '1测试A', '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        resource.del_all(value, xpath='//p[text()="资源代码"]/ancestor::div[2]//input')
        data = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        resource.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in data)
        assert 0 == len(after_layout)
        assert not resource.has_fail_message()
