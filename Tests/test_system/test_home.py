import logging
import random
from datetime import date
from time import sleep

import allure
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.personal_page import PersonalPage
from Pages.systemPage.homepage_page import HomePage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_home():
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
        page.click_button('(//span[text()="系统管理"])[1]')  # 点击系统管理
        page.click_button('(//span[text()="单元设置"])[1]')  # 点击单元设置
        page.click_button('(//span[text()="主页设置"])[1]')  # 点击主页设置
        page.wait_for_el_loading_mask()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("主页设置页用例")
@pytest.mark.run(order=200)
class TestHomePage:

    @allure.story("添加测试模版")
    # @pytest.mark.run(order=1)
    def test_home_save_template_11(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)
        home.click_template()
        ele = home.finds_elements(By.XPATH, '//span[text()=" 初始模版使用 "]')
        if ele:
            xpath = '//span[text()=" 初始模版使用 "]/following-sibling::span[not(contains(@style,"display: none"))]'
            text_ = home.get_find_element_xpath(xpath).get_attribute("innerText")
            if text_ == "加载模板":
                home.click_button(xpath)
                home.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                sleep(1)
        else:
            text = home.click_save_template_button(name="初始模版使用", button="确定")
            assert text == 1
        home.click_button('//div[@class="ivu-tabs-tab" and text()=" 页面设置 "]')
        value = home.get_find_element_xpath(
            '//div[p[text()="关联角色"]]/div//input').get_attribute("value")
        if "admin" not in value:
            home.click_button(
                '//div[p[text()="关联角色"]]//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]')
            home.click_button('//li[text()="admin "]')
            home.click_button(
                '//div[p[text()="关联角色"]]//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]')
        home.clear_all_button("确定")
        home.click_button('//div[text()=" 组件 "]')
        home.drag_component(index="4")
        home.click_save_button()
        message = home.get_find_message()
        assert message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("新增一个组件成功")
    # @pytest.mark.run(order=1)
    def test_home_add_success(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.clear_all_button("确定")
        num = home.drag_component(name="饼图")
        home.click_save_button()
        message = home.get_find_message()
        home.right_refresh()
        div_num = home.count_div_elements()
        assert num == div_num and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("新增全部组件成功")
    # @pytest.mark.run(order=1)
    def test_home_add_all_success(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.clear_all_button("确定")
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)
        num = home.drag_component()
        home.click_save_button()
        message = home.get_find_message()
        home.right_refresh()
        div_num = home.count_div_elements()
        assert num == div_num and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("点击清空全部，点击取消，不会删除组件")
    # @pytest.mark.run(order=1)
    def test_home_clear_all_cancel(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.clear_all_button("取消")
        home.click_save_button()
        message = home.get_find_message()
        home.right_refresh()
        num = home.count_div_elements()
        assert num == 16 and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("清空全部组件成功")
    # @pytest.mark.run(order=1)
    def test_home_clear_all_confirm(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.clear_all_button("确定")
        home.wait_for_el_loading_mask()
        home.click_save_button()
        message = home.get_find_message()
        home.right_refresh()
        num = home.count_div_elements()
        assert num == 0 and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("保存模版,不输入名称，点击确定，弹出提示不允许保存")
    # @pytest.mark.run(order=1)
    def test_home_save_template(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)
        home.clear_all_button("确定")
        home.drag_component(index="2")
        text = home.click_save_template_button(button="确定")
        assert text == "请输入模板名称"
        assert not home.has_fail_message()

    @allure.story("保存模版,点击取消，不会保存模版")
    # @pytest.mark.run(order=1)
    def test_home_save_template_cancel(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)
        home.clear_all_button("确定")
        home.drag_component(index="2")
        text = home.click_save_template_button(name="测试模版cancel", button="取消")
        assert text == 0
        assert not home.has_fail_message()

    @allure.story("保存模版,点击确定，保存模版")
    # @pytest.mark.run(order=1)
    def test_home_save_template_confirm1(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)
        home.clear_all_button("确定")
        home.drag_component(index="2")
        text = home.click_save_template_button(name="测试模版confirm", button="确定")
        home.click_save_button()
        message = home.get_find_message()
        assert text == 1 and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("添加测试模版")
    # @pytest.mark.run(order=1)
    def test_home_save_template_confirm2(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)
        home.clear_all_button("确定")
        home.drag_component(index="4")
        text = home.click_save_template_button(name="测试模版2confirm", button="确定")
        home.click_save_button()
        message = home.get_find_message()
        assert text == 1 and message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("添加模版，重复命名，点击确定，弹出提示不允许保存")
    # @pytest.mark.run(order=1)
    def test_home_add_template_repeat(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.wait_for_el_loading_mask()
        home.click_button('(//div[@class="d-flex m-b-7 toolBar"]//button)[2]')
        home.enter_texts('//div[text()=" 名称 "]/following-sibling::div//input', "测试模版confirm")
        home.click_button(
            f'//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = home.get_error_message()
        assert message == "模板已存在"
        assert not home.has_fail_message()

    @allure.story("切换模版点击取消不会更新模版")
    # @pytest.mark.run(order=1)
    def test_home_switch_template1(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.click_template()
        home.click_button('//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]')
        home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="取消"]')
        home.click_save_button()
        num = home.count_div_elements()
        style = home.get_find_element_xpath('//div[./span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        assert num == 4 and style == "display: none;"
        assert not home.has_fail_message()

    @allure.story("切换模版点击确定不保存，则修改的内容没有保存，并且切换到别的模版上")
    # @pytest.mark.run(order=1)
    def test_home_switch_template2(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.drag_component(name="表格")
        home.click_template()
        home.click_button('//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]')
        home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num1 = home.count_div_elements()
        style = home.get_find_element_xpath(
            '//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        home.click_button('//div[./span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
        home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num2 = home.count_div_elements()
        assert num1 == 2 and num2 == 4 and style == "display: none;"
        assert not home.has_fail_message()

    @allure.story("切换模版点击保存再点击确定，修改的内容保存")
    # @pytest.mark.run(order=1)
    def test_home_switch_template3(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.wait_for_el_loading_mask()
        home.drag_component(name="表格")
        home.click_template()
        home.click_save_button()
        home.get_find_message()
        home.click_button('//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]')
        home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num1 = home.count_div_elements()
        style = home.get_find_element_xpath(
            '//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        home.click_button('//div[./span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
        home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num2 = home.count_div_elements()
        assert num1 == 2 and num2 == 5 and style == "display: none;"
        assert not home.has_fail_message()

    @allure.story("刷新页面，不点击保存，则修改的内容不保存")
    # @pytest.mark.run(order=1)
    def test_home_switch_template4(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage

        home.click_template()
        home.click_button('//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]')
        home.click_button(
            '//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        home.click_button('//div[@class="ivu-tabs-tab"]')
        home.drag_component(name="数字")

        home.right_refresh()
        home.click_button('//button[./span[text()="无需保存"]]')
        home.wait_for_el_loading_mask()
        sleep(1)
        num = home.count_div_elements()
        assert num == 5
        assert not home.has_fail_message()

    @allure.story("刷新页面，点击保存，则修改的内容保存")
    # @pytest.mark.run(order=1)
    def test_home_switch_template5(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage

        home.click_template()
        home.click_button('//div[./span[text()=" 测试模版confirm "]]/span[text()=" 加载模板 "]')
        home.click_button(
            '//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        home.click_button('//div[@class="ivu-tabs-tab"]')
        home.drag_component(name="数字")
        home.right_refresh()
        home.click_button('//button[./span[text()="保存"]]')
        home.wait_for_el_loading_mask()
        home.get_find_message()
        sleep(1)
        num = home.count_div_elements()
        assert num == 3
        assert not home.has_fail_message()

    @allure.story("删除组件成功")
    # @pytest.mark.run(order=1)
    def test_home_delete(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.click_button('//div[@id="homeCanvasBox"]/div[2]')
        home.clear_button("确定")
        home.click_save_button()
        home.wait_for_el_loading_mask()
        home.right_refresh()
        num = home.count_div_elements()
        assert num == 2
        assert not home.has_fail_message()

    @allure.story("正在使用的模版不允许删除")
    # @pytest.mark.run(order=1)
    def test_home_nodelete_template(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        name = "测试模版confirm"
        home.click_template()
        home.wait_for_el_loading_mask()

        # 1️⃣ 悬停模版容器触发图标显示
        container = home.get_find_element_xpath(
            f'//span[text()=" {name} "]/ancestor::div[2]'
        )
        ActionChains(home.driver).move_to_element(container).perform()

        # 2️⃣ 等待删除图标可见
        delete_icon = WebDriverWait(home.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//span[text()=" {name} "]/ancestor::div[2]//i[contains(@class, "el-icon-delete-solid")]'
            ))
        )

        # 3️⃣ 点击删除图标并确认删除操作
        delete_icon.click()

        message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--error"]//p')
            )
        )
        assert message.text == "当前正在使用该模板，不能删除！"
        assert not home.has_fail_message()

    @allure.story("添加关联条件会出现在个人设置中")
    # @pytest.mark.run(order=1)
    def test_home_default_boot1(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        PersonalPage(driver).go_setting_page()
        home.wait_for_el_loading_mask()
        elem1 = len(driver.find_elements(By.XPATH, '//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")]'))
        home.click_button('//div[@class="demo-drawer-footer"]//span[text()="取消"]')
        home.click_template()
        sty = home.get_find_element_xpath(
            '//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        if sty != "display: none;":
            home.click_button('//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
            home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
            home.wait_for_el_loading_mask()
        home.click_button('//div[text()=" 页面设置 "]')
        value = home.get_find_element_xpath(
            '//div[p[text()="关联角色"]]/div//input').get_attribute("value")
        if "admin" in value:
            home.click_save_button()
            home.get_find_message()
            PersonalPage(driver).go_setting_page()
            sleep(3)
            elem2 = len(driver.find_elements(By.XPATH, '//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")]'))
        else:
            home.click_button('//div[p[text()="关联角色"]]//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]')
            home.click_button('//li[text()="admin "]')
            home.click_button(
                '//div[p[text()="关联角色"]]//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]')
            home.click_save_button()
            home.get_find_message()
            PersonalPage(driver).go_setting_page()
            sleep(1)
            after_eles = len(driver.find_elements(By.XPATH, '//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")]'))
            elem2 = (after_eles - 1)
        assert elem1 == elem2
        assert not home.has_fail_message()

    @allure.story("设置该模版为启动模版")
    # @pytest.mark.run(order=1)
    def test_home_default_boot2(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.click_template()
        sty = home.get_find_element_xpath(
            '//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        if sty != "display: none;":
            home.click_button('//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
            home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num = home.count_div_elements()
        home.click_save_button()
        home.get_find_message()
        PersonalPage(driver).go_setting_page()
        home.wait_for_el_loading_mask()
        home.click_button('//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")][last()]')
        home.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]/button')
        home.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        home.click_button('//div[@class="scroll-body"]//div[text()=" 主页 "]')
        sleep(1)
        home.right_refresh(name="主页")
        elem = driver.find_elements(By.XPATH, '//div[@id="homeRenderCanvas"]/div')
        assert (len(elem) - 1) == num
        assert not home.has_fail_message()

    @allure.story("不添加关联条件不会出现在个人设置中")
    # @pytest.mark.run(order=1)
    def test_home_default_boot3(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        PersonalPage(driver).go_setting_page()
        sleep(3)
        elem1 = len(driver.find_elements(By.XPATH, '//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")]'))
        home.click_button('//div[@class="demo-drawer-footer"]//span[text()="取消"]')
        home.click_template()
        sty = home.get_find_element_xpath(
            '//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        if sty != "display: none;":
            home.click_button('//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
            home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        home.click_button('//div[text()=" 页面设置 "]')
        value = home.get_find_element_xpath(
            '//div[p[text()="关联角色"]]/div//input').get_attribute("value")
        home.wait_for_el_loading_mask()
        if "admin" in value:
            home.click_button('//div[p[text()="关联角色"]]//div[span[text()="admin "]]/i')
            elem2 = (elem1 - 1)
        else:
            elem2 = elem1
        home.click_save_button()
        home.get_find_message()
        PersonalPage(driver).go_setting_page()
        sleep(3)
        after_eles = len(driver.find_elements(By.XPATH, '//div[p[text()=" 主页启动模板: "]]/div/div[contains(@class,"demo-upload-list")]'))
        assert elem2 == after_eles
        assert not home.has_fail_message()

    @allure.story("主页模版中没有改模版不会显示该模版")
    # @pytest.mark.run(order=1)
    def test_home_default_boot4(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        home.click_template()
        sty = home.get_find_element_xpath(
            '//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]').get_attribute("style")
        if sty != "display: none;":
            home.click_button('//div[span[text()=" 测试模版2confirm "]]/span[text()=" 加载模板 "]')
            home.click_button('//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        num = home.count_div_elements()
        home.click_save_button()
        home.get_find_message()
        home.click_button('//div[@class="scroll-body"]//div[text()=" 主页 "]')
        sleep(1)
        home.right_refresh(name="主页")
        elem = driver.find_elements(By.XPATH, '//div[@id="homeRenderCanvas"]/div')
        assert (len(elem) - 1) != num
        assert not home.has_fail_message()

    @allure.story("删除测试布局成功")
    # @pytest.mark.run(order=1)
    def test_home_savete(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        name = "初始模版使用"
        home.click_template()
        home.click_button(f'//div[./span[text()=" {name} "]]/span[text()=" 加载模板 "]')
        home.click_button(
            '//div[div[text()="是否加载这个模板？加载后会覆盖当前内容。"]]/following-sibling::div//span[text()="确定"]')
        home.wait_for_el_loading_mask()
        home.click_save_button()
        message = home.get_find_message()
        assert message == "保存成功"
        assert not home.has_fail_message()

    @allure.story("删除测试布局成功")
    # @pytest.mark.run(order=1)
    def test_home_delete_template1(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        name = "测试模版2confirm"
        ele = home.delete_template(name)
        assert ele == 0
        assert not home.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_home_delete_template(self, login_to_home):
        driver = login_to_home  # WebDriver 实例
        home = HomePage(driver)  # 用 driver 初始化 HomePage
        name = "测试模版confirm"
        ele = home.delete_template(name)
        assert ele == 0
        assert not home.has_fail_message()

