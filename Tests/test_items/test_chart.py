import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.chart_page import ChartPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_chart():
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
        page.click_button('(//span[text()="计划可视化图表"])[1]')  # 点击计划可视化图表
        page.click_button('(//span[text()="资源甘特图"])[1]')  # 点击资源甘特图
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("资源甘特图测试用例")
@pytest.mark.run(order=23)
class TestChartPage:
    @allure.story("校验文本框成功")
    # @pytest.mark.run(order=1)
    def test_chart_textverify(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        name = '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111'
        chart.click_add_button()
        chart.enter_texts('//input[@placeholder="请输入名称"]', name)
        chart.clicl_confirm_button()
        eles = driver.find_elements(
            By.XPATH, '//div[@class="el-tabs__nav is-top"]/div[@role="tab"]'
        )
        i = 0
        while i < len(eles):
            if eles[i].text == name:
                break
            i += 1
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="{name}"]',
                )
            )
        )
        assert element.text == name
        assert not chart.has_fail_message()

    @allure.story("添加布局名称成功")
    # @pytest.mark.run(order=1)
    def test_chart_addlayout(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_add_button()
        chart.enter_texts('//input[@placeholder="请输入名称"]', "测试布局")
        chart.clicl_confirm_button()
        eles = driver.find_elements(
            By.XPATH, '//div[@class="el-tabs__nav is-top"]/div[@role="tab"]'
        )
        i = 0
        while i < len(eles):
            if eles[i].text == "测试布局":
                break
            i += 1
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局"]',
                )
            )
        )
        assert element.text == "测试布局"
        assert not chart.has_fail_message()

    @allure.story("修改布局名称成功")
    # @pytest.mark.run(order=1)
    def test_chart_editlayout(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        wait = WebDriverWait(driver, 10)
        chart.click_button(
            '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局"]'
        )
        chart.click_button('//a[@title="设置"]')
        input_text = chart.get_find_element_xpath(
            '//label[text()="布局名称"]/following-sibling::div//input'
        )
        input_text.send_keys(Keys.CONTROL + "a")
        input_text.send_keys(Keys.DELETE)
        chart.enter_texts(
            '//label[text()="布局名称"]/following-sibling::div//input', "测试布局修改"
        )
        chart.clicl_confirm_button()
        sleep(1)
        element = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局修改"]',
                )
            )
        )
        assert element.text == "测试布局修改"
        assert not chart.has_fail_message()

    @allure.story("删除布局名称成功")
    # @pytest.mark.run(order=1)
    def test_chart_deletelayout(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button(
            '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局修改"]'
        )
        chart.wait_for_loading_to_disappear()
        chart.click_button(
            '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局修改"]/span'
        )
        chart.wait_for_loading_to_disappear()
        chart.clicl_confirm_button()
        ele = driver.find_elements(
            By.XPATH,
            '//div[@class="el-tabs__nav is-top"]/div[@role="tab" and text()="测试布局修改"]',
        )
        assert len(ele) == 0
        assert not chart.has_fail_message()

    @allure.story("排序方案可选择-显示顺序-升序")
    # @pytest.mark.run(order=1)
    def test_chart_sort1(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('//label[text()="排序方法"]/following-sibling::div//i')
        chart.click_button('(//span[@class="ivu-select-selected-value"])[2]')
        chart.click_button('(//li[text()="显示顺序"])[1]')
        chart.click_button('(//span[@class="ivu-select-selected-value"])[3]')
        chart.click_button('(//li[text()="升序"])[1]')
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="排序方法"]/following-sibling::div//input'
        )
        assert "ME.DisplayOrder,a" in ele.get_attribute("value")
        assert not chart.has_fail_message()

    @allure.story("排序方案可选择-资源代码顺序-降序")
    # @pytest.mark.run(order=1)
    def test_chart_sort2(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('//label[text()="排序方法"]/following-sibling::div//i')
        chart.click_button('(//span[@class="ivu-select-selected-value"])[2]')
        chart.click_button('(//li[text()="资源代码顺序"])[1]')
        chart.click_button('(//span[@class="ivu-select-selected-value"])[3]')
        chart.click_button('(//li[text()="降序"])[1]')
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="排序方法"]/following-sibling::div//input'
        )
        assert "ME.Code,d" in ele.get_attribute("value")
        assert not chart.has_fail_message()

    @allure.story("筛选方法可使用")
    # @pytest.mark.run(order=1)
    def test_chart_filter(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('//label[text()="筛选方法"]/following-sibling::div//i')
        ele = chart.get_find_element_xpath('//span[text()="添加覆盖日历。"]')
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="筛选方法"]/following-sibling::div//input'
        )
        assert (
            "AddOCalendar(Me.OperationMainRes,#2006/10/01 00:00:00#,#2006/10/15 00:00:00#,1)"
            in ele.get_attribute("value")
        )
        assert not chart.has_fail_message()

    @allure.story("指令筛选可使用")
    # @pytest.mark.run(order=1)
    def test_chart_instruction(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('//label[text()="指令筛选"]/following-sibling::div//i')
        ele = chart.get_find_element_xpath('//span[text()="计算运费。"]')
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="指令筛选"]/following-sibling::div//input'
        )
        assert "CalcDeliveryCost(ME)" in ele.get_attribute("value")
        assert not chart.has_fail_message()

    @allure.story("按钮显示文字开关可关闭")
    # @pytest.mark.run(order=1)
    def test_chart_button1(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
        )
        if (
            button.get_attribute("class")
            == "ivu-switch ivu-switch-checked ivu-switch-small"
        ):
            chart.click_button(
                '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()

        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-small" in button.get_attribute("class")
        assert not chart.has_fail_message()

    @allure.story("按钮显示文字开关可开启")
    # @pytest.mark.run(order=1)
    def test_chart_button2(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
        )
        if button.get_attribute("class") == "ivu-switch ivu-switch-small":
            chart.click_button(
                '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="按钮显示文字"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-checked ivu-switch-small" in button.get_attribute(
            "class"
        )
        assert not chart.has_fail_message()

    @allure.story("按钮自动刷新开关可关闭")
    # @pytest.mark.run(order=1)
    def test_chart_button3(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
        )
        if (
            button.get_attribute("class")
            == "ivu-switch ivu-switch-checked ivu-switch-small"
        ):
            chart.click_button(
                '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-small" in button.get_attribute("class")
        assert not chart.has_fail_message()

    @allure.story("按钮自动刷新开关可开启")
    # @pytest.mark.run(order=1)
    def test_chart_button4(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
        )
        if button.get_attribute("class") == "ivu-switch ivu-switch-small":
            chart.click_button(
                '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="自动刷新"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-checked ivu-switch-small" in button.get_attribute(
            "class"
        )
        assert not chart.has_fail_message()

    @allure.story("按钮移动后全固定开关可关闭")
    # @pytest.mark.run(order=1)
    def test_chart_button5(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
        )
        if (
            button.get_attribute("class")
            == "ivu-switch ivu-switch-checked ivu-switch-small"
        ):
            chart.click_button(
                '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-small" in button.get_attribute("class")
        assert not chart.has_fail_message()

    @allure.story("按钮移动后全固定开关可开启")
    # @pytest.mark.run(order=1)
    def test_chart_button6(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
        )
        if button.get_attribute("class") == "ivu-switch ivu-switch-small":
            chart.click_button(
                '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="移动后全固定"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-checked ivu-switch-small" in button.get_attribute(
            "class"
        )
        assert not chart.has_fail_message()

    @allure.story("按钮是否显示工作选择面板开关可关闭")
    # @pytest.mark.run(order=1)
    def test_chart_button7(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
        )
        if (
            button.get_attribute("class")
            == "ivu-switch ivu-switch-checked ivu-switch-small"
        ):
            chart.click_button(
                '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-small" in button.get_attribute("class")
        assert not chart.has_fail_message()

    @allure.story("按钮是否显示工作选择面板开关可开启")
    # @pytest.mark.run(order=1)
    def test_chart_button8(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
        )
        if button.get_attribute("class") == "ivu-switch ivu-switch-small":
            chart.click_button(
                '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="是否显示工作选择面板"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-checked ivu-switch-small" in button.get_attribute(
            "class"
        )
        assert not chart.has_fail_message()

    @allure.story("按钮变更使用时间开关可关闭")
    # @pytest.mark.run(order=1)
    def test_chart_button9(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
        )
        if (
            button.get_attribute("class")
            == "ivu-switch ivu-switch-checked ivu-switch-small"
        ):
            chart.click_button(
                '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-small" in button.get_attribute("class")
        assert not chart.has_fail_message()

    @allure.story("按钮变更使用时间开关可开启")
    # @pytest.mark.run(order=1)
    def test_chart_button10(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
        )
        if button.get_attribute("class") == "ivu-switch ivu-switch-small":
            chart.click_button(
                '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
            )
        chart.clicl_confirm_button()
        sleep(1)
        chart.click_button('//a[@title="设置"]')
        button = chart.get_find_element_xpath(
            '(//label[text()="变更使用时间"]/following-sibling::div//span)[1]'
        )
        assert "ivu-switch ivu-switch-checked ivu-switch-small" in button.get_attribute(
            "class"
        )
        assert not chart.has_fail_message()

    @allure.story("图棒-显示颜色")
    # @pytest.mark.run(order=1)
    def test_chart_picture(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('//div[text()=" 图棒 "]')
        chart.click_button('//label[text()="显示颜色表达式"]/following-sibling::div//i')
        ele = chart.get_find_element_xpath('//span[text()="绝对值函数"]')
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="显示颜色表达式"]/following-sibling::div//input'
        )
        assert "Abs(-1)ME.Order.Color" in ele.get_attribute("value")
        assert not chart.has_fail_message()

    @allure.story("资源甘特图-使用指令棒文本格式表达式")
    # @pytest.mark.run(order=1)
    def test_chart_resource(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('(//div[text()=" 资源甘特图 "])[2]')
        chart.click_button(
            '//label[text()="使用指令棒文本格式表达式"]/following-sibling::div//i'
        )
        chart.click_button('//div[text()=" 标准登录 "]')
        ele = chart.get_find_element_xpath(
            '//span[text()="被分割的前工序工作的制造数量的总和"]'
        )
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="使用指令棒文本格式表达式"]/following-sibling::div//input'
        )
        print(ele.get_attribute("value"))
        assert (
            "Sum(ME.Operation.PrevOperation,TARGET.OperationOutMainItemQty)"
            in ele.get_attribute("value")
        )
        assert not chart.has_fail_message()

    @allure.story("资源甘特图-工作面板显示内容")
    # @pytest.mark.run(order=1)
    def test_chart_work(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('(//div[text()=" 资源甘特图 "])[2]')
        chart.click_button(
            '//label[text()="工作面板显示内容"]/following-sibling::div//i'
        )
        chart.click_button('//div[text()=" 标准登录 "]')
        ele = chart.get_find_element_xpath('//span[text()="副资源(S0)"]')
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="工作面板显示内容"]/following-sibling::div//input'
        )
        print(ele.get_attribute("value"))
        assert (
            "ME.Operation.ProductionTask.UseInstructions['S0'].Resource"
            in ele.get_attribute("value")
        )
        assert not chart.has_fail_message()

    @allure.story("资源甘特图-左侧资源显示表达式")
    # @pytest.mark.run(order=1)
    def test_chart_expression(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        chart.click_button('//a[@title="设置"]')
        chart.click_button('(//div[text()=" 资源甘特图 "])[2]')
        chart.click_button(
            '//label[text()="左侧资源显示表达式"]/following-sibling::div//i'
        )
        chart.click_button('//div[text()=" 标准登录 "]')
        ele = chart.get_find_element_xpath('//span[text()="资源代码"]')
        action = ActionChains(driver)
        action.double_click(ele)
        action.perform()
        chart.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        chart.wait_for_loading_to_disappear()
        ele = chart.get_find_element_xpath(
            '//label[text()="左侧资源显示表达式"]/following-sibling::div//input'
        )
        print(ele.get_attribute("value"))
        assert "ME.Code" in ele.get_attribute("value")
        assert not chart.has_fail_message()

    @allure.story("排产成功")
    # @pytest.mark.run(order=1)
    def test_chart_plan(self, login_to_chart):
        driver = login_to_chart  # WebDriver 实例
        chart = ChartPage(driver)  # 用 driver 初始化 ChartPage
        wait = WebDriverWait(driver, 20)
        chart.click_button('//a[@title="排程"]')
        # 等待下拉框按钮可点击后点击展开
        dropdown_arrow = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="vue-treeselect__control-arrow-container"]')
            )
        )
        dropdown_arrow.click()

        # 等待第一个方案标签可点击后点击选择
        first_option = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@class="vue-treeselect__list"]/div[.]//label[text()="均衡排产"]',
                )
            )
        )
        first_option.click()

        # 执行计划
        chart.click_button('//span[text()="执行计划"]')

        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )

        assert success_element.text == "完成"
        assert not chart.has_fail_message()
