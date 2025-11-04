import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.function_page import FunctionPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_function():
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
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("导航栏测试用例")
@pytest.mark.run(order=26)
class TestFunctionPage:
    @allure.story("关闭导航栏页面成功")
    # @pytest.mark.run(order=1)
    def test_function_close1(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        data_list = ["客户", "物品组", "物品"]
        function.go_navigation(data_list[0], data_list[1], data_list[2])
        function.click_button(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        function.click_button(f'//div[./div[text()=" {data_list[2]} "] and contains(@class,"actionLabel")]/span')
        eles = driver.find_elements(By.XPATH, f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        assert len(eles) == 0
        assert not function.has_fail_message()

    @allure.story("右键关闭其他导航栏成功")
    # @pytest.mark.run(order=1)
    def test_function_close2(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        data_list = ["客户", "物品组", "物品"]
        function.go_navigation(data_list[0], data_list[1], data_list[2])
        item = function.get_find_element_xpath(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        function.click_button(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        # 右键点击
        ActionChains(driver).context_click(item).perform()
        function.click_button('//li[text()=" 关闭其他"]')
        eles = driver.find_elements(By.XPATH, f'//div[@class="scroll-body"]/div')
        assert len(eles) == 2
        assert not function.has_fail_message()

    @allure.story("右键关闭所有导航栏成功")
    # @pytest.mark.run(order=1)
    def test_function_close3(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        data_list = ["客户", "物品组", "物品"]
        function.go_navigation(data_list[0], data_list[1], data_list[2])
        item = function.get_find_element_xpath(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        function.click_button(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        # 右键点击
        ActionChains(driver).context_click(item).perform()
        function.click_button('//li[text()=" 关闭所有"]')
        eles = driver.find_elements(By.XPATH, f'//div[@class="scroll-body"]/div')
        assert len(eles) == 1
        assert not function.has_fail_message()

    @allure.story("导航栏刷新功能成功")
    # @pytest.mark.run(order=1)
    def test_function_ref(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        data_list = ["客户", "物品组", "物品"]
        function.go_navigation(data_list[0], data_list[1], data_list[2])
        item = function.get_find_element_xpath(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        function.click_button(f'//div[@class="scroll-body"]//div[text()=" {data_list[2]} "]')
        # 物料代码筛选框输入123
        function.enter_texts(
            '//p[text()="物料代码"]/ancestor::div[2]//input', "123"
        )
        # 右键点击
        ActionChains(driver).context_click(item).perform()
        function.click_button('//li[text()=" 刷新"]')
        itemtext = function.get_find_element_xpath(
            '//p[text()="物料代码"]/ancestor::div[2]//input'
        ).text
        assert itemtext == ""
        assert not function.has_fail_message()

    @allure.story("搜索页面进入指定页面")
    # @pytest.mark.run(order=1)
    def test_function_gopage(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        name = "客户"
        num = driver.find_elements(By.XPATH, f'//div[@class="scroll-body"]/div')
        function.enter_texts('//input[@class="vxe-input--inner" and @placeholder="搜索"]', f"{name}")
        function.click_button(f'//div[@class="my-dropdown1"]/div[.//span[text()="{name}"]]')
        customers = function.get_find_element_xpath(f'//div[@class="scroll-body"]//div[text()=" {name} "]')
        assert len(num) == 1 and customers.text == name
        assert not function.has_fail_message()

    @allure.story("收藏页面成功")
    # @pytest.mark.run(order=1)
    def test_function_collect(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        name = "客户"
        function.go_navigation(name1=name)
        # 定位元素
        element = function.get_find_element_xpath(f'(//span[text()="{name}"])[1]')
        # 鼠标悬停
        ActionChains(driver).move_to_element(element).perform()
        function.click_button(f'(//span[text()="{name}"])[1]/following-sibling::i')
        message = function.get_find_message()
        function.click_button('(//div[@class="ivu-dropdown-rel" and ./i[contains(@class,"icon-wrapper")]])[2]')
        sleep(3)
        eles = driver.find_elements(By.XPATH, '//div[@class="ivu-select-dropdown GroundGlass"]/ul/li')
        assert message == "收藏成功"
        assert any(li.text.strip() == "客户" for li in eles)
        assert not function.has_fail_message()

    @allure.story("取消收藏页面成功")
    # @pytest.mark.run(order=1)
    def test_function_nocollect(self, login_to_function):
        driver = login_to_function
        function = FunctionPage(driver)
        name = "客户"
        function.go_navigation(name1=name)
        # 定位元素
        element = function.get_find_element_xpath(f'(//span[text()="{name}"])[1]')
        # 鼠标悬停
        ActionChains(driver).move_to_element(element).perform()
        function.click_button(f'(//span[text()="{name}"])[1]/following-sibling::i')
        message = function.get_find_message()
        function.click_button('(//div[@class="ivu-dropdown-rel" and ./i[contains(@class,"icon-wrapper")]])[2]')
        sleep(3)
        eles = driver.find_elements(By.XPATH, '//div[@class="ivu-select-dropdown GroundGlass"]/ul/li')
        # 提取所有元素的文本并去除空格
        texts = [li.text.strip() for li in eles]

        # 断言 "客户" 不在列表中
        assert message == "取消成功"
        assert "客户" not in texts
        assert not function.has_fail_message()





