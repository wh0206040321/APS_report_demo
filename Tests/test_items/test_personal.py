import logging
from time import sleep

import allure
import pyautogui
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.color import Color
from selenium.common.exceptions import TimeoutException

from Pages.itemsPage.personal_page import PersonalPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture(scope="module")   # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_personal():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        driver = create_driver(date_driver.driver_path)
        shared_data = SharedDataUtil.load_data()
        password = shared_data.get("password")
        driver.implicitly_wait(3)

        # 初始化登录页面
        page = LoginPage(driver)  # 初始化登录页面
        url = date_driver.url
        logging.info(f"[INFO] 正在导航到 URL: {url}")

        # 🔁 添加重试机制（最多 3 次）
        for attempt in range(3):
            try:
                page.navigate_to(url)
                break
            except WebDriverException as e:
                capture_screenshot(driver, f"login_fail_attempt_{attempt + 1}")
                logging.warning(f"第 {attempt + 1} 次导航失败: {e}")
                driver.refresh()
                sleep(date_driver.URL_RETRY_WAIT)
        else:
            logging.error("导航失败多次，中止测试")
            safe_quit(driver)
            raise RuntimeError("无法连接到登录页面")
        page.enter_username(date_driver.username)
        if password is not None:
            page.enter_password(password)
        else:
            page.enter_password(date_driver.password)
        page.select_planning_unit(date_driver.planning)
        page.click_login_button()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("个人设置测试用例")
