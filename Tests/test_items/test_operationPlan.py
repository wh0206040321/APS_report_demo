import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.operationPlan_page import operationPlanPage
from Utils.data_driven import DateDriver
from Utils.shared_data_util import SharedDataUtil
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_operationPlan():
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
        page.click_button('(//span[text()="计划业务数据"])[1]')  # 点击计划业务数据
        page.click_button('(//span[text()="工作指示发布"])[1]')  # 点击工作指示发布
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("工作指示发布表测试用例")
@pytest.mark.run(order=22)
class TestOperationPlanPage:
    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_operationPlan_select2(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        driver.execute_script("document.body.style.zoom='1'")
        operationPlan.right_refresh('工作指示发布')
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = operationPlan.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            operationPlan.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            operationPlan.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]//input')
        eles = operationPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        operationPlan.right_refresh('工作指示发布')
        assert len(eles) == 0
        assert not operationPlan.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_operationPlan_select3(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        name = operationPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        operationPlan.hover("包含")
        sleep(1)
        operationPlan.select_input(first_char)
        sleep(1)
        eles = operationPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.get_attribute("innerText") for ele in eles]
        operationPlan.right_refresh('工作指示发布')
        assert all(first_char in text for text in list_)
        assert not operationPlan.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_operationPlan_select4(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        name = operationPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        operationPlan.hover("符合开头")
        sleep(1)
        operationPlan.select_input(first_char)
        sleep(1)
        eles = operationPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.get_attribute("innerText") for ele in eles]
        operationPlan.right_refresh('工作指示发布')
        assert all(str(operationPlan).startswith(first_char) for operationPlan in list_)
        assert not operationPlan.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_operationPlan_select5(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        name = operationPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        operationPlan.hover("符合结尾")
        sleep(1)
        operationPlan.select_input(last_char)
        sleep(1)
        eles = operationPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.get_attribute("innerText") for ele in eles]
        operationPlan.right_refresh('工作指示发布')
        assert all(str(operationPlan).endswith(last_char) for operationPlan in list_)
        assert not operationPlan.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_operationPlan_clear(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        name = "3"
        sleep(1)
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        operationPlan.hover("包含")
        sleep(1)
        operationPlan.select_input(name)
        sleep(1)
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i')
        operationPlan.hover("清除所有筛选条件")
        sleep(1)
        ele = operationPlan.get_find_element_xpath('//p[text()="资源代码"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        operationPlan.right_refresh('工作指示发布')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not operationPlan.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_operationPlan_ctrlC(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 driver 初始化 operationPlanPage
        operationPlan.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = operationPlan.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[3]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        operationPlan.click_button('//p[text()="资源代码"]/ancestor::div[2]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = operationPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[3]')
        eles = [ele.get_attribute("innerText") for ele in eles]
        operationPlan.right_refresh('工作指示发布')
        assert all(before_data in ele for ele in eles)
        assert not operationPlan.has_fail_message()

    @allure.story("不勾选资源不点击时间，点击查询 不允许查询")
    # @pytest.mark.run(order=1)
    def test_operationPlan_selectfail1(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(
            driver
        )  # 用 operationPlan 初始化 operationPlanPage
        operationPlan.click_selebutton()
        message = operationPlan.get_error_message()
        operationPlan.right_refresh('工作指示发布')
        # 检查元素是否包含子节点
        assert message == "请选择时间段和资源"
        assert not operationPlan.has_fail_message()

    @allure.story("不勾选资源选择时间段，点击查询 不允许查询")
    # @pytest.mark.run(order=1)
    def test_operationPlan_selectfail2(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(
            driver
        )  # 用 operationPlan 初始化 operationPlanPage
        sleep(1)
        operationPlan.click_inputbutton()
        operationPlan.click_timebutton()
        operationPlan.click_button('(//em[text()="1"])[1]')
        operationPlan.click_button('(//em[text()="28"])[last()]')
        operationPlan.click_okbutton()
        operationPlan.click_selebutton()
        message = operationPlan.get_error_message()
        operationPlan.right_refresh('工作指示发布')
        # 检查元素是否包含子节点
        assert message == "请选择时间段和资源"
        assert not operationPlan.has_fail_message()

    @allure.story("勾选资源，不选择时间段，点击查询 不允许查询")
    # @pytest.mark.run(order=1)
    def test_operationPlan_selectfail3(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(
            driver
        )  # 用 operationPlan 初始化 operationPlanPage
        sleep(1)
        operationPlan.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-unchecked"])[3]'
        )
        operationPlan.click_selebutton()
        message = operationPlan.get_error_message()
        operationPlan.right_refresh('工作指示发布')
        # 检查元素是否包含子节点
        assert message == "请选择时间段和资源"
        assert not operationPlan.has_fail_message()

    @allure.story("勾选资源，勾选时间段，点击查询 查询成功,发布指示成功")
    # @pytest.mark.run(order=1)
    def test_operationPlan_success(self, login_to_operationPlan):
        driver = login_to_operationPlan  # WebDriver 实例
        operationPlan = operationPlanPage(driver)  # 用 operationPlan 初始化 operationPlanPage
        shared_data = SharedDataUtil.load_data()
        resource1 = shared_data.get("master_res1")
        resource2 = shared_data.get("master_res2")
        sleep(1)
        # 搜索框输入资源代码
        operationPlan.enter_texts(
            '(//div[./p[text()="资源代码"]]/following-sibling::div//input)[1]',
            resource1
        )
        # 勾选资源
        sleep(1)
        row_number = driver.execute_script(
            "return document.evaluate("
            f'"count(//tr[.//span[text()=\\"{resource1}\\"]]/preceding-sibling::tr) + 1",'
            "document, null, XPathResult.NUMBER_TYPE, null"
            ").numberValue;"
        )
        print(f"行号: {int(row_number)}")
        operationPlan.click_button(
            f'//table[@class="vxe-table--body"]//tr[{int(row_number)}]/td[2]//span[1]/span'
        )
        sleep(1)
        # 清除资源代码的输入
        ele = operationPlan.get_find_element_xpath(
            '(//div[./p[text()="资源代码"]]/following-sibling::div//input)[1]'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        # 搜索框输入资源代码
        operationPlan.enter_texts(
            '(//div[./p[text()="资源代码"]]/following-sibling::div//input)[1]',
            resource2,
        )
        sleep(1)
        # 勾选资源
        row_number2 = driver.execute_script(
            "return document.evaluate("
            f'"count(//tr[.//span[text()=\\"{resource2}\\"]]/preceding-sibling::tr) + 1",'
            "document, null, XPathResult.NUMBER_TYPE, null"
            ").numberValue;"
        )
        print(f"行号: {int(row_number2)}")
        operationPlan.click_button(
            f'//table[@class="vxe-table--body"]//tr[{int(row_number2)}]/td[2]//span[1]/span'
        )
        # 清除资源代码的输入
        ele = operationPlan.get_find_element_xpath(
            '(//div[./p[text()="资源代码"]]/following-sibling::div//input)[1]'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)

        # 打开时间段选择弹窗（点击时间选择按钮）
        operationPlan.click_inputbutton()
        # 选择当前日期（点击带有 today 和 focused 样式的日期单元格）
        operationPlan.click_button(
            '//span[contains(@class,"ivu-date-picker-cells-cell-today")]/preceding-sibling::span[1]'
        )
        # 点击下月按钮
        operationPlan.click_button('(//span[@class="ivu-picker-panel-icon-btn ivu-date-picker-next-btn ivu-date-picker-next-btn-arrow"])[2]/i')
        sleep(0.5)
        operationPlan.click_button(
            '(//span[@class="ivu-picker-panel-icon-btn ivu-date-picker-next-btn ivu-date-picker-next-btn-arrow"])[2]/i')
        # 选择具体的时间点（例如：28 日）
        operationPlan.click_button('(//em[text()="28"])[last()]')
        # 点击确认按钮以完成时间段的选择
        operationPlan.click_okbutton()

        # 点击查询
        operationPlan.click_selebutton()
        operationPlan.enter_texts(
            '//div[./p[text()="订单代码"]]/parent::div//input', "1测试C订单"
        )

        input_text1 = operationPlan.get_find_element_xpath(
            f'(//table[.//span[text()="{resource1}"]])[last()]//tr[1]//td[7]'
        ).get_attribute("innerText")
        input_text2 = operationPlan.get_find_element_xpath(
            f'(//table[.//span[text()="{resource2}"]])[last()]//tr[2]//td[7]'
        ).get_attribute("innerText")
        input_text3 = driver.find_elements(
            By.XPATH, '(//tr[.//span[text()="1测试C订单"]])[3]'
        )

        operationPlan.click_button('//p[text()="工作指示发布"]')
        operationPlan.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        operationPlan.get_find_message()
        operationPlan.wait_for_loading_to_disappear()
        sleep(1)
        after_text = driver.find_elements(
            By.XPATH, '(//table[@class="vxe-table--body"])[3]/tbody//tr'
        )
        # 验证提示信息是否符合预期
        assert (
            input_text1 == resource1
            and input_text2 == resource2
            and len(input_text3) == 0
            and len(after_text) == 0
        )
        assert not operationPlan.has_fail_message()
