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
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.sched_page import SchedPage
from Pages.systemPage.imp_page import ImpPage
from Pages.systemPage.psi_page import PsiPage
from Pages.systemPage.planUnit_page import PlanUnitPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from selenium.webdriver.chrome.options import Options
import os


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_planUnit():
    driver = None
    try:
        """初始化并返回 driver"""
        download_path = os.path.abspath("downloads")
        os.makedirs(download_path, exist_ok=True)
        options = Options()
        options.add_argument("--allow-running-insecure-content")
        options.add_experimental_option("prefs", {
            "download.prompt_for_download": False,
            "download.default_directory": download_path,
            "safebrowsing.enabled": False
        })
        date_driver = DateDriver()
        driver = create_driver(date_driver.driver_path, options)
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
        list_ = ["系统管理", "系统设置", "计划单元"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("计划单元页用例")
@pytest.mark.run(order=204)
class TestPlanUnitPage:

    @allure.story("添加计划单元 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_planUnit_addfail(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        add = AddsPages(driver)
        layout = "测试布局A"
        add.add_layout(layout)
        # 获取布局名称的文本元素
        name = unit.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        unit.click_all_button("新增")
        list_ = [
            '(//label[text()="计划单元"])[1]/parent::div//input',
            '(//label[text()="计划单元名称"])[1]/parent::div//input',
            '(//label[text()="模板名称"])[1]/parent::div//div[@class="ivu-select-selection"]',
        ]
        unit.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        sleep(1)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        unit.right_refresh()
        assert all(value == expected_color for value in value_list)
        assert layout == name
        assert not unit.has_fail_message()

    @allure.story("添加计划单元 填写计划单元，不填写名称和模版 不允许提交")
    # @pytest.mark.run(order=1)
    def test_planUnit_addfail1(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        add = AddsPages(driver)
        name = "1测试计划单元"
        unit.click_all_button("新增")
        list_ = [
            '(//label[text()="计划单元名称"])[1]/parent::div//input',
            '(//label[text()="模板名称"])[1]/parent::div//div[@class="ivu-select-selection"]',
        ]
        unit.enter_texts('(//label[text()="计划单元"])[1]/parent::div//input', name)
        unit.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        sleep(1)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        unit.right_refresh()
        assert all(value == expected_color for value in value_list)
        assert not unit.has_fail_message()

    @allure.story("添加计划单元 填写计划单元，名称不填写模版 不允许提交")
    # @pytest.mark.run(order=1)
    def test_planUnit_addfail2(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        add = AddsPages(driver)
        name = "1测试计划单元"
        unit.click_all_button("新增")
        list_ = [
            '(//label[text()="模板名称"])[1]/parent::div//div[@class="ivu-select-selection"]',
        ]
        unit.enter_texts('(//label[text()="计划单元"])[1]/parent::div//input', name)
        unit.enter_texts('(//label[text()="计划单元名称"])[1]/parent::div//input', name)
        unit.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        sleep(1)
        value_list = add.get_border_color(list_)
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        unit.right_refresh()
        assert all(value == expected_color for value in value_list)
        assert not unit.has_fail_message()

    @allure.story("添加标准计划单元成功")
    # @pytest.mark.run(order=1)
    def test_planUnit_success1(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试计划单元标准"
        module = "标准"
        unit.add_plan_unit(name, module)
        unit.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        unit.get_find_message()
        unit.wait_for_loading_to_disappear()
        unit.select_input(name)
        ele = unit.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        assert len(ele) == 1
        assert not unit.has_fail_message()

    @allure.story("添加CTB计划单元成功")
    # @pytest.mark.run(order=1)
    def test_planUnit_success2(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试计划单元CTB"
        module = "CTB"
        unit.add_plan_unit(name, module)
        unit.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        unit.get_find_message()
        unit.wait_for_loading_to_disappear()
        unit.select_input(name)
        ele = unit.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        assert len(ele) == 1
        assert not unit.has_fail_message()

    @allure.story("添加小日程计划单元成功")
    # @pytest.mark.run(order=1)
    def test_planUnit_success3(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试计划单元小日程"
        module = "小日程"
        unit.add_plan_unit(name, module)
        unit.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        unit.get_find_message()
        unit.wait_for_loading_to_disappear()
        unit.select_input(name)
        ele = unit.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        assert len(ele) == 1
        assert not unit.has_fail_message()

    @allure.story("添加重复名称，不允许添加")
    # @pytest.mark.run(order=1)
    def test_planUnit_repeat(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试计划单元小日程"
        module = "标准"
        unit.add_plan_unit(name, module)
        unit.click_button(
            '(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        ele = unit.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute('innerText')
        unit.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert ele == '记录已存在,请检查！'
        assert not unit.has_fail_message()

    # @allure.story("文本框的校验")
    # # @pytest.mark.run(order=1)
    # def test_planUnit_textverify(self, login_to_planUnit):
    #     driver = login_to_planUnit  # WebDriver 实例
    #     unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
    #     name = "1111111111111111333311222211112222211111111133331111111444441111111111111111111111111111111111111111"
    #     module = "标准"
    #     unit.add_plan_unit(name, module)
    #     unit.select_input(name)
    #     unit.click_confirm_button()
    #     ele = unit.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
    #     assert len(ele) == 1
    #     assert not unit.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_planUnit_addtest1(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试A"
        module = "标准"
        unit.add_plan_unit(name, module)
        unit.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])')
        unit.get_find_message()
        unit.wait_for_loading_to_disappear()
        unit.select_input(name)
        ele = unit.finds_elements(By.XPATH, f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        assert len(ele) == 1
        assert not unit.has_fail_message()

    @allure.story("不允许修改计划单元和模版名称")
    # @pytest.mark.run(order=1)
    def test_planUnit_updaterepeat(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试计划单元小日程"
        unit.select_input(name)
        unit.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        unit.click_all_button("编辑")
        sleep(1)
        unit.enter_texts('//label[text()="计划单元名称"]/parent::div//input', '修改计划单元名称')
        sty1 = unit.get_find_element_xpath('(//label[text()="计划单元"])[1]/parent::div//input').get_attribute("disabled")
        sty2 = unit.get_find_element_xpath('(//label[text()="模板名称"])[1]/parent::div//div[@class="ivu-select-selection"]//input[@type="text"]').get_attribute("disabled")
        unit.click_confirm_button()
        ele = unit.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{name}"]]/td[3]').get_attribute("innerText")
        assert sty1 == sty2 == 'true'
        assert ele == '修改计划单元名称'
        unit.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        unit.click_all_button("编辑")
        sleep(1)
        unit.enter_texts('//label[text()="计划单元名称"]/parent::div//input', name)
        unit.click_confirm_button()
        ele = unit.get_find_element_xpath(f'//table[@class="vxe-table--body"]//tr[td[2]//span[text()="{name}"]]/td[3]').get_attribute("innerText")
        unit.right_refresh()
        assert ele == name
        assert not unit.has_fail_message()

    @allure.story("查询物料代码成功")
    # @pytest.mark.run(order=1)
    def test_unit_selectcodesuccess(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试A"
        # 点击查询
        unit.click_sel_button()
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
        unit.click_button('//div[text()="计划单元" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        unit.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        unit.click_select_button()
        # 定位第一行是否为name
        unitcode = unit.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        unitcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        unit.right_refresh()
        assert unitcode == name and len(unitcode2) == 0
        assert not unit.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_unit_selectnodatasuccess(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage

        # 点击查询
        unit.click_sel_button()
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
        unit.click_button('//div[text()="计划单元" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        unit.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        unit.click_select_button()
        unitcode = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        unit.right_refresh()
        assert len(unitcode) == 0
        assert not unit.has_fail_message()

    @allure.story("查询计划单元名称中包含A成功")
    # @pytest.mark.run(order=1)
    def test_unit_selectnamesuccess(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage

        name = "A"
        # 点击查询
        unit.click_sel_button()
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
        unit.click_button('//div[text()="计划单元名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        unit.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        unit.click_select_button()
        eles = unit.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        unit.right_refresh()
        assert len(eles) > 0
        assert all(name in ele for ele in eles)
        assert not unit.has_fail_message()

    @allure.story("查询物料名称包含单元并且模版名称为标准")
    # @pytest.mark.run(order=1)
    def test_unit_selectsuccess2(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage

        name = "单元"
        m = '标准'
        # 点击查询
        unit.click_sel_button()
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
        unit.click_button('//div[text()="计划单元名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        unit.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        unit.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        unit.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        unit.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        unit.click_button('//div[text()="模板名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击=
        unit.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            m,
        )
        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        unit.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        unit.click_select_button()
        eles1 = unit.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[4]')
        eles2 = unit.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        unit.right_refresh()
        assert len(eles1) > 0 and len(eles2) > 0
        assert all(m == ele for ele in eles1) and all(name in ele for ele in eles2)
        assert not unit.has_fail_message()

    @allure.story("查询计划单元包含A或模版名称为CTB")
    # @pytest.mark.run(order=1)
    def test_unit_selectsuccess3(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage

        name = "A"
        m = 'CTB'
        # 点击查询
        unit.click_sel_button()
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
        unit.click_button('//div[text()="计划单元" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        unit.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        unit.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )

        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        unit.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        unit.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击物料优先度
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        unit.click_button('//div[text()="模板名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        unit.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值0
        unit.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            m,
        )
        # 点击（
        unit.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        unit.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        unit.click_select_button()
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
                td2 = tds[1].text.strip()
                td4 = tds[3].text.strip()

                assert name in td2 or m == td4, f"第 {idx + 1} 行不符合：td3={td2}, td4={td4}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td2 = tds[1].text.strip()
                td4 = tds[3].text.strip()

                assert name in td2 or m == td4, f"第 {idx + 1} 行不符合：td3={td2}, td4={td4}"
                valid_count += 1
        unit.right_refresh()
        assert not unit.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_unit_select2(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        driver.execute_script("document.body.style.zoom='1'")
        unit.right_refresh('计划单元')
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        sleep(1)
        eles = unit.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            unit.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            unit.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]//input')
        eles = unit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        unit.right_refresh('计划单元')
        assert len(eles) == 0
        assert not unit.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_unit_select3(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = unit.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        unit.hover("包含")
        sleep(1)
        unit.select_input(first_char)
        sleep(1)
        eles = unit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        unit.right_refresh('计划单元')
        assert all(first_char in text for text in list_)
        assert not unit.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_unit_select4(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = unit.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        unit.hover("符合开头")
        sleep(1)
        unit.select_input(first_char)
        sleep(1)
        eles = unit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        unit.right_refresh('计划单元')
        assert all(str(unit).startswith(first_char) for unit in list_)
        assert not unit.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_unit_select5(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = unit.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        unit.hover("符合结尾")
        sleep(1)
        unit.select_input(last_char)
        sleep(1)
        eles = unit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        unit.right_refresh('计划单元')
        assert all(str(unit).endswith(last_char) for unit in list_)
        assert not unit.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_unit_clear(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "3"
        sleep(1)
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        unit.hover("包含")
        sleep(1)
        unit.select_input(name)
        sleep(1)
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i')
        unit.hover("清除所有筛选条件")
        sleep(1)
        ele = unit.get_find_element_xpath('//p[text()="计划单元"]/ancestor::div[2]/div[3]//i').get_attribute(
            "class")
        unit.right_refresh('计划单元')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not unit.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_unit_ctrlIrepeat(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        unit.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = unit.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = unit.get_error_message()
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not unit.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_unit_ctrlI(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        unit.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        unit.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        unit.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = unit.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        unit.get_find_message()
        unit.select_input('1没有数据添加')
        ele2 = unit.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not unit.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_unit_ctrlM(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        unit.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        unit.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        unit.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = unit.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        unit.get_find_message()
        unit.select_input('1没有数据修改')
        ele2 = unit.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        unit.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        unit.click_all_button('删除')
        unit.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = unit.get_find_message()
        unit.right_refresh('计划单元')
        assert message == "删除成功！"
        assert not unit.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_unit_ctrlC(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        unit.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = unit.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        unit.click_button('//p[text()="计划单元"]/ancestor::div[2]//input')
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = unit.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        unit.right_refresh('计划单元')
        assert all(before_data in ele for ele in eles)
        assert not unit.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_unit_shift(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        unit.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = unit.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = unit.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not unit.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_unit_ctrls(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        unit.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = unit.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = unit.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        unit.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = unit.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not unit.has_fail_message()

    @allure.story("下载成功")
    # @pytest.mark.run(order=1)
    def test_unit_download(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        unit.right_refresh()
        name = "1测试A"

        unit.select_input(name)
        unit.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        unit.click_all_button("下载")
        ele = unit.finds_elements(By.XPATH,
                                     '//div[@class="ivu-modal-body"]//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not unit.has_fail_message()

    @allure.story("上传成功")
    # @pytest.mark.run(order=1)
    def test_unit_upload(self, login_to_planUnit):
        driver = login_to_planUnit  # WebDriver 实例
        unit = PlanUnitPage(driver)  # 用 driver 初始化 PlanUnitPage
        name = "1测试A"
        unit.select_input(name)
        unit.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{name}"]')
        unit.click_all_button("上传")

        # 清理 .crdownload 文件，避免上传未完成的文件
        current_dir = os.path.dirname(__file__)
        download_path = os.path.join(current_dir, "downloads")
        for f in os.listdir(download_path):
            if f.endswith(".crdownload"):
                os.remove(os.path.join(download_path, f))

        sleep(2)
        # 1. 准备上传文件路径
        upload_file = os.path.join(download_path, f"{name}.km")
        assert os.path.isfile(upload_file), f"❌ 上传文件不存在: {upload_file}"

        # 2. 定位上传控件并执行上传
        unit.upload_file(upload_file)
        unit.click_button('//div[@class="el-message-box__btns"]/button[2]')
        message = unit.get_find_message()
        # 3. 等待上传完成并断言结果
        assert message == "上传成功", "上传失败或未显示成功提示"