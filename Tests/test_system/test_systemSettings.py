import logging
import os
from datetime import datetime
from time import sleep

import allure
import pyautogui
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.systemPage.systemSettings_page import SystemSettingsPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_systemSettings():
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
        list_ = ["系统管理", "系统设置", "系统标识设置"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("系统标识设置页用例")
@pytest.mark.run(order=211)
class TestSystemSettingsPage:

    @allure.story("设置商标名称成功")
    # @pytest.mark.run(order=1)
    def test_systemSettings_trademark1(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        text = '测试商标'
        settings.enter_texts('//div[p[text()=" 商标名称: "]]//input', text)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.get_find_element_xpath('//div[@class="copyRight"]').get_attribute('innerText')
        settings.login()
        assert maeessage == "保存成功"
        assert text in ele
        assert not settings.has_fail_message()

    @allure.story("商标名称不填默认为 Elligent SCP")
    # @pytest.mark.run(order=1)
    def test_systemSettings_trademark2(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        text = 'Elligent SCP'
        ele = settings.get_find_element_xpath('//div[p[text()=" 商标名称: "]]//input')
        ele.send_keys(Keys.CONTROL + "a")
        ele.send_keys(Keys.DELETE)
        sleep(1)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.get_find_element_xpath('//div[@class="copyRight"]').get_attribute('innerText')
        settings.login()
        assert maeessage == "保存成功"
        assert text in ele
        assert not settings.has_fail_message()

    @allure.story("LOGO显示方式为文字")
    # @pytest.mark.run(order=1)
    def test_systemSettings_logo1(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" LOGO显示方式: "]]//span')
        settings.click_button('//ul/li[text()="仅显示文字"]')
        settings.click_save_button()
        maeessage = settings.get_find_message()
        eles = settings.finds_elements(By.XPATH, '//div[@class="navTop"]/div[1]/div')
        assert maeessage == "保存成功" and len(eles) == 1
        assert not settings.has_fail_message()

    @allure.story("上传成功系统图标成功")
    # @pytest.mark.run(order=1)
    def test_systemSettings_upload(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" 系统图标: "]]//i')
        # 清理未完成下载
        download_path = os.path.join(os.path.dirname(__file__), "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)

        # 准备上传文件路径
        upload_file = os.path.join(download_path, "WPS图片.png")
        assert os.path.exists(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        settings.upload_file(upload_file, 1)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.finds_elements(By.XPATH, '//div[p[text()=" 系统图标: "]]/div//img')
        # 3. 等待上传完成并断言结果
        assert maeessage == "保存成功" and len(ele) == 1
        assert not settings.has_fail_message()
        pyautogui.press('esc')

    @allure.story("LOGO显示方式为仅显示图标")
    # @pytest.mark.run(order=1)
    def test_systemSettings_logo2(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" LOGO显示方式: "]]//span')
        settings.click_button('//ul/li[text()="仅显示图标"]')
        settings.click_save_button()
        maeessage = settings.finds_elements(By.XPATH, '//div[@class="el-message el-message--success"]/p[text()="保存成功"]')
        eles = settings.finds_elements(By.XPATH, '//div[@class="navTop"]/div[1]/span')
        assert len(maeessage) == 1
        assert len(eles) == 0
        assert not settings.has_fail_message()

    @allure.story("删除系统图标成功")
    # @pytest.mark.run(order=1)
    def test_systemSettings_del1(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        sleep(2)
        name = "系统图标"
        settings.del_icon(name)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.finds_elements(By.XPATH, '//div[p[text()=" 系统图标: "]]/div//img')
        assert maeessage == "保存成功" and len(ele) == 0
        assert not settings.has_fail_message()

    @allure.story("LOGO显示方式为图标+文字")
    # @pytest.mark.run(order=1)
    def test_systemSettings_logo3(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" LOGO显示方式: "]]//span')
        settings.click_button('//ul/li[text()="图标+文字"]')
        settings.click_save_button()
        maeessage = settings.get_find_message()
        eles = settings.finds_elements(By.XPATH, '//div[@class="navTop"]/div[1]/div')
        assert maeessage == "保存成功" and len(eles) == 2
        assert not settings.has_fail_message()

    @allure.story("登录页不显示LOGO")
    # @pytest.mark.run(order=1)
    def test_systemSettings_logo4(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        cla = settings.get_find_element_xpath('//div[p[text()=" 登录页显示系统Logo: "]]/span').get_attribute("class")
        if 'ivu-switch-checked' in cla:
            settings.click_button('//div[p[text()=" 登录页显示系统Logo: "]]/span')
        sleep(2)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.get_find_element_xpath('//div[@id="app"]/div/div[@class="logoHead"]').get_attribute("style")
        settings.login()
        assert maeessage == "保存成功" and ele == "display: none;"
        assert not settings.has_fail_message()

    @allure.story("登录页显示LOGO")
    # @pytest.mark.run(order=1)
    def test_systemSettings_logo5(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        cla = settings.get_find_element_xpath('//div[p[text()=" 登录页显示系统Logo: "]]/span').get_attribute("class")
        if 'ivu-switch-checked' not in cla:
            settings.click_button('//div[p[text()=" 登录页显示系统Logo: "]]/span')
        sleep(2)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.get_find_element_xpath('//div[@id="app"]/div/div[@class="logoHead"]').get_attribute("style")
        settings.login()
        assert maeessage == "保存成功" and ele == ""
        assert not settings.has_fail_message()

    @allure.story("设置成功登录背景图成功")
    # @pytest.mark.run(order=1)
    def test_systemSettings_loginicon(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" 登录背景图: "]]//i')
        # 清理未完成下载
        download_path = os.path.join(os.path.dirname(__file__), "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)

        # 准备上传文件路径
        upload_file = os.path.join(download_path, "WPS图片.png")
        assert os.path.exists(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        settings.upload_file(upload_file, 2)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.finds_elements(By.XPATH, '//div[p[text()=" 登录背景图: "]]/div//img')

        settings.log_out()
        img = settings.finds_elements(By.XPATH, '//div[@id="app"]/div/div[@class="view-left"]/div[1]/div')
        pyautogui.press('esc')
        settings.login()
        assert maeessage == "保存成功" and len(ele) == 1
        assert len(img) == 1
        assert not settings.has_fail_message()

    @allure.story("恢复登录背景图为默认")
    # @pytest.mark.run(order=1)
    def test_systemSettings_del2(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        sleep(2)
        name = "登录背景图"
        settings.del_icon(name)
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.finds_elements(By.XPATH, '//div[p[text()=" 登录背景图: "]]/div//img')
        settings.log_out()
        img = settings.finds_elements(By.XPATH, '//div[@id="app"]/div/div[@class="view-left"]/div[1]/div')
        settings.login()
        assert maeessage == "保存成功" and len(ele) == 0
        assert len(img) == 2
        assert not settings.has_fail_message()

    @allure.story("设置平台登录为全部登录")
    # @pytest.mark.run(order=1)
    def test_systemSettings_login1(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" 登录方式: "]]//span')
        settings.click_button('//ul/li[text()="全部"]')
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.finds_elements(By.XPATH, '//div[@class="LoginTypeTab"]//li[text()=" 域账号登录 "]')
        settings.login()
        assert maeessage == "保存成功" and len(ele) == 1
        assert not settings.has_fail_message()

    @allure.story("设置登录方式只能平台账户登录")
    # @pytest.mark.run(order=1)
    def test_systemSettings_login2(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.click_button('//div[p[text()=" 登录方式: "]]//span')
        settings.click_button('//ul/li[text()="平台账户"]')
        settings.click_save_button()
        maeessage = settings.get_find_message()
        settings.log_out()
        ele = settings.finds_elements(By.XPATH, '//div[@class="LoginTypeTab"]//li[text()=" 域账号登录 "]')
        settings.login()
        assert maeessage == "保存成功" and len(ele) == 0
        assert not settings.has_fail_message()

    @allure.story("校验数字文本框最大只能输入9999999999")
    # @pytest.mark.run(order=1)
    def test_systemSettings_inputnum1(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.enter_texts('//div[p[text()=" 禁用不登录账户（天）: "]]//input', "e./,124ds.jd.fvwq324444443521244444444tgg77飞435535353535erq")
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.get_find_element_xpath('//div[p[text()=" 禁用不登录账户（天）: "]]//input').get_attribute("value")
        assert maeessage == "保存成功" and ele == '9999999999'
        ele = settings.get_find_element_xpath('//div[p[text()=" 禁用不登录账户（天）: "]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        settings.enter_texts('//div[p[text()=" 禁用不登录账户（天）: "]]//input', "0")
        settings.click_save_button()
        maeessage = settings.get_find_message()
        assert not settings.has_fail_message()

    @allure.story("校验修改登录密码最少位数数字文本框最大只能输入30")
    # @pytest.mark.run(order=1)
    def test_systemSettings_inputnum2(self, login_to_systemSettings):
        driver = login_to_systemSettings  # WebDriver 实例
        settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
        settings.enter_texts('//div[p[text()=" 修改登录密码最少位数: "]]//input',
                             "333333333333333333")
        settings.click_save_button()
        maeessage = settings.get_find_message()
        ele = settings.get_find_element_xpath('//div[p[text()=" 修改登录密码最少位数: "]]//input').get_attribute("value")
        assert maeessage == "保存成功" and ele == '30'
        ele = settings.get_find_element_xpath('//div[p[text()=" 修改登录密码最少位数: "]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        settings.enter_texts('//div[p[text()=" 修改登录密码最少位数: "]]//input', "8")
        settings.click_save_button()
        maeessage = settings.get_find_message()
        assert not settings.has_fail_message()

    # @allure.story("平台设置数字文本框做校验")
    # # @pytest.mark.run(order=1)
    # def test_systemSettings_inputnum3(self, login_to_systemSettings):
    #     driver = login_to_systemSettings  # WebDriver 实例
    #     settings = SystemSettingsPage(driver)  # 用 driver 初始化 SystemSettingsPage
    #     settings.click_button('//div[text()=" 平台设置 "]')
    #     settings.enter_texts('//div[p[text()=" 数据库命令超时时间 (秒): "]]//input',
    #                          "e./,124ds.jd.fvwq324444443521244444444tgg77飞435535353535erq")
    #     settings.click_save_button()
    #     maeessage = settings.get_find_message()
    #     ele = settings.get_find_element_xpath('//div[p[text()=" 数据库命令超时时间 (秒): "]]//input').get_attribute("value")
    #     assert maeessage == "保存成功" and ele == '9999999999'
    #     ele = settings.get_find_element_xpath('//div[p[text()=" 数据库命令超时时间 (秒): "]]//input')
    #     ele.send_keys(Keys.CONTROL, "a")
    #     ele.send_keys(Keys.DELETE)
    #     settings.enter_texts('//div[p[text()=" 数据库命令超时时间 (秒): "]]//input', "100112")
    #     settings.click_save_button()
    #     maeessage = settings.get_find_message()
    #     assert not settings.has_fail_message()