@pytest.mark.run(order=29)
class TestPersonalPage:
    @allure.story("修改密码不符合标准")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "123", "123"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 密码至少包含大写字母，小写字母，数字，特殊字符中的3类 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "a123", "a123"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 密码至少包含大写字母，小写字母，数字，特殊字符中的3类 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword3(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "AAA123", "AAA123"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 密码至少包含大写字母，小写字母，数字，特殊字符中的3类 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,密码长度最小为8")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword4(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "AAAb123", "AAAb123"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 密码最小长度为8位，最大为30位 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,不能包含特殊字符")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword5(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        text = " 不能包含+: , [ < > ' )  / ，]符号 "
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "Qw12+>3", "Qw12+>3"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, f'//p[text()="{text}"]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,首位字符不允许为空格")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword6(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", " AAAb123", " AAAb123"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 首位字符不允许为空格 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,不允许包含用户名")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword7(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", f"W11{DateDriver.username}", f"W1{DateDriver.username}"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 不允许包含用户名 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,新密码与确认密码不一致")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword8(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", "Qw123456", "Qw123446"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 与新密码保持一致 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("修改密码不符合标准,新密码不能包含旧密码")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword10(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}", f"{DateDriver.password}1", f"{DateDriver.password}1"]
        personal.edit_password(password[0], password[1], password[2])
        ele = driver.find_elements(By.XPATH, '//p[text()=" 新密码不能包含旧密码 "]')
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert len(ele) == 1
        assert not personal.has_fail_message()

    @allure.story("旧密码错误不允许修改")
    # @pytest.mark.run(order=1)
    def test_personal_editpassword11(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        password = [f"{DateDriver.password}1", "Qq123456", "Qq123456"]
        personal.edit_password(password[0], password[1], password[2])
        message = personal.get_error_message()
        personal.click_button('//div[div[text()="修改密码"]]//i[@title="关闭"]')
        assert message == "修改失败"
        assert not personal.has_fail_message()

    # @allure.story("修改密码成功")
    # # @pytest.mark.run(order=1)
    # def test_personal_editpasswordsuccess(self, login_to_personal):
    #     driver = login_to_personal  # WebDriver 实例
    #     personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
    #     newpassword = "Qq123456"
    #     password = [f"{DateDriver.password}", newpassword, newpassword]
    #     personal.edit_password(password[0], password[1], password[2])
    #     message = personal.get_find_message().text
    #     if message == "修改成功":
    #         # 清空之前的共享数据
    #         SharedDataUtil.clear_data()
    #         SharedDataUtil.save_data(
    #             {"password": newpassword}
    #         )
    #         assert message == "修改成功"
    #     else:
    #         assert 1 != 1
    #     assert not personal.has_fail_message()

    # @allure.story("新密码登录成功")
    # # @pytest.mark.run(order=1)
    # def test_personal_loginsuccess1(self, login_to_personal):
    #     driver = login_to_personal  # WebDriver 实例
    #     personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
    #     # 断言登录成功，检查排产单元是否存在
    #     profile_icon = personal.get_find_element(
    #         f'//div[text()=" {DateDriver().planning} "]'
    #     )
    #     assert profile_icon.is_displayed()  # 断言用户头像可见，表明登录成功
    #     assert not personal.has_fail_message()
    #
    # @allure.story("注销成功，使用旧密码登录，登录失败")
    # # @pytest.mark.run(order=1)
    # def test_personal_loginsuccess2(self, login_to_personal):
    #     driver = login_to_personal  # WebDriver 实例
    #     personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
    #     personal.click_button('//div[@class="flex-alignItems-center"]')
    #     personal.click_button('//div[text()=" 注销 "]')
    #     personal.enter_username(f"{DateDriver().username}")  # 输入用户名
    #     personal.enter_password(f"{DateDriver().password}")  # 输入密码
    #     personal.click_button('(//input[@type="text"])[2]')  # 点击下拉框
    #     personal.click_button(f'//li[text()="{DateDriver().planning}"]')  # 点击计划单元
    #     personal.click_button(
    #         '//button[@type="button" and @class="ivu-btn ivu-btn-primary ivu-btn-long ivu-btn-large"]'
    #     )  # 点击登录按钮
    #     element = personal.get_find_element('//div[text()=" 用户名或密码无效 "]')
    #     assert element.text == "用户名或密码无效"
    #     assert not personal.has_fail_message()
    #
    # @allure.story("把密码修改回来")
    # # @pytest.mark.run(order=1)
    # def test_personal_editpasswordback(self, login_to_personal):
    #     driver = login_to_personal  # WebDriver 实例
    #     personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
    #     shared_data = SharedDataUtil.load_data()
    #     password = shared_data.get("password")
    #     pw = [password, f"{DateDriver.password}", f"{DateDriver.password}"]
    #     personal.edit_password(pw[0], pw[1], pw[2])
    #     # 清空之前的共享数据
    #     SharedDataUtil.clear_data()
    #     message = personal.get_find_message().text
    #     assert message == "修改成功"
    #     assert not personal.has_fail_message()

    @allure.story("切换系统格式")
    # @pytest.mark.run(order=1)
    def test_personal_switchformat1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        personal.go_setting_page()
        ele = personal.get_find_element('(//div[@class="w-b-80"])[1]/div[2]').get_attribute("class")
        if "launchTemplate" in ele:
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        else:
            personal.click_button('(//div[@class="w-b-80"])[1]/div[2]')
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')

        message = personal.get_find_message()
        sleep(2)
        format = personal.get_find_element('(//span[text()="需求管理"])[1]').get_attribute("class")
        assert "m-l-2" == format and message == "保存成功"
        assert not personal.has_fail_message()

    @allure.story("切换后重新启动，设置不变，切换回常用风格")
    # @pytest.mark.run(order=1)
    def test_personal_switchformat2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        personal.go_setting_page()
        ele1 = personal.get_find_element('(//div[@class="w-b-80"])[1]/div[1]').get_attribute("class")
        ele2 = personal.get_find_element('(//div[@class="w-b-80"])[1]/div[2]').get_attribute("class")
        if "launchTemplate" in ele1:
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        else:
            personal.click_button('(//div[@class="w-b-80"])[1]/div[1]')
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')

        message = personal.get_find_message()
        sleep(2)
        format = personal.get_find_element('(//span[text()="需求管理" and contains(@class,"listSpan")])').get_attribute("class")
        assert "launchTemplate" in ele2 and "listSpan" in format and message == "保存成功"
        assert not personal.has_fail_message()

    @allure.story("切换系统颜色背景")
    # @pytest.mark.run(order=1)
    def test_personal_switchcolor1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        personal.go_setting_page()
        personal.click_button('(//div[@class="w-b-80"])[2]/div[contains(@style,"background: rgb(33, 113, 15)")]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        sleep(2)
        raw_color = personal.get_find_element('//div[@class="navTop"]').value_of_css_property("background-color")
        parsed_color = Color.from_string(raw_color).rgb
        assert parsed_color == "rgb(33, 113, 15)"
        assert not personal.has_fail_message()

    @allure.story("重新启动设置不变，切换回默认背景颜色")
    # @pytest.mark.run(order=1)
    def test_personal_switchcolor2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        before_raw_color = personal.get_find_element('//div[@class="navTop"]').value_of_css_property("background-color")
        before_parsed_color = Color.from_string(before_raw_color).rgb
        personal.go_setting_page()
        personal.click_button('(//div[@class="w-b-80"])[2]//div[text()=" 默认 "]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        message = personal.get_find_message()
        sleep(1)
        after_raw_color = personal.get_find_element('//div[@class="navTop"]').value_of_css_property("background-color")
        after_parsed_color = Color.from_string(after_raw_color).rgb
        assert message == "保存成功"
        assert before_parsed_color == "rgb(33, 113, 15)" and after_parsed_color == "rgb(50, 66, 85)"
        assert not personal.has_fail_message()

    @allure.story("设置菜单展开方式为悬浮")
    # @pytest.mark.run(order=1)
    def test_personal_expand1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        # 获取设置前宽度
        before_width = driver.find_element(By.XPATH, '//ul[@role="menubar"]').size['width']

        personal.go_setting_page()

        # 获取 “悬浮” 的 checkbox
        checkbox = personal.get_find_element('//label[text()="悬浮"]//input')

        # 如果已经是悬浮状态，为了保证断言逻辑成立，可以先切换为默认展开，然后再切换回悬浮
        if checkbox.is_selected():
            personal.click_button('//label[text()="展开(默认)"]/span')
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
            personal.get_find_message()
            before_element = driver.find_element(By.XPATH, '//ul[@role="menubar"]')
            before_width = before_element.size['width']
            personal.go_setting_page()

        # 设置为默认展开并确认
        personal.click_button('//label[text()="悬浮"]/span')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        message = personal.get_find_message()
        sleep(3)
        after_element = driver.find_element(By.XPATH, '//ul[@role="menubar"]')
        after_width = after_element.size['width']
        assert message == "保存成功"
        assert before_width != after_width and int(before_width) > int(after_width), f"before_width:{before_width},after_width:{after_width}"
        assert not personal.has_fail_message()

    @allure.story("重新启动设置不变,设置菜单展开方式为默认展开")
    # @pytest.mark.run(order=1)
    def test_personal_expand2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        # 获取设置前宽度
        before_width = driver.find_element(By.XPATH, '//ul[@role="menubar"]').size['width']

        personal.go_setting_page()

        # 获取 “展开(默认)” 的 checkbox
        checkbox = personal.get_find_element('//label[text()="展开(默认)"]//input')

        # 如果已经是默认展开状态，为了保证断言逻辑成立，可以先切换为悬浮，然后再切换回默认展开
        if checkbox.is_selected():
            personal.click_button('//label[text()="悬浮"]/span')
            personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
            personal.get_find_message()
            sleep(1)
            before_element = driver.find_element(By.XPATH, '//ul[@role="menubar"]')
            before_width = before_element.size['width']
            personal.go_setting_page()

        # 设置为默认展开并确认
        personal.click_button('//label[text()="展开(默认)"]/span')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        message = personal.get_find_message()
        sleep(1)
        after_element = driver.find_element(By.XPATH, '//ul[@role="menubar"]')
        after_width = after_element.size['width']
        assert message == "保存成功"
        assert before_width != after_width and int(before_width) < int(after_width), f"before_width:{before_width},after_width:{after_width}"
        assert not personal.has_fail_message()

    @allure.story("环境设置为服务器，个人设置本地引擎打开方式ip和web服务禁止选中")
    # @pytest.mark.run(order=1)
    def test_personal_openengine1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        wait = WebDriverWait(driver, 60)
        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="系统设置"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        personal.go_engine_page(name='system_web')

        # 等待 el-loading-spinner 消失
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-spinner"))
        )
        target = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="vue-treeselect__control-arrow-container"]'))
        )
        sleep(3)
        target.click()

        # 等待第一个方案标签可点击后点击选择
        first_option = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@class="vue-treeselect__list"]/div[1]',
                )
            )
        )
        first_option.click()

        # 执行计划
        personal.click_button('//button[@class="m-l-10 ivu-btn ivu-btn-primary"]')

        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )

        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="web服务"]')
        sleep(1)
        ele1 = personal.get_find_element('//li[text()="web服务"]').get_attribute("class")
        ele2 = personal.get_find_element('//li[text()="IP"]').get_attribute("class")
        assert success_element.text == "完成"
        assert "ivu-select-item-disabled" in ele1 and "ivu-select-item-disabled" in ele2
        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="取消"]')
        assert not personal.has_fail_message()

    @allure.story("打开引擎为web服务")
    # @pytest.mark.run(order=1)
    def test_personal_openengine2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        wait = WebDriverWait(driver, 20)
        personal.go_engine_page(name='web')
        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="web服务"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()

        sleep(1)
        ele = driver.find_elements(By.XPATH, '//span[text()=" 引擎启动方式:本地 "]')
        personal.click_button('//button[@class="m-l-10 ivu-btn ivu-btn-primary"]')
        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )
        sleep(2)
        # 等待 2s，如果有 Alert，就接受掉
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except TimeoutException:
            pass  # alert 未出现
        assert success_element.text == "完成"
        assert len(ele) == 1
        pyautogui.press('esc')

    @allure.story("打开引擎为IP")
    # @pytest.mark.run(order=1)
    def test_personal_openengine3(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        sleep(3)
        pyautogui.press('esc')
        wait = WebDriverWait(driver, 20)
        personal.go_engine_page(name='ip')
        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="IP"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        ele = driver.find_elements(By.XPATH, '//span[text()=" 引擎启动方式:本地 "]')
        sleep(1)
        personal.click_button('//button[@class="m-l-10 ivu-btn ivu-btn-primary"]')
        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )
        sleep(2)
        # 等待 2s，如果有 Alert，就接受掉
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except TimeoutException:
            pass  # alert 未出现
        assert success_element.text == "完成"
        assert len(ele) == 1
        assert not personal.has_fail_message()
        pyautogui.press('esc')

    @allure.story("打开引擎为系统设置-web服务器")
    # @pytest.mark.run(order=1)
    def test_personal_openengine4(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        wait = WebDriverWait(driver, 100)
        sleep(2)
        pyautogui.press('esc')
        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="系统设置"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        personal.go_engine_page(name='system_webip')
        ele = driver.find_elements(By.XPATH, '//span[text()=" 引擎启动方式:本地 "]')
        sleep(2)
        personal.click_button('//button[@class="m-l-10 ivu-btn ivu-btn-primary"]')
        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )
        # 等待 2s，如果有 Alert，就接受掉
        sleep(2)
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except TimeoutException:
            pass  # alert 未出现
        assert success_element.text == "完成"
        assert len(ele) == 1
        assert not personal.has_fail_message()
        pyautogui.press('esc')

    @allure.story("打开引擎为系统设置-IP")
    # @pytest.mark.run(order=1)
    def test_personal_openengine5(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        wait = WebDriverWait(driver, 100)
        sleep(2)
        pyautogui.press('esc')
        personal.go_setting_page()

        personal.click_button('//p[text()=" 本地引擎打开方式: "]/following-sibling::div//i')
        personal.click_button('//li[text()="系统设置"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        personal.go_engine_page(name='system_ip')
        ele = driver.find_elements(By.XPATH, '//span[text()=" 引擎启动方式:本地 "]')
        sleep(2)
        personal.click_button('//button[@class="m-l-10 ivu-btn ivu-btn-primary"]')
        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )
        # 等待 2s，如果有 Alert，就接受掉
        sleep(2)
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except TimeoutException:
            pass  # alert 未出现
        assert success_element.text == "完成"
        assert len(ele) == 1
        assert not personal.has_fail_message()
        pyautogui.press('esc')

    @allure.story("切换系统语言-英语")
    # @pytest.mark.run(order=1)
    def test_personal_language1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        text = personal.switch_language("English")
        assert text == "Search"
        assert not personal.has_fail_message()

    @allure.story("切换系统语言-日语")
    # @pytest.mark.run(order=1)
    def test_personal_language2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        text = personal.switch_language("日本語")
        assert text == "検索けんさく"
        assert not personal.has_fail_message()

    @allure.story("切换系统语言-汉语")
    # @pytest.mark.run(order=1)
    def test_personal_language3(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        text = personal.switch_language("简体中文")
        assert text == "搜索"
        assert not personal.has_fail_message()

    @allure.story("不操作自动退出-10秒")
    # @pytest.mark.run(order=1)
    def test_personal_exit1(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        page = LoginPage(driver)
        date_driver = DateDriver()
        num = 10
        personal.go_exit(num)
        sleep(num)
        ele = driver.find_elements(By.XPATH, '//div[text()="由于您已经长时间没有操作，系统已自动退出！"]')
        personal.click_button('//div[./div[text()="由于您已经长时间没有操作，系统已自动退出！"]]/following-sibling::div//button')
        username = driver.find_elements(By.XPATH, '//input[@placeholder="请输入账户"]')
        page.login(date_driver.username, date_driver.password, date_driver.planning)
        sleep(5)
        assert len(ele) == 1 == len(username)
        assert not personal.has_fail_message()

    @allure.story("不操作自动退出-输入超过86400数字为86400")
    # @pytest.mark.run(order=1)
    def test_personal_exit2(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        num = 100000
        personal.go_exit(num)
        personal.go_setting_page()
        input_ = personal.get_find_element('//div[./p[text()=" 不操作自动退出(秒): "]]//input').get_attribute('value')
        assert input_ == "86400"
        assert not personal.has_fail_message()

    @allure.story("页面搜索栏展开收缩-开启")
    # @pytest.mark.run(order=1)
    def test_personal_search_open(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        radio = personal.get_find_element('//div[p[text()=" 页面搜索栏展开收缩: "]]//label[text()="开启"]/span').get_attribute('class')
        if 'ivu-radio-checked' not in radio:
            personal.click_button('//div[p[text()=" 页面搜索栏展开收缩: "]]//label[text()="开启"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        sleep(3)
        ele = personal.get_find_element('//div[div[@class="vxe-pulldown--content"]//input[@placeholder="搜索"]]').get_attribute('style')
        assert ele == 'display: none;'
        assert not personal.has_fail_message()

    @allure.story("页面搜索栏展开收缩-关闭")
    # @pytest.mark.run(order=1)
    def test_personal_search_close(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        personal.go_setting_page()
        radio = personal.get_find_element(
            '//div[p[text()=" 页面搜索栏展开收缩: "]]//label[text()="不开启(默认)"]/span').get_attribute('class')
        if 'ivu-radio-checked' not in radio:
            personal.click_button('//div[p[text()=" 页面搜索栏展开收缩: "]]//label[text()="不开启(默认)"]')
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        personal.get_find_message()
        sleep(3)
        ele = personal.get_find_element('//div[div[@class="vxe-pulldown--content"]//input[@placeholder="搜索"]]').get_attribute('style')
        assert ele == ''
        assert not personal.has_fail_message()

    @allure.story("组件菜单文字-显示")
    # @pytest.mark.run(order=1)
    def test_personal_characters_display(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        name = "显示"
        style = personal.go_characters_display(name)
        assert style == ""
        assert not personal.has_fail_message()

    @allure.story("组件菜单文字-不显示(默认)")
    # @pytest.mark.run(order=1)
    def test_personal_characters_nodisplay(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        name = "不显示(默认)"
        style = personal.go_characters_display(name)
        assert style == "display: none;"
        assert not personal.has_fail_message()

    @allure.story("恢复菜单展开方式为默认展开")
    # @pytest.mark.run(order=1)
    def test_personal_expand3(self, login_to_personal):
        driver = login_to_personal  # WebDriver 实例
        personal = PersonalPage(driver)  # 用 driver 初始化 PersonalPage
        personal.go_setting_page()
        radio = personal.get_find_element('//label[text()="展开(默认)"]/span')
        if radio.get_attribute('class') == "ivu-radio":
            radio.click()
        personal.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        message = personal.get_find_message()
        assert message == "保存成功"
        assert not personal.has_fail_message()