import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.operationPlan_page import operationPlanPage
from Pages.itemsPage.previewPlan_page import PreviewPlanPage
from Utils.data_driven import DateDriver
from Utils.shared_data_util import SharedDataUtil
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_previewPlan():
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
        page.click_button('(//span[text()="工作指示一览"])[1]')  # 点击工作指示一览
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("工作指示一览表测试用例")
@pytest.mark.run(order=23)
class TestPreviewPlanPage:
    @allure.story("工作指示发布成功，工作指示一览显示成功")
    # @pytest.mark.run(order=1)
    def test_previewPlan_select(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 previewPlan 初始化 PreviewPlanPage
        shared_data = SharedDataUtil.load_data()
        resource1 = shared_data.get("master_res1")
        resource2 = shared_data.get("master_res2")
        previewPlan.enter_texts(
            '//div[./p[text()="订单代码"]]/parent::div//input', "1测试C订单"
        )
        ele_code1 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[1]/td[4]'
        ).text
        ele_resource1 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[1]/td[7]'
        ).text
        ele_code2 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[2]/td[4]'
        ).text
        ele_resource2 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[2]/td[7]'
        ).text
        previewPlan.right_refresh('工作指示一览')
        assert (
            ele_code1 == "1测试C订单"
            and ele_resource1 == resource1
            and ele_code2 == "1测试C订单"
            and ele_resource2 == resource2
        )
        assert not previewPlan.has_fail_message()

    @allure.story("删除工作指示成功，并且工作指示发布重新可以查询信息")
    # @pytest.mark.run(order=1)
    def test_previewPlan_delete(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 previewPlan 初始化 PreviewPlanPage
        operationPlan = operationPlanPage(driver)
        shared_data = SharedDataUtil.load_data()
        resource1 = shared_data.get("master_res1")
        resource2 = shared_data.get("master_res2")
        previewPlan.enter_texts(
            '//div[./p[text()="订单代码"]]/parent::div//input', "1测试C订单"
        )
        ele_resource1 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[1]/td[7]'
        ).text
        ele_resource2 = previewPlan.get_find_element_xpath(
            '//table[.//td[4]//span[text()="1测试C订单"]]//tr[2]/td[7]'
        ).text
        if ele_resource1 == resource1 and ele_resource2 == resource2:
            sleep(2)
            previewPlan.click_button(
                '//table[@class="vxe-table--header"]//th[2]/div/span/span'
            )
            sleep(1)
            previewPlan.click_del_button()
            previewPlan.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        previewPlan.wait_for_loading_to_disappear()
        ele_none = driver.find_elements(
            By.XPATH, '//table[.//td[4]//span[text()="1测试C订单"]]/tbody//tr'
        )

        previewPlan.click_button('(//span[text()="工作指示发布"])[1]')
        sleep(1)
        # 搜索框输入资源代码
        operationPlan.enter_texts(
            '(//div[./p[text()="资源代码"]]/following-sibling::div//input)[1]',
            f"{resource1}",
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
            f"{resource2}",
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
        operationPlan.click_button(
            '(//span[@class="ivu-picker-panel-icon-btn ivu-date-picker-next-btn ivu-date-picker-next-btn-arrow"])[2]/i')
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
        ).text
        input_text2 = operationPlan.get_find_element_xpath(
            f'(//table[.//span[text()="{resource2}"]])[last()]//tr[2]//td[7]'
        ).text
        input_text3 = driver.find_elements(
            By.XPATH, '(//tr[.//span[text()="1测试C订单"]])[3]'
        )

        operationPlan.click_button('//p[text()="工作指示发布"]')
        operationPlan.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        operationPlan.get_find_message()
        operationPlan.wait_for_loading_to_disappear()
        after_text = driver.find_elements(
            By.XPATH, '(//table[@class="vxe-table--body"])[3]/tbody//tr'
        )
        operationPlan.click_button('//div[div[text()=" 工作指示发布 "]]/span')

        # 验证提示信息是否符合预期
        assert (
            input_text1 == resource1
            and input_text2 == resource2
            and len(input_text3) == 0
            and len(ele_none) == 0
            and len(after_text) == 0
        )
        assert not previewPlan.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_previewPlan_select2(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 driver 初始化 PreviewPlanPage
        previewPlan.right_refresh('工作指示一览')
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = previewPlan.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            previewPlan.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            previewPlan.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]//input')
        eles = previewPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        previewPlan.right_refresh('工作指示一览')
        assert len(eles) == 0
        assert not previewPlan.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_previewPlan_select3(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 driver 初始化 PreviewPlanPage
        name = previewPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        previewPlan.hover("包含")
        sleep(1)
        previewPlan.select_input(first_char)
        sleep(1)
        eles = previewPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        previewPlan.right_refresh('工作指示一览')
        assert all(first_char in text for text in list_)
        assert not previewPlan.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_previewPlan_select4(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 driver 初始化 PreviewPlanPage
        name = previewPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        previewPlan.hover("符合开头")
        sleep(1)
        previewPlan.select_input(first_char)
        sleep(1)
        eles = previewPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        previewPlan.right_refresh('工作指示一览')
        assert all(str(previewPlan).startswith(first_char) for previewPlan in list_)
        assert not previewPlan.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_previewPlan_select5(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 driver 初始化 PreviewPlanPage
        name = previewPlan.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[3]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        previewPlan.hover("符合结尾")
        sleep(1)
        previewPlan.select_input(last_char)
        sleep(1)
        eles = previewPlan.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[3]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        previewPlan.right_refresh('工作指示一览')
        assert all(str(previewPlan).endswith(last_char) for previewPlan in list_)
        assert not previewPlan.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_previewPlan_clear(self, login_to_previewPlan):
        driver = login_to_previewPlan  # WebDriver 实例
        previewPlan = PreviewPlanPage(driver)  # 用 driver 初始化 PreviewPlanPage
        name = "3"
        sleep(1)
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        previewPlan.hover("包含")
        sleep(1)
        previewPlan.select_input(name)
        sleep(1)
        previewPlan.click_button('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i')
        previewPlan.hover("清除所有筛选条件")
        sleep(1)
        ele = previewPlan.get_find_element_xpath('//p[text()="工作代码"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        previewPlan.right_refresh('工作指示一览')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not previewPlan.has_fail_message()
