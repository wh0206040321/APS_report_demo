import logging
from datetime import datetime
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
from Pages.itemsPage.sched_page import SchedPage
from Pages.systemPage.auditLog_page import AuditLogPage
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.systemPage.psi_page import PsiPage
from Pages.systemPage.synchronize_page import SynchronizePage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from datetime import datetime


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_auditlog():
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
        list_ = ["系统管理", "单元设置", "审核日志"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("审核日志页用例")
@pytest.mark.run(order=209)
class TestAuditLogPage:

    @allure.story("操作时间默认显示当天，异常默认显示为是")
    # @pytest.mark.run(order=1)
    def test_auditlog_default(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        # 获取当前日期
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        time_ = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input').get_attribute("value")
        abnormal = audit.get_find_element_xpath('//div[span[text()="异常:"] ]//input[@class="ivu-select-input"]').get_attribute("value")
        assert f"{formatted_date} - {formatted_date}" == time_ and abnormal == "是"
        assert not audit.has_fail_message()

    @allure.story("点击查询默认显示当天有异常数据")
    # @pytest.mark.run(order=1)
    def test_auditlog_defaultsele1(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        abnormal_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[6]')
        time_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[8]')
        assert all(formatted_date in time for time in time_list)
        assert all("at" in abnormal for abnormal in abnormal_list)
        assert not audit.has_fail_message()

    @allure.story("点击查询默认显示当天查询无异常数据")
    # @pytest.mark.run(order=1)
    def test_auditlog_defaultsele2(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        audit.click_button('//div[span[text()="异常:"] ]//input[@class="ivu-select-input"]')
        audit.click_button('//div[@class="d-flex"]//li[text()="否"]')
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        abnormal_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[6]')
        time_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[8]')
        assert all(formatted_date in time for time in time_list)
        assert all("" in abnormal for abnormal in abnormal_list)
        assert not audit.has_fail_message()

    @allure.story("设置时间为当月，用户为当前登录者，显示异常")
    # @pytest.mark.run(order=1)
    def test_auditlog_defaultsele3(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        name = '洪奥青'
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.enter_texts('//div[span[text()="用户:"]]//input[@class="ivu-select-input"]', name)
        audit.click_button(f'//div[@class="d-flex"]//li[text()="{name}"]')
        audit.click_button('//div[span[text()="用户:"]]//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]')
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        user_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[3]')
        abnormal_list = audit.loop_judgment('//table[@class="vxe-table--body"]//tr/td[6]')

        audit.click_button('//div[p[text()="执行开始时间"]]/div[1]')
        sleep(0.5)
        time_list_before = audit.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[8]').text
        time_list_before_ = time_list_before.split()[0]
        audit.click_button('//div[p[text()="执行开始时间"]]/div[1]')
        sleep(0.5)
        time_list_after = audit.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]/td[8]').text
        time_list_after_ = time_list_after.split()[0]
        assert all(name == user for user in user_list)
        assert all("at" in abnormal for abnormal in abnormal_list)
        assert formatted_first_day <= time_list_before_ <= time_list_after_ <= formatted_date
        assert not audit.has_fail_message()

    @allure.story("查询用户代码功")
    # @pytest.mark.run(order=1)
    def test_audit_select1(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        date_driver = DateDriver()
        name = date_driver.username
        today = datetime.now().date()
        # 格式化为年/月/日
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        audit.select_input(name)
        sleep(1)
        eles = audit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        list_ = [ele.text for ele in eles]
        assert all(text == name for text in list_), f"表格内容不符合预期，实际值: {list_}"
        assert not audit.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_audit_select2(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")

        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        sleep(1)
        eles = audit.get_find_element_xpath('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            audit.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            audit.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//input')
        eles = audit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        assert len(eles) == 0
        assert not audit.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_audit_select3(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        name = "a"
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        audit.hover("包含")
        sleep(1)
        audit.select_input(name)
        sleep(1)
        eles = audit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(name in text for text in list_)
        assert not audit.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_audit_select4(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        name = "a"
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        audit.hover("符合开头")
        sleep(1)
        audit.select_input(name)
        sleep(1)
        eles = audit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(name) for item in list_)
        assert not audit.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_audit_select5(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        name = "n"
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        audit.hover("符合结尾")
        sleep(1)
        audit.select_input(name)
        sleep(1)
        eles = audit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(name) for item in list_)
        assert not audit.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_audit_clear(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        today = datetime.now().date()
        # 格式化为年/月/日
        formatted_date = today.strftime("%Y/%m/%d")
        first_day = datetime(today.year, today.month, 1).date()
        formatted_first_day = first_day.strftime("%Y/%m/%d")
        ele = audit.get_find_element_xpath('//div[span[text()="操作时间:"]]//input')
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        audit.enter_texts('//div[span[text()="操作时间:"]]//input', f"{formatted_first_day} - {formatted_date}")
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        name = "a"
        sleep(1)
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        audit.hover("包含")
        sleep(1)
        audit.select_input(name)
        sleep(1)
        audit.click_button('//div[p[text()="用户代码"]]/following-sibling::div//i')
        audit.hover("清除所有筛选条件")
        sleep(1)
        ele = audit.get_find_element_xpath('//div[p[text()="用户代码"]]/following-sibling::div//i').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not audit.has_fail_message()

    @allure.story("点击导出成功")
    # @pytest.mark.run(order=1)
    def test_auditlog_export(self, login_to_auditlog):
        driver = login_to_auditlog  # WebDriver 实例
        audit = AuditLogPage(driver)  # 用 driver 初始化 AuditLogPage
        audit.click_all_button("查询")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "is--visible")))
        audit.click_all_button("导出Excel")
        ele = audit.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not audit.has_fail_message()
