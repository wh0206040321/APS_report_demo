import logging
import os
import re
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
from Pages.systemPage.apps_page import AppsPage
from Pages.systemPage.expression_page import ExpressionPage
from Pages.systemPage.role_page import RolePage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_module():
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
        list_ = ["系统管理", "系统设置", "模块管理"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("模块管理页用例")
@pytest.mark.run(order=214)
class TestSModulePage:

    @allure.story("新增直接点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_module_addfail1(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        layout = "测试布局A"
        module.add_layout(layout)
        # 获取布局名称的文本元素
        name = module.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        sleep(1)
        module.click_all_button("新增")
        sleep(1)
        module.click_confirm()
        message = module.get_error_message()
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert layout == name
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not module.has_fail_message()

    @allure.story("新增模块代码和模块名称点击保存不允许添加")
    # @pytest.mark.run(order=1)
    def test_module_addfail2(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'ABCDAA'
        sleep(1)
        module.click_all_button("新增")
        xpath_list = [
            '//div[span[text()=" 模块代码 "]]/following-sibling::div//input',
            '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
        ]
        add.batch_modify_input(xpath_list, name)
        module.click_confirm()
        message = module.get_error_message()
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == "校验不通过，请检查标红的表单字段！"
        assert not module.has_fail_message()

    @allure.story("新增模块代码成功")
    # @pytest.mark.run(order=1)
    def test_module_addsuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'ABCDAA'
        sleep(1)
        module.click_all_button("新增")
        xpath_list = [
            '//div[span[text()=" 模块代码 "]]/following-sibling::div//input',
            '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
            '//div[span[text()=" 图标 "]]/following-sibling::div//i',
            '//div[@class="flex-wrap"]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        module.click_button(xpath_list[2])
        module.click_button(xpath_list[3])
        module.click_confirm()
        message = module.get_find_message()
        module.wait_for_loading_to_disappear()
        module.select_input_module(name)
        ele = module.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        assert message == "新增成功！" and ele == name
        assert not module.has_fail_message()

    @allure.story("新增重复，不允许添加")
    # @pytest.mark.run(order=1)
    def test_module_addreaped(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        name = 'ABCDAA'
        sleep(1)
        module.click_all_button("新增")
        xpath_list = [
            '//div[span[text()=" 模块代码 "]]/following-sibling::div//input',
            '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
            '//div[span[text()=" 图标 "]]/following-sibling::div//i',
            '//div[@class="flex-wrap"]/div[1]',
        ]
        add.batch_modify_input(xpath_list[:2], name)
        module.click_button(xpath_list[2])
        module.click_button(xpath_list[3])
        module.click_confirm()
        ele = module.finds_elements(By.XPATH, '//div[text()=" 记录已存在,请检查！ "]')
        module.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(ele) == 1
        assert not module.has_fail_message()

    @allure.story("修改对话框按钮代码禁用")
    # @pytest.mark.run(order=1)
    def test_module_updateenabled(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        before_name = 'ABCDAA'
        module.wait_for_loading_to_disappear()
        module.select_input_module(before_name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{before_name}"]')
        sleep(1)
        module.click_all_button("编辑")
        xpath_list = [
            '//div[span[text()=" 组件代码 "]]/following-sibling::div//input',
        ]
        sleep(2)
        ele = module.get_find_element_xpath(xpath_list[0]).get_attribute("readonly")
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert ele == "true" or ele == "readonly"
        assert not module.has_fail_message()

    @allure.story("修改模块名称和排序成功")
    # @pytest.mark.run(order=1)
    def test_module_updatesuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        before_name = 'ABCDAA'
        after_name = 'ACDAA'
        module.wait_for_loading_to_disappear()
        module.select_input_module(before_name)
        module.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        sleep(1)
        module.click_all_button("编辑")
        xpath_list = [
            '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
            '//div[span[text()=" 排序 "]]/following-sibling::div//input',
        ]
        add.batch_modify_input(xpath_list[:1], after_name)
        n = module.get_find_element_xpath(xpath_list[1])
        n.send_keys(Keys.CONTROL, "a")
        n.send_keys(Keys.DELETE)
        module.enter_texts(xpath_list[1], "33")
        module.click_confirm()
        message = module.get_find_message()
        module.select_input_module(before_name)
        sleep(2)
        ele1 = module.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[3]').text
        ele2 = module.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[5]').text
        module.right_refresh('模块管理')
        assert message == "编辑成功！" and ele1 == after_name and ele2 == "33"
        module.select_input_module(before_name)
        module.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        sleep(1)
        module.click_all_button("编辑")
        xpath_list = [
            '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
            '//div[span[text()=" 排序 "]]/following-sibling::div//input',
        ]
        add.batch_modify_input(xpath_list[:1], before_name)
        n = module.get_find_element_xpath(xpath_list[1])
        n.send_keys(Keys.CONTROL, "a")
        n.send_keys(Keys.DELETE)
        module.enter_texts(xpath_list[1], "33")
        module.click_confirm()
        message = module.get_find_message()
        module.select_input_module(before_name)
        sleep(2)
        ele1 = module.get_find_element_xpath(
            f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{before_name}"]]/td[3]').text
        module.right_refresh('模块管理')
        assert message == "编辑成功！" and ele1 == before_name
        assert not module.has_fail_message()

    @allure.story("查询模块代码成功")
    # @pytest.mark.run(order=1)
    def test_module_selectsuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "ComponentSystemSet"
        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="模块代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        module.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        module.click_select_button2()
        # 定位第一行是否为name
        itemcode = module.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[2]',
        )
        module.right_refresh('模块管理')
        assert itemcode == name and len(itemcode2) == 0
        assert not module.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_module_selectnodatasuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="模块代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        module.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        module.click_select_button2()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        )
        module.right_refresh('模块管理')
        assert len(itemcode) == 0
        assert not module.has_fail_message()

    @allure.story("查询模块名称包含计划成功")
    # @pytest.mark.run(order=1)
    def test_module_selectnamesuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "计划"
        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="模块名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        module.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        module.click_select_button2()
        eles = module.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        module.right_refresh('模块管理')
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not module.has_fail_message()

    @allure.story("查询排序>3")
    # @pytest.mark.run(order=1)
    def test_module_selectsuccess1(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        num = 3
        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        module.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            num,
        )
        sleep(1)

        # 点击确认
        module.click_select_button2()
        eles = module.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        module.right_refresh('模块管理')
        assert len(eles) > 0
        assert all(int(ele) > num for ele in eles)
        assert not module.has_fail_message()

    @allure.story("查询模块名称包含计划并且排序>3")
    # @pytest.mark.run(order=1)
    def test_module_selectsuccess2(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "计划"
        num = 4
        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="模块名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        module.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        module.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        module.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        module.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        module.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        module.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        module.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        module.click_select_button2()
        eles1 = module.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        eles2 = module.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        module.right_refresh('模块管理')
        assert len(eles1) > 0 and len(eles2) > 0
        assert all(int(ele) > num for ele in eles1) and all(name in ele for ele in eles2)
        assert not module.has_fail_message()

    @allure.story("查询模块名称包含计划或排序≥4")
    # @pytest.mark.run(order=1)
    def test_module_selectsuccess3(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        name = "计划"
        num = 4
        # 点击查询
        module.click_all_button("查询")
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
        module.click_button('//div[text()="模块名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        module.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        module.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        module.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        module.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        module.click_button('//div[text()="排序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        module.click_button('//div[text()="≥" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值0
        module.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            num,
        )
        # 点击（
        module.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        module.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        module.click_select_button2()
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
        module.right_refresh('模块管理')
        assert not module.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("过滤查组件名称成功")
    # @pytest.mark.run(order=1)
    def test_module_select1(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.wait_for_loading_to_disappear()
        name = "计划"
        module.enter_texts('//div[div[span[text()=" 模块名称"]]]//input', name)
        sleep(2)
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        list_ = [ele.text for ele in eles]
        module.right_refresh('模块管理')
        assert all(name in text for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not module.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_module_select2(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.wait_for_loading_to_disappear()
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        sleep(1)
        eles = module.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            module.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            module.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        module.click_button('//div[div[span[text()=" 模块代码"]]]//input')
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        module.right_refresh('模块管理')
        assert len(eles) == 0
        assert not module.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_module_select3(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.wait_for_loading_to_disappear()
        name = "Co"
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        module.hover("包含")
        sleep(1)
        module.select_input_module(name)
        sleep(1)
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        module.right_refresh('模块管理')
        assert all(name in text for text in list_)
        assert not module.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_module_select4(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "Plan"
        module.wait_for_loading_to_disappear()
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        module.hover("符合开头")
        sleep(1)
        module.select_input_module(name)
        sleep(1)
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        module.right_refresh('模块管理')
        assert len(list_) > 0
        assert all(str(item).startswith(name) for item in list_)
        assert not module.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_module_select5(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.wait_for_loading_to_disappear()
        name = "t"
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        module.hover("符合结尾")
        sleep(1)
        module.select_input_module(name)
        sleep(1)
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        module.right_refresh('模块管理')
        assert all(str(item).endswith(name) for item in list_)
        assert not module.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_module_clear(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.wait_for_loading_to_disappear()
        sleep(1)
        name = "3"
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        module.hover("包含")
        sleep(1)
        module.select_input_module(name)
        sleep(1)
        module.click_button('//div[div[span[text()=" 模块代码"]]]/div[3]//i')
        module.hover("清除所有筛选条件")
        sleep(1)
        ele = module.get_find_element_xpath('//div[div[span[text()=" 模块代码"]]]//i[@class="vxe-icon-funnel suffixIcon"]').get_attribute(
            "class")
        module.right_refresh('模块管理')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not module.has_fail_message()

    @allure.story("设置菜单,显示模块显示应用成功")
    # @pytest.mark.run(order=1)
    def test_module_setmenu1(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        apps = AppsPage(driver)
        date_driver = DateDriver()
        role = RolePage(driver)
        # 新增菜单
        name = "1新增菜单"
        sleep(1)
        module.click_button(f'(//span[text()="菜单组件"])[1]')
        module.wait_for_loading_to_disappear()
        module.select_input_menu(name)
        sleep(1)
        ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        if len(ele) == 0:
            module.click_all_button("新增")
            module.enter_texts('//div[span[text()=" 组件代码 "]]/following-sibling::div//input', name)
            module.enter_texts('//div[span[text()=" 组件名称 "]]/following-sibling::div//input', name)
            module.click_button('//div[span[text()=" 图标 "]]/following-sibling::div//i')
            module.click_button('//div[div[text()="请选择图标"]]/following-sibling::div//div[@class="flex-wrap"]/div')
            sleep(0.5)
            module.click_confirm()
            message = module.get_find_message()
            module.wait_for_loading_to_disappear()
            module.select_input_menu(name)
            sleep(1)
            assert message == "新增成功！"
        eles = module.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        assert eles == name

        # 编辑模块
        module.click_button(f'(//span[text()="模块管理"])[1]')
        module.wait_for_loading_to_disappear()
        module.select_input_module('ABCDAA')
        sleep(1)
        module.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[text()="ABCDAA"]')
        sleep(1)
        module.click_all_button("编辑")
        module.click_button('//div[span[text()=" 组件代码 "]]/following-sibling::div//i')
        module.wait_for_loading_to_disappear()
        module.enter_texts('(//div[div[span[text()=" 组件代码"]]]//input)[last()]', name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        sleep(3)
        module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        module.get_find_message()
        module.wait_for_loading_to_disappear()
        module.select_input_menu(name)
        ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[7]//span[text()="{name}"]')
        assert len(ele) == 1

        # 新增应用
        module.click_button(f'(//span[text()="应用管理"])[1]')
        apps.wait_for_loading_to_disappear()
        name = "1新增应用"
        apps.select_input(name)
        ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        if len(ele) == 0:
            module.click_all_button("新增")
            sleep(1)
            xpath_list = [
                '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
                '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
                '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
                '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
                '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
            ]
            add.batch_modify_input(xpath_list[:2], name)
            apps.click_button(xpath_list[2])
            apps.click_button('//li[text()="ABCDAA"]')

            apps.click_button(xpath_list[3])
            apps.click_button('(//div[@class="flex-wrap"]/div[1])[last()]')

            apps.enter_texts(xpath_list[4], "1")
            apps.click_save_button()
            message = apps.get_find_message()
            apps.click_apps_button()
            apps.select_input(name)
            sleep(1)
            assert message == "新增成功！"
        ele = apps.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[2]').text
        assert ele == name

        # 应用添加按钮成功
        module.click_button(f'//table[@class="vxe-table--body"]//tr[1]/td[2]')
        module.click_all_button("按钮管理")
        module.wait_for_loading_to_disappear()
        for row in [1, 2]:
            xpath = f'//table[@class="vxe-table--body"]//tr[{row}]/td[2]//span[contains(@class,"vxe-cell--checkbox")]'
            element = module.get_find_element_xpath(xpath)
            if 'is--checked' not in element.get_attribute("class"):
                element.click()
        row_values = [(1, "1"), (2, "2")]

        for row_num, value in row_values:
            module.enter_texts(f'//table[@class="vxe-table--body"]//tr[{row_num}]/td[4]//input', value)
            module.enter_texts(f'//table[@class="vxe-table--body"]//tr[{row_num}]/td[5]//input', value)
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = module.get_find_message()
        assert message == "保存成功"

        # 设置权限成功
        role.click_button(f'(//span[text()="角色管理"])[1]')
        role.wait_for_loading_to_disappear()
        role.enter_texts('//div[div[p[text()="角色代码"]]]//input', 'admin')
        role.enter_texts('//div[div[p[text()="计划单元名称"]]]//input', date_driver.planning)
        sleep(1)
        role.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[text()="admin"]')
        sleep(1)
        role.click_all_button("编辑")
        sleep(1)
        role.enter_texts('//input[@placeholder="请输入关键字筛选"]', 'ABCDAA')
        element = role.get_find_element_xpath('//div[@class="ivu-tree"]//li[1]/label')
        # 检查是否包含指定类
        if 'ivu-checkbox-wrapper-checked' not in element.get_attribute("class"):
            element.click()
        role.click_all_button("保存")
        message = role.get_find_message()
        assert message == "保存成功"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        list_ = ["1新增菜单", "ABCDAA", "1新增应用"]
        for v in list_:
            module.click_button(f'(//span[text()="{v}"])[1]')
        ele = module.finds_elements(By.XPATH,
                                  '//div[@class="ivu-modal-body"]//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not module.has_fail_message()

    @allure.story("添加模块在同一个菜单")
    # @pytest.mark.run(order=1)
    def test_module_setmenu2(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        apps = AppsPage(driver)
        date_driver = DateDriver()
        role = RolePage(driver)
        # 新增模块
        module.click_button('//div[@class="labelTitle"][text()=" 模块管理 "]')
        module.wait_for_loading_to_disappear()
        name = 'ACBDDD'
        menu_name = "1新增菜单"
        sleep(1)
        module.select_input_module(name)
        ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        if len(ele) == 0:
            module.click_all_button("新增")
            xpath_list = [
                '//div[span[text()=" 模块代码 "]]/following-sibling::div//input',
                '//div[span[text()=" 模块名称 "]]/following-sibling::div//input',
                '//div[span[text()=" 图标 "]]/following-sibling::div//i',
                '(//div[@class="flex-wrap"]/div[1])[last()]',
                '//div[span[text()=" 组件代码 "]]/following-sibling::div//i'
            ]
            add.batch_modify_input(xpath_list[:2], name)
            module.click_button(xpath_list[2])
            module.click_button(xpath_list[3])
            module.click_button(xpath_list[4])
            module.wait_for_loading_to_disappear()
            module.enter_texts('(//div[div[span[text()=" 组件代码"]]]//input)[last()]', menu_name)
            module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{menu_name}"]')
            module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
            sleep(3)
            module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
            message = module.get_find_message()
            module.wait_for_loading_to_disappear()
            module.select_input_module(name)
            ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
            assert message == "新增成功！"
        assert len(ele) == 1
        # 新增应用
        module.click_button(f'(//span[text()="应用管理"])[1]')
        module.right_refresh('应用管理')
        name = "1新增应用2"
        apps.select_input(name)
        ele = module.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        if len(ele) == 0:
            module.click_all_button("新增")
            sleep(1)
            xpath_list = [
                '//div[@class="d-flex"]/div[label[text()="应用代码"]]//input',
                '//div[@class="d-flex"]/div[label[text()="应用名称"]]//input',
                '//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]',
                '//div[@class="d-flex"]/div[label[text()="图标"]]//i[contains(@class,"ivu-icon")]',
                '//div[@class="d-flex"]/div[label[text()="排序"]]//input',
            ]
            add.batch_modify_input(xpath_list[:2], name)
            apps.click_button(xpath_list[2])
            apps.click_button('//li[text()="ACBDDD"]')

            apps.click_button(xpath_list[3])
            apps.click_button('(//div[@class="flex-wrap"]/div[1])[last()]')

            apps.enter_texts(xpath_list[4], "1")
            apps.click_save_button()
            message = apps.get_find_message()
            apps.click_apps_button()
            apps.select_input(name)
            sleep(1)
            assert message == "新增成功！"
        ele = apps.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]').text
        assert ele == name
        # 应用添加按钮成功
        module.click_button(f'//table[@class="vxe-table--body"]//tr[1]/td[2]')
        module.click_all_button("按钮管理")
        module.wait_for_loading_to_disappear()
        for row in [1, 2]:
            xpath = f'//table[@class="vxe-table--body"]//tr[{row}]/td[2]//span[contains(@class,"vxe-cell--checkbox")]'
            element = module.get_find_element_xpath(xpath)
            if 'is--checked' not in element.get_attribute("class"):
                element.click()
        row_values = [(1, "1"), (2, "2")]

        for row_num, value in row_values:
            module.enter_texts(f'//table[@class="vxe-table--body"]//tr[{row_num}]/td[4]//input', value)
            module.enter_texts(f'//table[@class="vxe-table--body"]//tr[{row_num}]/td[5]//input', value)
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = module.get_find_message()
        assert message == "保存成功"

        # 设置权限成功
        role.click_button(f'(//span[text()="角色管理"])[1]')
        role.wait_for_loading_to_disappear()
        role.right_refresh()
        role.enter_texts('//div[div[p[text()="角色代码"]]]//input', 'admin')
        role.enter_texts('//div[div[p[text()="计划单元名称"]]]//input', date_driver.planning)
        sleep(1)
        role.click_button('//table[@class="vxe-table--body"]//tr/td[2]//span[text()="admin"]')
        sleep(1)
        role.click_all_button("编辑")
        sleep(1)
        role.enter_texts('//input[@placeholder="请输入关键字筛选"]', 'ACBDDD')
        element = role.get_find_element_xpath('//div[@class="ivu-tree"]//li[1]/label')
        # 检查是否包含指定类
        if 'ivu-checkbox-wrapper-checked' not in element.get_attribute("class"):
            element.click()
        role.click_all_button("保存")
        message = role.get_find_message()
        assert message == "保存成功"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        list_ = ["1新增菜单", "ACBDDD", "1新增应用2"]
        for v in list_:
            module.click_button(f'(//span[text()="{v}"])[1]')
        ele = module.finds_elements(By.XPATH,
                                    '//div[@class="ivu-modal-body"]//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not module.has_fail_message()

    @allure.story("设置不显示菜单成功")
    # @pytest.mark.run(order=1)
    def test_module_menushow(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        driver = login_to_module  # WebDriver 实例
        add = AddsPages(driver)
        apps = AppsPage(driver)
        date_driver = DateDriver()
        role = RolePage(driver)

        module.click_button('//div[@class="labelTitle"][text()=" 菜单组件 "]')
        menu_name = "1新增菜单"
        module.wait_for_loading_to_disappear()
        sleep(1)
        module.select_input_menu(menu_name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{menu_name}"]')
        module.click_all_button("编辑")
        sleep(1)
        ele = module.get_find_element_xpath('//div[span[text()=" 是否显示 "]]/following-sibling::label//input').is_selected()
        if ele:
            module.click_button('//div[span[text()=" 是否显示 "]]/following-sibling::label/span')
            module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
            message = module.get_find_message()
            assert message == "编辑成功！"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        ele = module.finds_elements(By.XPATH, f'//div[@class="listDivCon"]/div[span[text()="{menu_name}"]]')
        assert len(ele) == 0
        assert not module.has_fail_message()

    @allure.story("设置不显示模块成功")
    # @pytest.mark.run(order=1)
    def test_module_moduleshow(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        add = AddsPages(driver)
        date_driver = DateDriver()
        role = RolePage(driver)
        # 显示菜单
        module.click_button('//div[@class="labelTitle"][text()=" 菜单组件 "]')
        menu_name = "1新增菜单"
        module.wait_for_loading_to_disappear()
        sleep(1)
        module.select_input_menu(menu_name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{menu_name}"]')
        module.click_all_button("编辑")
        ele = module.get_find_element_xpath('//div[span[text()=" 是否显示 "]]/following-sibling::label//input').is_selected()
        if not ele:
            module.click_button('//div[span[text()=" 是否显示 "]]/following-sibling::label/span')
            module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
            message = module.get_find_message()
            assert message == "编辑成功！"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        ele = module.finds_elements(By.XPATH, f'//div[@class="listDivCon"]/div[span[text()="{menu_name}"]]')
        assert len(ele) == 1

        module.click_button('(//span[text()="模块管理"])[1]')
        name = "ABCDAA"
        module.wait_for_loading_to_disappear()
        sleep(1)
        module.select_input_module(name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        module.click_all_button("编辑")
        ele = module.get_find_element_xpath('//div[span[text()=" 显示模块 "]]/following-sibling::label//input').is_selected()
        if ele:
            module.click_button('//div[span[text()=" 显示模块 "]]/following-sibling::label/span')
            module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
            message = module.get_find_message()
            assert message == "编辑成功！"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        module.click_button(f'(//span[text()="{menu_name}"])[1]')
        ele = module.finds_elements(By.XPATH, f'//div[@class="newPageMenu"]/ul/li//span[text()="{name}"]')
        assert len(ele) == 0
        assert not module.has_fail_message()

    @allure.story("设置模块排序成功")
    # @pytest.mark.run(order=1)
    def test_module_sort1(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        name = "ABCDAA"
        menu_name = "1新增菜单"
        module.click_button('//div[@class="labelTitle"][text()=" 模块管理 "]')
        module.wait_for_loading_to_disappear()
        sleep(1)
        module.select_input_module(name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        module.click_all_button("编辑")
        ele = module.get_find_element_xpath('//div[span[text()=" 显示模块 "]]/following-sibling::label//input').is_selected()
        if not ele:
            module.click_button('//div[span[text()=" 显示模块 "]]/following-sibling::label/span')

        module.enter_texts('//div[span[text()=" 排序 "]]/following-sibling::div//input', '2')
        module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        message = module.get_find_message()
        assert message == "编辑成功！"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        module.click_button(f'(//span[text()="{menu_name}"])[1]')
        ele = module.finds_elements(By.XPATH, f'//div[@class="newPageMenu"]/ul/li[2]//span[text()="{name}"]')
        assert len(ele) == 1
        assert not module.has_fail_message()

    @allure.story("设置菜单排序成功")
    # @pytest.mark.run(order=1)
    def test_module_sort2(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        menu_name = "1新增菜单"
        module.click_button('(//span[text()="系统管理"])[1]')
        module.click_button('(//span[text()="菜单组件"])[1]')
        module.wait_for_loading_to_disappear()
        sleep(1)
        module.select_input_menu(menu_name)
        module.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{menu_name}"]')
        module.click_all_button("编辑")

        module.enter_texts('//div[span[text()=" 排序 "]]/following-sibling::div//input', '1000')
        module.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[last()]')
        message = module.get_find_message()
        assert message == "编辑成功！"
        driver.refresh()
        module.wait_for_loading_to_disappear()
        ele = module.finds_elements(By.XPATH, f'//div[@class="listDivCon"]/div[last()][span[text()="{menu_name}"]]')
        assert len(ele) == 1
        assert not module.has_fail_message()

    @allure.story("设置2个应用在同一个模块下")
    # @pytest.mark.run(order=1)
    def test_module_appmodule(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        apps = AppsPage(driver)
        app_name = "1新增应用2"
        apps.click_button('(//span[text()="应用管理"])[1]')
        apps.wait_for_loading_to_disappear()
        sleep(1)
        apps.select_input(app_name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{app_name}"]')
        apps.click_all_button("编辑")

        apps.click_button('//div[@class="d-flex"]/div[label[text()="模块名称"]]//input[@type="text"]')
        apps.click_button('//li[text()="ABCDAA"]')

        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        assert message == "编辑成功！"
        driver.refresh()
        apps.wait_for_loading_to_disappear()
        apps.click_button(f'(//span[text()="1新增菜单"])[1]')
        apps.click_button(f'(//span[text()="ABCDAA"])[1]')
        eles = apps.finds_elements(By.XPATH, '//span[text()="ABCDAA"]/ancestor::li[1]/ul//span[@class="menuItemSpan"]')
        assert len(eles) == 2
        assert not apps.has_fail_message()

    @allure.story("设置不显示菜单成功")
    # @pytest.mark.run(order=1)
    def test_module_appshow(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        apps = AppsPage(driver)
        app_name = "1新增应用"
        apps.select_input(app_name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{app_name}"]')
        apps.click_all_button("编辑")

        ele = module.get_find_element_xpath('//div[@class="d-flex"]/div[label[text()="显示菜单"]]/div/label/span').get_attribute("class")
        if 'ivu-checkbox-checked' in ele:
            module.click_button('//div[@class="d-flex"]/div[label[text()="显示菜单"]]/div/label/span')

        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        assert message == "编辑成功！"
        driver.refresh()
        apps.wait_for_loading_to_disappear()
        apps.click_button(f'(//span[text()="1新增菜单"])[1]')
        apps.click_button(f'(//span[text()="ABCDAA"])[1]')
        eles = apps.finds_elements(By.XPATH, '//span[text()="ABCDAA"]/ancestor::li[1]/ul//span[@class="menuItemSpan"]')
        ele = apps.finds_elements(By.XPATH, f'//span[@class="menuItemSpan"][text()="{app_name}"]')
        assert len(eles) == 1 and len(ele) == 0
        assert not apps.has_fail_message()

    @allure.story("设置菜单排序成功")
    # @pytest.mark.run(order=1)
    def test_module_appsort(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        apps = AppsPage(driver)
        app_name = "1新增应用"
        apps.select_input(app_name)
        apps.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{app_name}"]')
        apps.click_all_button("编辑")

        ele = module.get_find_element_xpath(
            '//div[@class="d-flex"]/div[label[text()="显示菜单"]]/div/label/span').get_attribute("class")
        if 'ivu-checkbox-checked' not in ele:
            module.click_button('//div[@class="d-flex"]/div[label[text()="显示菜单"]]/div/label/span')
        apps.enter_texts('//div[@class="d-flex"]/div[label[text()="排序"]]//input', '1000')

        apps.click_save_button()
        message = apps.get_find_message()
        apps.click_apps_button()
        assert message == "编辑成功！"
        driver.refresh()
        apps.wait_for_loading_to_disappear()
        apps.click_button(f'(//span[text()="1新增菜单"])[1]')
        ele = apps.get_find_element_xpath('(//span[text()="ABCDAA"])[1]/ancestor::li[1]').get_attribute('aria-expanded')
        if ele == 'false':
            apps.click_button(f'(//span[text()="ABCDAA"])[1]')
        eles = apps.get_find_element_xpath('(//span[text()="ABCDAA"]/ancestor::li[1]/ul//span[@class="menuItemSpan"])[2]').get_attribute('innerText')
        assert eles == app_name
        assert not apps.has_fail_message()

    @allure.story("删除菜单，删除模块，删除应用成功")
    # @pytest.mark.run(order=1)
    def test_module_delAll(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        apps = AppsPage(driver)
        module.click_button('(//span[text()="系统管理"])[1]')
        sleep(1)
        ele = apps.get_find_element_xpath('(//span[text()="系统设置"])[1]/ancestor::li[1]').get_attribute('aria-expanded')
        if ele != 'true':
            apps.click_button('(//span[text()="系统设置"])[1]')
        module.click_button('(//span[text()="菜单组件"])[1]')
        value = ['1新增菜单']
        module.del_all(xpath='//div[div[span[text()=" 组件代码"]]]/div[3]//input', value=value)
        module.right_refresh("菜单组件")
        sleep(1)
        itemdata = [
            driver.find_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{v}"]')
            for v in value[:1]
        ]
        assert all(len(elements) == 0 for elements in itemdata)

        apps.click_button('(//span[text()="应用管理"])[1]')
        value = ['1新增应用', '1新增应用2']
        apps.del_all(xpath='//div[p[text()="应用代码"]]/following-sibling::div//input', value=value)
        apps.right_refresh()
        sleep(1)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:2]
        ]
        assert all(len(elements) == 0 for elements in itemdata)

        module.click_button('(//span[text()="模块管理"])[1]')
        module.wait_for_loading_to_disappear()
        value = ['ABCDAA', 'ACBDDD']
        module.del_all(xpath='//div[div[span[text()=" 模块代码"]]]//input', value=value)
        module.right_refresh("模块管理")
        sleep(1)
        itemdata = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:2]
        ]
        assert all(len(elements) == 0 for elements in itemdata)
        assert not module.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_module_ctrlIrepeat(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = module.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = module.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
        module.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not module.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_module_ctrlI(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        module.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        module.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = module.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        module.get_find_message()
        module.select_input_module('1没有数据添加')
        ele2 = module.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not module.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_module_ctrlM(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        module.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        module.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[3])[2]//input', '1没有数据修改')
        ele1 = module.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[3])[2]//input').get_attribute(
            "value")
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        module.get_find_message()
        module.enter_texts('//div[div[span[text()=" 模块名称"]]]//input', '1没有数据修改')
        ele2 = module.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[3])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据修改'
        assert not module.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_module_shiftdel(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        button = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        button.right_refresh('模块管理')
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]']
        button.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = button.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        button.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        button.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加1')
        sleep(2)
        button.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        button.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        button.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据添加12')
        sleep(1)
        ele1 = button.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
        ele2 = button.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
        button.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        button.get_find_message()
        button.wait_for_loading_to_disappear()
        button.select_input_module('1没有数据添加1')
        ele11 = button.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        ele22 = button.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        assert not button.has_fail_message()
        button.select_input_module('1没有数据添加')
        before_data = button.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[1]']
        button.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = button.get_find_element_xpath(elements[2])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        button.click_all_button('删除')
        button.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = button.get_find_message()
        button.wait_for_loading_to_disappear()
        after_data = button.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not button.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_module_shiftdel(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.right_refresh('模块管理')
        module.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        module.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        module.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加1')
        sleep(1)
        ele1 = module.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        module.get_find_message()
        module.select_input_module('1没有数据添加1')
        ele2 = module.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加1'
        assert not module.has_fail_message()
        module.select_input_module('1没有数据添加')
        before_data = module.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
                    '//table[@class="vxe-table--body"]//tr[2]//td[1]']
        module.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = module.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        module.click_all_button('删除')
        module.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = module.get_find_message()
        module.wait_for_loading_to_disappear()
        after_data = module.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 2, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not module.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_module_ctrlC(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        module.right_refresh('模块管理')
        module.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = module.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        module.click_button('//div[div[span[text()=" 模块代码"]]]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = module.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        module.right_refresh('模块管理')
        assert all(before_data in ele for ele in eles)
        assert not module.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_module_shift(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
                    '//table[@class="vxe-table--body"]//tr[2]//td[1]']
        module.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = module.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = module.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not module.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_module_ctrls(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage
        elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
                    '//table[@class="vxe-table--body"]//tr[2]//td[1]']
        module.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = module.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = module.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        module.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = module.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not module.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_module_delsuccess(self, login_to_module):
        driver = login_to_module  # WebDriver 实例
        module = ExpressionPage(driver)  # 用 driver 初始化 ExpressionPage

        module.wait_for_loading_to_disappear()
        layout = "测试布局A"

        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = module.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = module.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）

        module.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        for i in range(1, 10):
            try:
                print(f"尝试点击第 {i} 个删除布局按钮...")

                # 构建XPath，注意索引从1开始
                xpath = f'(//li[text()="删除布局"])[{index + i}]'
                module.click_button(xpath)
                break
            except Exception as e:
                print(f"⚠️ 点击第 {i} 个按钮时出错: {e}")
        sleep(2)
        # 点击确认删除的按钮
        module.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        module.wait_for_loading_to_disappear()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not module.has_fail_message()