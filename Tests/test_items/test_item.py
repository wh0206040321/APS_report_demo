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
from Pages.itemsPage.item_page import ItemPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_item():
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
        page.click_button('(//span[text()="物品"])[1]')  # 点击物品
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物料表测试用例")
@pytest.mark.run(order=4)
class TestItemPage:
    @allure.story("添加物料信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_item_addfail(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        layout = "测试布局A"
        item.add_layout(layout)
        # 获取布局名称的文本元素
        name = item.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        item.click_add_button()
        # 物料代码xpath
        input_box = item.get_find_element_xpath(
            '(//label[text()="物料代码"])[1]/parent::div//input'
        )
        # 物料名称xpath
        inputname_box = item.get_find_element_xpath(
            '(//label[text()="物料名称"])[1]/parent::div//input'
        )
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        bordername_color = inputname_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert (
            bordername_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert layout == name
        assert not item.has_fail_message()

    @allure.story("添加物料信息，只填写物料代码，不填写物料名称，不允许提交")
    # @pytest.mark.run(order=2)
    def test_item_addcodefail(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        item.click_add_button()
        item.enter_texts(
            '(//label[text()="物料代码"])[1]/parent::div//input', "text1231"
        )
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = item.get_find_element_xpath(
            '(//label[text()="物料名称"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not item.has_fail_message()

    @allure.story("添加物料信息，只填写物料名称，不填写物料代码，不允许提交")
    # @pytest.mark.run(order=3)
    def test_item_addnamefail(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        item.click_add_button()
        item.enter_texts(
            '(//label[text()="物料名称"])[1]/parent::div//input', "text1231"
        )

        # 点击确定
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        input_box = item.get_find_element_xpath(
            '(//label[text()="物料代码"])[1]/parent::div//input'
        )
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert not item.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_item_addnum(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_add_button()  # 检查点击添加
        # 数值特征数字框输入文字字母符号数字
        item.enter_texts(
            '(//label[text()="数值特征1"])[1]/parent::div//input', "1文字abc。？~1_2+3"
        )
        sleep(1)
        # 获取数值特征数字框
        itemnum = item.get_find_element_xpath(
            '(//label[text()="数值特征1"])[1]/parent::div//input'
        ).get_attribute("value")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert itemnum == "1123", f"预期{itemnum}"
        assert not item.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_item_addsel(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_add_button()  # 检查点击添加
        # 自动补充标志下拉框
        item.click_button(
            '(//label[text()="自动补充标志"])[1]/parent::div//input[@class="ivu-select-input"]'
        )
        # 自动补充标志选择是(是库存+1对1制造)
        item.click_button('//li[text()="是(库存+1对1制造)"]')
        # 获取自动补充标志下拉框
        itemsel = item.get_find_element_xpath(
            '(//label[text()="自动补充标志"])[1]/parent::div//input['
            '@class="ivu-select-input"]'
        ).get_attribute("value")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert itemsel == "是(库存+1对1制造)", f"预期{itemsel}"
        assert not item.has_fail_message()

    @allure.story("代码设计器选择成功，并且没有乱码")
    # @pytest.mark.run(order=1)
    def test_item_addcodebox(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        item.click_add_button()  # 检查点击添加
        # 点击代码设计器
        item.click_button('(//label[text()="关联条件"])[1]/parent::div//i')
        # 点击标准登录
        item.click_button('(//div[text()=" 标准登录 "])[1]')
        # 首先，定位到你想要双击的元素
        element_to_double_click = driver.find_element(
            By.XPATH, '(//span[text()="订单规格1相等"])[1]'
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        # 点击确认
        item.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
        # 获取代码设计器文本框
        sleep(1)
        itemcode = item.get_find_element_xpath(
            '(//label[text()="关联条件"])[1]/parent::div//input'
        ).get_attribute("value")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        item.right_refresh('物品')
        assert itemcode == "ME.Order.Spec1==OTHER.Order.Spec1", f"预期{itemcode}"
        assert not item.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_item_textverify(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        item.add_test_item(name)
        item.enter_texts('(//label[text()="物料优先度"])[1]/parent::div//input', name)
        # 点击确定
        item.click_confirm()
        adddata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        num_ = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[6]'
        ).text
        assert adddata == name and num_ == "9999999999", f"预期数据是111，实际得到{adddata}"
        assert not item.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_item_addsuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "111"
        item.add_test_item(name)
        # 点击确定
        item.click_confirm()
        adddata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是111，实际得到{adddata}"
        assert not item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_item_addrepeat(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "111"
        item.add_test_item(name)
        # 点击确定
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute("innerText")
        item.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_item_delcancel(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "111"
        # 定位内容为‘111’的行
        item.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert itemdata == name, f"预期{itemdata}"
        assert not item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_item_addsuccess1(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "1测试A"
        item.add_test_item(name)
        # 点击确定
        item.click_confirm()
        adddata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是1测试A，实际得到{adddata}"
        assert not item.has_fail_message()

    @allure.story("修改物料代码重复")
    # @pytest.mark.run(order=1)
    def test_item_editrepeat(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "1测试A"
        # 选中1测试A物料代码
        item.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        item.click_edi_button()
        # 物料代码输入111
        item.enter_texts('(//label[text()="物料代码"])[1]/parent::div//input', "111")
        # 点击确定
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute("innerText")
        item.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not item.has_fail_message()

    @allure.story("修改物料代码成功")
    # @pytest.mark.run(order=1)
    def test_item_editcodesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "1测试A"
        # 选中1测试A物料代码
        item.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        item.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 物料代码输入
        item.enter_texts(
            '(//label[text()="物料代码"])[1]/parent::div//input', f"{text}"
        )
        # 点击确定
        item.click_confirm()
        # 定位表格内容
        itemdata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]'
        ).text
        assert itemdata == text, f"预期{itemdata}"
        assert not item.has_fail_message()

    @allure.story("把修改后的物料代码改回来")
    # @pytest.mark.run(order=1)
    def test_item_editcodesuccess2(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "1测试A"
        # 选中1测试A物料代码
        item.click_button(f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]')
        # 点击修改按钮
        item.click_edi_button()
        # 物料代码输入
        item.enter_texts('(//label[text()="物料代码"])[1]/parent::div//input', f"{name}")
        # 点击确定
        item.click_confirm()
        # 定位表格内容
        itemdata = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert itemdata == name, f"预期{itemdata}"
        assert not item.has_fail_message()

    @allure.story("修改物料名称，自动补充标识，关联条件成功")
    # @pytest.mark.run(order=1)
    def test_item_editnamesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "1测试A"
        # 选中物料代码
        item.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        item.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 输入修改的物料名称
        item.enter_texts(
            '(//label[text()="物料名称"])[1]/parent::div//input', f"{text}"
        )
        # 获取修改好的值
        editname = item.get_find_element_xpath(
            '(//label[text()="物料名称"])[1]/parent::div//input'
        ).get_attribute("value")

        # 修改自动补充标识 自动补充标志下拉框
        item.click_button(
            '(//label[text()="自动补充标志"])[1]/parent::div//input[@class="ivu-select-input"]'
        )
        # 自动补充标志选择是(是库存+1对1制造)
        item.click_button('//li[text()="是(库存+1对1制造)"]')
        # 获取自动补充标志下拉框的值
        itemsel = item.get_find_element_xpath(
            '(//label[text()="自动补充标志"])[1]/parent::div//input[@class="ivu-select-input"]'
        ).get_attribute("value")

        # 修改关联条件 点击代码设计器
        item.click_button('(//label[text()="关联条件"])[1]/parent::div//i')
        # 点击标准登录
        item.click_button('(//div[text()=" 标准登录 "])[1]')
        # 首先，定位到你想要双击的元素
        element_to_double_click = driver.find_element(
            By.XPATH, '(//span[text()="订单规格1相等"])[1]'
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        # 点击确认
        item.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'
        )
        # 获取代码设计器文本框
        sleep(1)
        itemcode = item.get_find_element_xpath(
            '(//label[text()="关联条件"])[1]/parent::div//input'
        ).get_attribute("value")
        # 点击确定
        item.click_confirm()
        # 定位表格内容
        itemname = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]/div'
        ).text
        itemautoGenerateFlag = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[8]/div'
        ).text
        sleep(1)
        itempeggingConditionExpr = item.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[10]/div'
        ).text
        assert (
            itemname == editname
            and itemautoGenerateFlag == itemsel
            and itempeggingConditionExpr == itemcode
        )
        assert not item.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_item_refreshsuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        # 物料代码筛选框输入123
        item.enter_texts(
            '//p[text()="物料代码"]/ancestor::div[2]//input', "123"
        )
        item.click_ref_button()
        itemtext = item.get_find_element_xpath(
            '//p[text()="物料代码"]/ancestor::div[2]//input'
        ).text
        assert itemtext == "", f"预期{itemtext}"
        assert not item.has_fail_message()

    @allure.story("查询物料代码成功")
    # @pytest.mark.run(order=1)
    def test_item_selectcodesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "1测试A"
        # 点击查询
        item.click_sel_button()
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
        # 点击物料代码
        item.click_button('//div[text()="物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        # 定位第一行是否为name
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        item.right_refresh('物品')
        assert itemcode == name and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_item_selectnodatasuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        # 点击查询
        item.click_sel_button()
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
        # 点击物料代码
        item.click_button('//div[text()="物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        item.right_refresh('物品')
        assert len(itemcode) == 0
        assert not item.has_fail_message()

    @allure.story("查询物料名字包含A成功")
    # @pytest.mark.run(order=1)
    def test_item_selectnamesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "A"
        # 点击查询
        item.click_sel_button()
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
        # 点击物料名称
        item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        eles = item.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        item.right_refresh('物品')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not item.has_fail_message()

    @allure.story("查询物料优先度>0")
    # @pytest.mark.run(order=1)
    def test_item_selectsuccess1(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        num = 0
        # 点击查询
        item.click_sel_button()
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
        # 点击物料优先度
        item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            num,
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        eles = item.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[6]')
        item.right_refresh('物品')
        assert len(eles) > 0
        assert all(int(ele) > num for ele in eles)
        assert not item.has_fail_message()

    @allure.story("查询物料名称包含A并且物料优先度>0")
    # @pytest.mark.run(order=1)
    def test_item_selectsuccess2(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "A"
        num = 0
        # 点击查询
        item.click_sel_button()
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
        # 点击物料名称
        item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        item.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[2]',
        )
        # 双击命令
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
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        item.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        item.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        item.click_select_button()
        eles1 = item.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[6]')
        eles2 = item.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        item.right_refresh('物品')
        assert len(eles1) > 0 and len(eles2) > 0
        assert all(int(ele) > num for ele in eles1) and all(name in ele for ele in eles2)
        assert not item.has_fail_message()

    @allure.story("查询物料名称包含A或物料优先度≥1")
    # @pytest.mark.run(order=1)
    def test_item_selectsuccess3(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage

        name = "A"
        num = 1
        # 点击查询
        item.click_sel_button()
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
        # 点击物料名称
        item.click_button('//div[text()="物料名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        item.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        item.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        item.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        item.click_button('//div[text()="物料优先度" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        item.click_button('//div[text()="≥" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值0
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        item.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        item.click_select_button()
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
                td6_raw = tds[5].text.strip()
                td6_raw = int(td6_raw) if td6_raw else 0

                assert name in td3 or td6_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td8={td6_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td6_raw = tds[5].text.strip()
                td6_raw = int(td6_raw) if td6_raw else 0
                assert name in td3 or td6_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td5={td6_raw}"
                valid_count += 1
        assert not item.has_fail_message()
        item.right_refresh('物品')
        print(f"符合条件的行数：{valid_count}")

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_item_addall(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        adds = AddsPages(driver)
        input_value = '11测试全部数据'
        item.click_add_button()
        custom_xpath_list = [
            f'//label[text()="自定义字符{i}"]/following-sibling::div//input'
            for i in range(1, 21)
        ]
        text_list = [
            '//label[text()="物料代码"]/following-sibling::div//input',
            '//label[text()="物料名称"]/following-sibling::div//input',
            '//label[text()="工作分割比率"]/following-sibling::div//input',
            '//label[text()="备注"]/following-sibling::div//input',
        ]
        text_list.extend(custom_xpath_list)
        adds.batch_modify_input(text_list, input_value)


        value_bos = '//div[@class="vxe-modal--body"]//table[@class="vxe-table--body"]//tr[1]/td[3]'
        spe_xpath_list = [
            f'//label[text()="生产特征{i}"]/following-sibling::div//i'
            for i in range(1, 11)
        ]
        box_list = [
            '//label[text()="物料组代码"]/following-sibling::div//i',
            '//label[text()="BASE物料"]/following-sibling::div//i',
            '//label[text()="资源"]/following-sibling::div//i',
            '//label[text()="物料切换对象"]/following-sibling::div//i',
        ]
        box_list.extend(spe_xpath_list)
        adds.batch_modify_dialog_box(box_list, value_bos)


        code_value = '//span[text()="AdvanceAlongResourceWorkingTime"]'
        code_list = [
            '//label[text()="关联条件"]/following-sibling::div//i',
            '//label[text()="关联时工作输出指令排序表达式"]/following-sibling::div//i',
            '//label[text()="关联时工作输入指令排序表达式"]/following-sibling::div//i',
            '//label[text()="库存MIN2日期表达式"]/following-sibling::div//i',
            '//label[text()="库存MIN3日期表达式"]/following-sibling::div//i',
            '//label[text()="目标库存MIN日期表达式"]/following-sibling::div//i',
            '//label[text()="库存有效期限"]/following-sibling::div//i',
        ]
        adds.batch_modify_code_box(code_list, code_value)

        select_list = [
            {"select": '//label[text()="物料种类"]/following-sibling::div//i', "value": '//li[text()="原材料"]'},
            {"select": '//label[text()="自动补充标志"]/following-sibling::div//i', "value": '//li[text()="是(库存+1对1制造)"]'},
            {"select": '//label[text()="备料方法"]/following-sibling::div//i', "value": '//li[text()="采购优先"]'},
            {"select": '//label[text()="显示颜色"]/following-sibling::div//i', "value": '//span[text()="RGB(128,128,255)"]'},
            {"select": '//label[text()="物料切换方法"]/following-sibling::div//i', "value": '//li[text()="混存"]'},
            {"select": '//label[text()="物料制约标志"]/following-sibling::div//i', "value": '//label[text()="物料制约标志"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="是"]'},
            {"select": '//label[text()="库存增减方法"]/following-sibling::div//i', "value": '//li[text()="线形/梯形"]'},
            {"select": '//label[text()="制造批量大小计算方法"]/following-sibling::div//i', "value": '//li[text()="均等"]'},
            {"select": '//label[text()="制造批量尾数为末尾"]/following-sibling::div//i', "value": '//label[text()="制造批量尾数为末尾"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="否"]'},
            {"select": '//label[text()="采购批量计算方法"]/following-sibling::div//i', "value": '//label[text()="采购批量计算方法"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="均等"]'},
            {"select": '//label[text()="采购批量尾数为末尾"]/following-sibling::div//i', "value": '//label[text()="采购批量尾数为末尾"]/following-sibling::div//div[@class="ivu-select-dropdown"]//li[text()="否"]'},
        ]
        adds.batch_modify_select_input(select_list)

        input_num_value = '1'
        num_xpath_list1 = [
            f'//label[text()="数值特征{i}"]/following-sibling::div//input'
            for i in range(1, 6)
        ]
        num_xpath_list2 = [
            f'//label[text()="自定义数值{i}"]/following-sibling::div//input'
            for i in range(1, 21)
        ]
        num_xpath_list3 = [
            f'//label[text()="{label}{i}"]/following-sibling::div//input'
            for i in range(1, 8)
            for label in ["单批上限", "合批上限", "合批期间"]
        ]

        num_list = [
            '//label[text()="物料优先度"]/following-sibling::div//input',
            '//label[text()="单价"]/following-sibling::div//input',
            '//label[text()="制造效率"]/following-sibling::div//input',
            '//label[text()="显示顺序"]/following-sibling::div//input',
            '//label[text()="库存MIN"]/following-sibling::div//input',
            '//label[text()="库存MIN2"]/following-sibling::div//input',
            '//label[text()="库存MIN3"]/following-sibling::div//input',
            '//label[text()="预留"]/following-sibling::div//input',
            '//label[text()="目标库存MIN"]/following-sibling::div//input',
            '//label[text()="库存MAX"]/following-sibling::div//input',
            '//label[text()="制造批量MAX"]/following-sibling::div//input',
            '//label[text()="制造批量MIN"]/following-sibling::div//input',
            '//label[text()="制造批量单位"]/following-sibling::div//input',
            '//label[text()="采购批量MAX"]/following-sibling::div//input',
            '//label[text()="采购批量MIN"]/following-sibling::div//input',
            '//label[text()="采购批量单位"]/following-sibling::div//input',
            '//label[text()="工作分割数量"]/following-sibling::div//input',
            '//label[text()="工作并行数量"]/following-sibling::div//input',
            '//label[text()="工作批量MIN"]/following-sibling::div//input',
            '//label[text()="工作批量MAX"]/following-sibling::div//input',
            '//label[text()="工作批量单位"]/following-sibling::div//input',
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
        all_value = text_list + box_input_list + code_input_list + select_input_list + num_list + time_xpath_list
        len_num = len(all_value)
        before_all_value = adds.batch_acquisition_input(all_value)
        item.click_confirm()
        driver.refresh()
        item.wait_for_loading_to_disappear()
        num = adds.go_settings_page()
        sleep(1)
        item.enter_texts(
            '//p[text()="物料代码"]/ancestor::div[2]//input', input_value
        )
        sleep(1)
        item.click_button(
            f'(//div[@class="vxe-table--main-wrapper"])[2]//table[@class="vxe-table--body"]//tr/td[2][.//span[text()="{input_value}"]]')
        sleep(1)
        item.click_edi_button()
        after_all_value = adds.batch_acquisition_input(all_value)
        username = item.get_find_element_xpath('//label[text()="更新者"]/following-sibling::div//input').get_attribute("value")
        updatatime = item.get_find_element_xpath('//label[text()="更新时间"]/following-sibling::div//input').get_attribute("value")
        today_str = date.today().strftime('%Y/%m/%d')
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert before_all_value == after_all_value and username == DateDriver().username and today_str in updatatime and int(num) == (int(len_num) + 2)
        assert all(before_all_value), "列表中存在为空或为假值的元素！"
        assert not item.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_item_select2(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        driver.execute_script("document.body.style.zoom='1'")
        item.right_refresh('物品')
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = item.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            item.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            item.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]//input')
        eles = item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        item.right_refresh('物品')
        assert len(eles) == 0
        assert not item.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_item_select3(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        item.hover("包含")
        sleep(1)
        item.select_input_item(first_char)
        sleep(1)
        eles = item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        item.right_refresh('物品')
        assert all(first_char in text for text in list_)
        assert not item.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_item_select4(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        item.hover("符合开头")
        sleep(1)
        item.select_input_item(first_char)
        sleep(1)
        eles = item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        item.right_refresh('物品')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not item.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_item_select5(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        item.hover("符合结尾")
        sleep(1)
        item.select_input_item(last_char)
        sleep(1)
        eles = item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        item.right_refresh('物品')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not item.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_item_clear(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        name = "3"
        sleep(1)
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        item.hover("包含")
        sleep(1)
        item.select_input_item(name)
        sleep(1)
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i')
        item.hover("清除所有筛选条件")
        sleep(1)
        ele = item.get_find_element_xpath('//p[text()="物料代码"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        item.right_refresh('物品')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not item.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_item_ctrlIrepeat(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = item.get_error_message()
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not item.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_item_ctrlI(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        item.get_find_message()
        item.select_input_item('1没有数据添加')
        ele2 = item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not item.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_item_ctrlM(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        item.get_find_message()
        item.select_input_item('1没有数据修改')
        ele2 = item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        item.click_del_button()
        item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = item.get_find_message()
        item.right_refresh('物品')
        assert message == "删除成功！"
        assert not item.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_item_ctrlC(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        item.click_button('//p[text()="物料代码"]/ancestor::div[2]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        item.right_refresh('物品')
        assert all(before_data in ele for ele in eles)
        assert not item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_item_shift(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = item.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_item_ctrls(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = item.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = item.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not item.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_item_delsuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        driver.refresh()
        item.wait_for_loading_to_disappear()
        layout = "测试布局A"

        value = ['111', '11测试全部数据', '1测试A','111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111']
        item.del_all(value, xpath='//p[text()="物料代码"]/ancestor::div[2]//input')
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        item.del_layout(layout)
        item.wait_for_loading_to_disappear()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in itemdata)
        assert 0 == len(after_layout)
        assert not item.has_fail_message()

