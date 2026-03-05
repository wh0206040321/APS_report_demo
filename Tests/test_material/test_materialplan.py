import logging
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.plan_page import PlanPage
from Pages.itemsPage.sched_page import SchedPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_materialplan():
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
        list_ = ["计划运行", "计算工作台", "物控计算"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        sleep(1)
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物控计算测试用例")
@pytest.mark.run(order=143)
class TestMaterialPlanPage:
    @allure.story("不输入计划方案，点击执行不成功")
    # @pytest.mark.run(order=1)
    def test_materialplan_fail(self, login_to_materialplan):
        driver = login_to_materialplan  # WebDriver 实例
        plan = PlanPage(driver)  # 用 driver 初始化 PlanPage
        wait = WebDriverWait(driver, 20)
        # 等待loading遮罩消失
        wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.el-loading-spinner")
            )
        )

        plan.click_plan()
        message = plan.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请选择计划方案"
        assert not plan.has_fail_message()

    @allure.story("执行成功")
    # @pytest.mark.run(order=1)
    def test_materialplan_success(self, login_to_materialplan):
        driver = login_to_materialplan
        plan = PlanPage(driver)
        wait = WebDriverWait(driver, 60)

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
        plan.click_plan()
        # 等待“完成”的文本出现
        success_element1 = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[1]/p[text()=" 完成 "]')
            )
        )

        # 等待“完成”的文本出现
        success_element3 = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )

        assert success_element1.text == "完成"
        assert success_element3.text == "完成"
        assert not plan.has_fail_message()

    @allure.story("日志信息过滤查询成功")
    # @pytest.mark.run(order=1)
    def test_plan_select_materialplan(self, login_to_materialplan):
        driver = login_to_materialplan
        plan = PlanPage(driver)
        wait = WebDriverWait(driver, 60)
        date_driver = DateDriver()

        plan.click_button('(//div[@class="d-flex"])[2]/p[text()=" 完成 "]')
        plan.wait_for_loading_to_disappear()
        # 过滤条件查询，一个不选，显示正常
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = plan.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            plan.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            plan.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        plan.click_button('//div[div[p[text()="日志信息"]]]//input')
        eles = plan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        plan.hover("清除所有筛选条件")
        assert len(eles) == 0

        # 过滤条件查询，设置包含条件查询成功
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        plan.hover("包含")
        sleep(1)
        plan.select_input_material('BOM')
        sleep(1)
        eles = plan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all('BOM' in text for text in list_)

        # 过滤条件查询，设置符合开头查询成功
        name = plan.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr//td[3]'
        ).get_attribute('innerText')
        first_char = '检查'
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        plan.hover("符合开头")
        sleep(1)
        plan.select_input_material(first_char)
        sleep(1)
        eles = plan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).startswith(first_char) for item in list_)

        # 过滤条件查询，设置符合结尾查询成功
        name = plan.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr//td[3]'
        ).get_attribute('innerText')
        last_char = '。'
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        plan.hover("符合结尾")
        sleep(1)
        plan.select_input_material(last_char)
        sleep(1)
        eles = plan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[9]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        assert all(str(item).endswith(last_char) for item in list_)

        # 清除筛选效果成功
        plan.click_button('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]')
        plan.hover("清除所有筛选条件")
        sleep(1)
        ele = plan.get_find_element_xpath('//div[div[p[text()="日志信息"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not plan.has_fail_message()
