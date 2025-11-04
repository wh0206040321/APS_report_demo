# tests/test_login.py

import allure
import pytest

from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit


@pytest.fixture
def login_pa():
    driver = None
    try:
        """初始化并返回 LoginPage 对象"""
        date_driver = DateDriver()
        driver = create_driver(date_driver.driver_path)

        # 初始化页面
        page = LoginPage(driver)
        page.navigate_to(date_driver.url)

        yield page
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("登录页面测试用例")
@pytest.mark.run(order=1)
class TestLoginPage:
    @allure.story("账户错误 计划单元无选项")
    def test_login_acfail(self, login_pa):
        login_pa.enter_username("123")  # 输入用户名
        login_pa.enter_password("1234qweR")  # 输入错误的密码
        login_pa.click_button('(//input[@type="text"])[2]')  # 点击下拉框
        li_element = login_pa.get_find_element(
            '//li[text()="无匹配数据"]'
        )  # 账户错误时 不显示计划单元名称,li的标签为无匹配数据
        li_text = li_element.get_attribute("innerText")
        assert li_text == "无匹配数据"
        assert not login_pa.has_fail_message()

    @allure.story("密码错误 登录失败")
    def test_login_pafail(self, login_pa):
        login_pa.enter_username(f"{DateDriver().username}")  # 输入用户名
        login_pa.enter_password("12345qweR")  # 输入错误的密码
        login_pa.click_button('(//input[@type="text"])[2]')  # 点击下拉框
        login_pa.click_button(f'//li[text()="{DateDriver().planning}"]')  # 点击计划单元
        login_pa.click_button(
            '//button[@type="button" and @class="ivu-btn ivu-btn-primary ivu-btn-long ivu-btn-large"]'
        )  # 点击登录按钮
        element = login_pa.get_find_element('//div[text()=" 用户名或密码无效 "]').text
        assert element == "用户名或密码无效"
        assert not login_pa.has_fail_message()

    @allure.story("登录成功")
    def test_login_success(self, login_pa):
        login_pa.enter_username(f"{DateDriver().username}")  # 输入用户名
        login_pa.enter_password(f"{DateDriver().password}")  # 输入密码
        login_pa.click_button('(//input[@type="text"])[2]')  # 点击下拉框
        login_pa.click_button(f'//li[text()="{DateDriver().planning}"]')  # 点击计划单元
        login_pa.click_button(
            '//button[@type="button" and @class="ivu-btn ivu-btn-primary ivu-btn-long ivu-btn-large"]'
        )  # 点击登录按钮

        # 断言登录成功，检查排产单元是否存在
        profile_icon = login_pa.get_find_element(
            f'//div[text()=" {DateDriver().planning} "]'
        )
        assert profile_icon.is_displayed()  # 断言用户头像可见，表明登录成功
        assert not login_pa.has_fail_message()
