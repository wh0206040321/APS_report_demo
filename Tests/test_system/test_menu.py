import logging
import os
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.expression_page import ExpressionPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_menu():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
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
        list_ = ["系统管理", "系统设置", "菜单组件"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("菜单组件页用例")
@pytest.mark.run(order=213)
class TestSMenuPage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_menu_addfail1(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        menu.add_layout(layout)
        # 获取布局名称的文本元素
        name = menu.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        sleep(1)
        menu.click_all_button("新增")
        sleep(1)
        menu.click_confirm()
        message = menu.get_error_message()
        menu.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert layout == name
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not menu.has_fail_message()

    @allure.story("新增只填写组件代码点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_menu_addfail2(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = 'ABCDAA'
        menu.wait_for_loading_to_disappear()
        menu.click_all_button("新增")
        menu.enter_texts('//div[@id="ph5ht87u-mndd"]//input', name)
        menu.click_confirm()
        message = menu.get_error_message()
        menu.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not menu.has_fail_message()

    @allure.story("新增填写代码和名称点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_menu_addfail3(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = 'ABCDAA'
        menu.wait_for_loading_to_disappear()
        menu.click_all_button("新增")
        menu.enter_texts('//div[@id="ph5ht87u-mndd"]//input', name)
        menu.enter_texts('//div[@id="t4svyhz8-n3vp"]//input', name)
        menu.click_confirm()
        message = menu.get_error_message()
        menu.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not menu.has_fail_message()

    @allure.story("添加菜单成功")
    # @pytest.mark.run(order=1)
    def test_menu_addsuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = 'ABCDAA'
        menu.wait_for_loading_to_disappear()
        menu.click_all_button("新增")
        menu.enter_texts('//div[@id="ph5ht87u-mndd"]//input', name)
        menu.enter_texts('//div[@id="t4svyhz8-n3vp"]//input', name)
        menu.click_button('//div[@id="twqlo0fa-ulcj"]//i')
        menu.click_button('//div[div[text()="请选择图标"]]/following-sibling::div//div[@class="flex-wrap"]/div')
        sleep(0.5)
        menu.click_confirm()
        message = menu.get_find_message()
        menu.select_input_menu(name)
        sleep(1)
        eles = menu.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        assert eles == name
        assert message == "新增成功！"
        assert not menu.has_fail_message()

    @allure.story("添加重复组件代码不允许添加")
    # @pytest.mark.run(order=1)
    def test_menu_addrepeat1(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = 'ABCDAA'
        menu.wait_for_loading_to_disappear()
        menu.click_all_button("新增")
        menu.enter_texts('//div[@id="ph5ht87u-mndd"]//input', name)
        menu.enter_texts('//div[@id="t4svyhz8-n3vp"]//input', name)
        menu.click_button('//div[@id="twqlo0fa-ulcj"]//i')
        menu.click_button('//div[div[text()="请选择图标"]]/following-sibling::div//div[@class="flex-wrap"]/div')
        sleep(0.5)
        menu.click_confirm()
        sleep(1)
        message = menu.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute('innerText')
        menu.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        menu.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == "记录已存在,请检查！"
        assert not menu.has_fail_message()

    @allure.story("修改重复需求来源编码不允许修改")
    # @pytest.mark.run(order=1)
    def test_menu_update(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        value = "ABCDAA"
        menu.select_input_menu(value)
        menu.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{value}"]')
        menu.click_all_button("编辑")
        sleep(2)
        ele = menu.get_find_element_xpath('//div[@id="0lollcex-w9k3"]//input').get_attribute("readonly")
        menu.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert ele == "true" or ele == "readonly"
        assert not menu.has_fail_message()

    @allure.story("修改组件名称，图标成功")
    # @pytest.mark.run(order=1)
    def test_menu_updatesuccess1(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        before_name = 'ABCDAA'
        after_name = 'ACDAA'
        menu.wait_for_loading_to_disappear()
        menu.select_input_menu(before_name)
        menu.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{before_name}"]')
        menu.click_all_button("编辑")
        menu.enter_texts('//div[@id="b4cp83c8-qiax"]//input', after_name)
        menu.click_button('//div[@id="3srdw2xs-v6kc"]//i')
        menu.click_button('//div[div[text()="请选择图标"]]/following-sibling::div//div[@class="flex-wrap"]/div[2]')
        sleep(0.5)
        menu.click_confirm()
        message = menu.get_find_message()
        menu.select_input_menu(before_name)
        eles2 = menu.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[3]').text
        assert eles2 == after_name
        assert message == "编辑成功！"
        assert not menu.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_menu_refreshsuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        before_name = 'ABCDAA'
        menu.select_input_menu(before_name)
        menu.right_refresh('菜单组件')
        menutext = menu.get_find_element_xpath(
            '//div[div[span[text()=" 组件代码"]]]//input'
        ).text
        assert menutext == "", f"预期{menutext}"
        assert not menu.has_fail_message()

    @allure.story("查询组件代码成功")
    # @pytest.mark.run(order=1)
    def test_menu_selectsuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "SchedulingManagement"
        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="组件代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        menu.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        menu.click_select_button2()
        # 定位第一行是否为name
        itemcode = menu.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[2]',
        )
        menu.right_refresh('菜单组件')
        assert itemcode == name and len(itemcode2) == 0
        assert not menu.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_menu_selectnodatasuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="组件代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        menu.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        menu.click_select_button2()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        )
        menu.right_refresh('菜单组件')
        assert len(itemcode) == 0
        assert not menu.has_fail_message()

    @allure.story("查询组件名称包含A成功")
    # @pytest.mark.run(order=1)
    def test_menu_selectnamesuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "A"
        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="组件名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        menu.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        menu.click_select_button2()
        eles = menu.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        menu.right_refresh('菜单组件')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not menu.has_fail_message()

    @allure.story("查询排序>3")
    # @pytest.mark.run(order=1)
    def test_menu_selectsuccess1(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        num = 3
        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        menu.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            num,
        )
        sleep(1)

        # 点击确认
        menu.click_select_button2()
        eles = menu.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        menu.right_refresh('菜单组件')
        assert len(eles) > 0
        assert all(int(ele) > num for ele in eles)
        assert not menu.has_fail_message()

    @allure.story("查询组件名称包含计划并且排序>3")
    # @pytest.mark.run(order=1)
    def test_menu_selectsuccess2(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "计划"
        num = 3
        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="组件名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        menu.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        menu.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        menu.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        menu.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        menu.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        menu.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        menu.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        menu.click_select_button2()
        eles1 = menu.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        eles2 = menu.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        menu.right_refresh('菜单组件')
        assert len(eles1) > 0 and len(eles2) > 0
        assert all(int(ele) > num for ele in eles1) and all(name in ele for ele in eles2)
        assert not menu.has_fail_message()

    @allure.story("查询组件名称包含计划或物料优先度≥4")
    # @pytest.mark.run(order=1)
    def test_menu_selectsuccess3(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "计划"
        num = 4
        # 点击查询
        menu.click_all_button("查询")
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
        menu.click_button('//div[text()="组件名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        menu.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        menu.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        menu.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        menu.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        menu.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        menu.click_button('//div[text()="≥" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值0
        menu.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        menu.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        menu.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        menu.click_select_button2()
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
                td5_raw = tds[4].text.strip()
                td5_raw = int(td5_raw) if td5_raw else 0

                assert name in td3 or td5_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td5_raw = tds[4].text.strip()
                td5_raw = int(td5_raw) if td5_raw else 0
                assert name in td3 or td5_raw >= num, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1
        menu.right_refresh('菜单组件')
        assert not menu.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("过滤查组件代码成功")
    # @pytest.mark.run(order=1)
    def test_menu_select1(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        name = "Plan"
        sleep(1)
        menu.select_input_menu(name)
        sleep(2)
        eles = menu.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        menu.right_refresh('菜单组件')
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not menu.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_menu_select2(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        eles = menu.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            menu.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            menu.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//input')
        eles = menu.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        menu.right_refresh('菜单组件')
        assert len(eles) == 0
        assert not menu.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_menu_select3(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        name = "Co"
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        menu.hover("包含")
        sleep(1)
        menu.select_input_menu(name)
        sleep(1)
        eles = menu.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        menu.right_refresh('菜单组件')
        assert all(name in text for text in list_)
        assert not menu.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_menu_select4(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "De"
        menu.wait_for_loading_to_disappear()
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        menu.hover("符合开头")
        sleep(1)
        menu.select_input_menu(name)
        sleep(1)
        eles = menu.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        menu.right_refresh('菜单组件')
        assert all(str(item).startswith(name) for item in list_)
        assert not menu.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_menu_select5(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        name = "t"
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        menu.hover("符合结尾")
        sleep(1)
        menu.select_input_menu(name)
        sleep(1)
        eles = menu.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        menu.right_refresh('菜单组件')
        assert all(str(item).endswith(name) for item in list_)
        assert not menu.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_menu_clear(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu.wait_for_loading_to_disappear()
        name = "3"
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        menu.hover("包含")
        sleep(1)
        menu.select_input_menu(name)
        sleep(1)
        menu.click_button('//div[div[span[text()=" 组件代码"]]]/div[3]//i')
        menu.hover("清除所有筛选条件")
        sleep(1)
        ele = menu.get_find_element_xpath('//div[div[span[text()=" 组件代码"]]]/div[3]//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not menu.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_menu_delsuccess(self, login_to_menu):
        driver = login_to_menu  # WebDriver 实例
        menu = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        menu.wait_for_loading_to_disappear()
        sleep(1)
        value = ['ABCDAA']
        menu.del_all(xpath='//div[div[span[text()=" 组件代码"]]]/div[3]//input', value=value)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:1]
        ]
        menu.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in itemdata)
        assert 0 == len(after_layout)
        assert not menu.has_fail_message()