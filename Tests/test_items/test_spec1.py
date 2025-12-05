import logging
import random
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.spec1_page import Spec1Page
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_spec1():
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
        page.click_button('(//span[text()="计划生产特征"])[1]')  # 点击计划生产特征
        page.click_button('(//span[text()="生产特征1"])[1]')  # 点击生产特征1
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("生产特征表测试用例")
@pytest.mark.run(order=2)
class TestSpecPage:
    @allure.story("添加生产特征信息 不填写数据点击确认 不允许提交，添加新布局")
    # @pytest.mark.run(order=1)
    def test_spec_addfail(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        layout = "测试布局A"
        spec.add_layout(layout)
        name = spec.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        spec.click_add_button()
        # 代码xpath
        input_box = spec.get_find_element_xpath(
            '(//label[text()="代码"])[1]/parent::div//input'
        )
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        border_color = input_box.value_of_css_property("border-color")
        expected_color = "rgb(237, 64, 20)"  # 红色的 rgb 值
        assert (
            border_color == expected_color
        ), f"预期边框颜色为{expected_color}, 但得到{border_color}"
        assert layout == name
        assert not spec.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_spec_addnum(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        spec.click_add_button()  # 检查点击添加
        ele = spec.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        # 数值特征数字框输入文字字母符号数字
        spec.enter_texts(
            '(//label[text()="显示顺序"])[1]/parent::div//input', "e1文字abc。.？~1_2+=3"
        )
        sleep(1)
        # 获取显示顺序数字框
        specnum = spec.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        ).get_attribute("value")
        assert specnum == "1123", f"预期{specnum}"
        assert not spec.has_fail_message()

    @allure.story("下拉框选择成功")
    # @pytest.mark.run(order=1)
    def test_spec_addsel(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        spec.click_add_button()  # 检查点击添加
        # 显示颜色下拉框
        spec.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        # 显示颜色
        spec.click_button('//span[text()="RGB(100,255,178)"]')
        # 获取下拉框数据
        specsel = spec.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text
        assert specsel == "2", f"预期{specsel}"
        assert not spec.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_spec_textverify(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "1111111111111111333311222211112222211111111133331111111444441111111111111111111111111111111111111111"
        spec.click_add_button()  # 检查点击添加
        # 输入代码
        spec.enter_texts('(//label[text()="代码"])[1]/parent::div//input', name)
        spec.enter_texts('(//label[text()="名称"])[1]/parent::div//input', name)
        spec.enter_texts('(//label[text()="显示顺序"])[1]/parent::div//input', name)
        # 点击确定
        spec.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        spec.wait_for_loading_to_disappear()
        adddata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        num_ = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[5]'
        ).text
        assert adddata == name and num_ == '9999999999',f"预期数据是{name}，实际得到{adddata}"
        assert not spec.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_spec_addsuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "111"
        spec.add_spec_data(name)
        adddata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是111，实际得到{adddata}"
        assert not spec.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_spec_addrepeat(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "111"
        spec.add_spec_data(name)
        # 获取重复弹窗文字
        error_popup = spec.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not spec.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_spec_delcancel(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "111"
        # 定位内容为‘111’的行
        spec.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        spec.click_del_button()  # 点击删除
        # 点击取消
        spec.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        # 定位内容为‘111’的行
        itemdata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert itemdata == name, f"预期{itemdata}"
        assert not spec.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_spec_addsuccess1(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "1测试A"
        spec.click_add_button()  # 检查点击添加
        # 输入代码
        spec.enter_texts('(//label[text()="代码"])[1]/parent::div//input', name)
        spec.enter_texts('(//label[text()="名称"])[1]/parent::div//input', name)
        # 显示颜色下拉框
        spec.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        # 显示颜色
        spec.click_button('//span[text()="RGB(100,255,178)"]')
        ele = spec.get_find_element_xpath(
            '(//label[text()="显示顺序"])[1]/parent::div//input'
        )
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        # 显示顺序框输入文字字母符号数字
        spec.enter_texts(
            '(//label[text()="显示顺序"])[1]/parent::div//input', "20"
        )
        # 点击确定
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        spec.wait_for_loading_to_disappear()
        adddata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert adddata == name, f"预期数据是1测试A，实际得到{adddata}"
        assert not spec.has_fail_message()

    @allure.story("修改代码重复")
    # @pytest.mark.run(order=1)
    def test_spec_editrepeat(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 选中1测试A物料代码
        spec.click_button('//tr[./td[2][.//span[text()="1测试A"]]]/td[2]')
        # 点击修改按钮
        spec.click_edi_button()
        # 物料代码输入111
        spec.enter_texts('(//label[text()="代码"])[1]/parent::div//input', "111")
        # 点击确定
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = spec.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not spec.has_fail_message()

    @allure.story("修改代码成功")
    # @pytest.mark.run(order=1)
    def test_spec_editcodesuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "1测试A"
        # 选中1测试A代码
        spec.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        spec.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 物料代码输入
        spec.enter_texts(
            '(//label[text()="代码"])[1]/parent::div//input', f"{text}"
        )
        # 点击确定
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        spec.wait_for_loading_to_disappear()
        # 定位表格内容
        specdata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]'
        ).text
        assert specdata == text, f"预期{specdata}"
        assert not spec.has_fail_message()

    @allure.story("把修改后的代码改回来")
    # @pytest.mark.run(order=1)
    def test_spec_editcodesuccess2(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "1测试A"
        # 选中1测试A代码
        spec.click_button(f'//tr[./td[2][.//span[contains(text(),"{name}")]]]/td[2]')
        # 点击修改按钮
        spec.click_edi_button()
        # 代码输入
        spec.enter_texts('(//label[text()="代码"])[1]/parent::div//input', name)
        # 点击确定
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        spec.wait_for_loading_to_disappear()
        # 定位表格内容
        specdata = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]'
        ).text
        assert specdata == name, f"预期{specdata}"
        assert not spec.has_fail_message()

    @allure.story("修改名称，显示颜色成功")
    # @pytest.mark.run(order=1)
    def test_spec_editnamesuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "1测试A"
        # 选中代码
        spec.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        # 点击修改按钮
        spec.click_edi_button()
        sleep(1)
        # 生成随机数
        random_int = random.randint(1, 10)
        text = name + f"{random_int}"
        # 输入修改的物料名称
        spec.enter_texts(
            '(//label[text()="名称"])[1]/parent::div//input', f"{text}"
        )
        # 获取修改好的值
        editname = spec.get_find_element_xpath(
            '(//label[text()="名称"])[1]/parent::div//input'
        ).get_attribute("value")

        # 修改显示颜色下拉框
        spec.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        sleep(0.5)
        spec.click_button('(//label[text()="显示颜色"])[1]/parent::div//i')
        # 显示颜色
        spec.click_button('//span[text()="RGB(242,128,255)"]')
        # 获取下拉框数据
        specsel = spec.get_find_element_xpath(
            '//div[label[text()="显示颜色"]]/div//span[@class="ivu-select-selected-value"]'
        ).text
        # 点击确定
        spec.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        spec.wait_for_loading_to_disappear()
        # 定位表格内容
        itemname = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[3]/div'
        ).text
        color = spec.get_find_element_xpath(
            f'//tr[./td[2][.//span[text()="{name}"]]]/td[4]/div'
        ).text
        sleep(1)
        assert (
            itemname == editname
            and specsel == color
        )
        assert not spec.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_spec_refreshsuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 代码筛选框输入123
        spec.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', "123"
        )
        spec.click_ref_button()
        spectext = spec.get_find_element_xpath(
            '//p[text()="代码"]/ancestor::div[2]//input'
        ).text
        assert spectext == "", f"预期{spectext}"
        assert not spec.has_fail_message()

    @allure.story("查询代码成功")
    # @pytest.mark.run(order=1)
    def test_spec_selectcodesuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        name = "111"
        # 点击查询
        spec.click_sel_button()
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
        spec.click_button('//div[text()="代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        spec.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        spec.click_select_button()
        sleep(1)
        # 定位第一行是否为111
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == name and len(speccode2) == 0
        assert not spec.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_spec_selectnodatasuccess(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 点击查询
        spec.click_sel_button()
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
        # 点击代码
        spec.click_button('//div[text()="代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        spec.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        spec.click_select_button()
        itemcode = driver.find_elements(
            By.XPATH,
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]',
        )
        assert len(itemcode) == 0
        assert not spec.has_fail_message()

    @allure.story("查询显示顺序>10")
    # @pytest.mark.run(order=1)
    def test_spec_selectsuccess1(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 点击查询
        spec.click_sel_button()
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
        # 点击显示顺序
        spec.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        spec.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "10",
        )
        sleep(1)

        # 点击确认
        spec.click_select_button()
        # 定位第一行显示顺序
        speccode = spec.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        assert len(speccode) > 0
        assert all(int(code) > 10 for code in speccode)
        assert not spec.has_fail_message()

    @allure.story("查询名称包含1并且显示顺序>10")
    # @pytest.mark.run(order=1)
    def test_spec_selectsuccess2(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 点击查询
        spec.click_sel_button()
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
        spec.click_button('//div[text()="名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        spec.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        spec.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "1",
        )

        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        spec.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        spec.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击显示顺序
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        spec.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        spec.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            "10",
        )
        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        spec.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        spec.click_select_button()
        specname = spec.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[3]')
        speccode = spec.loop_judgment('(//table[@class="vxe-table--body"])[2]//tr/td[5]')
        assert len(specname) > 0 and len(speccode) > 0
        assert all(int(code) > 10 for code in speccode) and all(
            "1" in name for name in specname
        )
        assert not spec.has_fail_message()

    @allure.story("以普开头或显示顺序>10")
    # @pytest.mark.run(order=1)
    def test_spec_selectsuccess3(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page

        # 点击查询
        spec.click_sel_button()
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
        # 点击名称
        spec.click_button('//div[text()="名称" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[3]'
        )
        spec.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击包含
        spec.click_button('//div[text()="Begins with" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "普",
        )

        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[7]'
        )
        spec.click_button('//div[text()=")" and contains(@optid,"opt_")]')

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
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[3]'
        )
        spec.click_button('//div[text()="(" and contains(@optid,"opt_")]')
        # 点击显示顺序
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[4]'
        )
        spec.click_button('//div[text()="显示顺序" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[5]//input'
        )
        # 点击>
        spec.click_button('//div[text()=">" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值10
        spec.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[6]//input',
            "10",
        )
        # 点击（
        spec.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[2]/td[7]'
        )
        spec.click_button('//div[text()=")" and contains(@optid,"opt_")]')

        sleep(1)

        # 点击确认
        spec.click_select_button()
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
                td5_val = int(td5_raw) if td5_raw else 0

                assert "普" in td3 or td5_val > 10, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1

            except StaleElementReferenceException:
                # 如果行元素失效，再重试一次
                row = driver.find_elements(By.XPATH, xpath_rows)[idx]
                tds = row.find_elements(By.TAG_NAME, "td")
                td3 = tds[2].text.strip()
                td5_raw = tds[4].text.strip()
                td5_val = int(td5_raw) if td5_raw else 0
                assert "普" in td3 or td5_val > 10, f"第 {idx + 1} 行不符合：td3={td3}, td5={td5_raw}"
                valid_count += 1
        assert not spec.has_fail_message()
        print(f"符合条件的行数：{valid_count}")

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_spec_addall(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        data_list = ["全部数据", "20"]
        spec.click_add_button()  # 检查点击添加
        spec.add_input_all(data_list[0], data_list[1])
        sleep(1)
        spec.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', data_list[0]
        )
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{data_list[0]}"]]]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = ['全部数据', '全部数据', '2', '20', '全部数据', f'{DateDriver().username}', '2025', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text)):
            if i == 6:
                assert str(e) in str(a), f"第7项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not spec.has_fail_message()

    @allure.story("重新打开浏览器，数据还存在")
    # @pytest.mark.run(order=1)
    def test_spec_restart(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        code = '全部数据'
        spec.enter_texts(
            '//p[text()="代码"]/ancestor::div[2]//input', code
        )
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = f'//tr[./td[2][.//span[text()="{code}"]]]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)
                text = td.text.strip()
                columns_text.append(text)

        print(columns_text)
        bef_text = ['全部数据', '全部数据', '2', '20', '全部数据', f'{DateDriver().username}', '2025', '20', '20', '20',
                    '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20',
                    '20', '20']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text)):
            if i == 6:
                assert str(e) in str(a), f"第7项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not spec.has_fail_message()

    @allure.story("删除测试数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_spec_delsuccess1(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        layout = "测试布局A"

        value = ['全部数据', '111', '1测试A', '1111111111111111333311222211112222211111111133331111111444441111111111111111111111111111111111111111']
        spec.del_all(value, '//p[text()="代码"]/ancestor::div[2]//input')
        data = [
            driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:4]
        ]
        spec.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert all(len(elements) == 0 for elements in data)
        assert 0 == len(after_layout)
        assert not spec.has_fail_message()

    @allure.story("生产特征2增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec2(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征22', '1测试生产特征2']
        after_name = '1修改生产特征22'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(2)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征3增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec3(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征33', '1测试生产特征3']
        after_name = '1修改生产特征33'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(3)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征4增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec4(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征44', '1测试生产特征4']
        after_name = '1修改生产特征44'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(4)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征5增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec5(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征55', '1测试生产特征5']
        after_name = '1修改生产特征55'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(5)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征6增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec6(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征66', '1测试生产特征6']
        after_name = '1修改生产特征66'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(6)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征7增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec7(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征77', '1测试生产特征7']
        after_name = '1修改生产特征77'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(7)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征8增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec8(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征88', '1测试生产特征8']
        after_name = '1修改生产特征88'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(8)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征9增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec9(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征99', '1测试生产特征9']
        after_name = '1修改生产特征99'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(9)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()

    @allure.story("生产特征10增删查改")
    # @pytest.mark.run(order=1)
    def test_spec_spec10(self, login_to_spec1):
        driver = login_to_spec1  # WebDriver 实例
        spec = Spec1Page(driver)  # 用 driver 初始化 Spec1Page
        list_name = ['1测试生产特征100', '1测试生产特征10']
        after_name = '1修改生产特征10'
        spec.click_button('//div[text()=" 生产特征1 "]')
        spec.click_button('//div[div[text()=" 生产特征1 "]]/span')
        spec.click_spec_num(10)
        add1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
        add2 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        add3 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(add2) == 0:
            spec.add_spec_data(list_name[1])
        if len(add1) == 0 and len(add3) == 0:
            spec.add_spec_data(list_name[0])
            ele0 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[0]}"]]]/td[2]')
            assert len(ele0) == 1
        ele1 = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{list_name[1]}"]]]/td[2]')
        assert len(ele1) == 1

        edit = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        if len(edit) == 0:
            spec.edit_spec_data(list_name[0], after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 1

        spec.select_spec_data(after_name)
        speccode = spec.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]//tr[@class="vxe-body--row"][1]/td[2]'
        ).text
        # 定位第二行没有数据
        speccode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][2]/td[2]',
        )
        assert speccode == after_name and len(speccode2) == 0

        spec.del_spec_data(after_name)
        ele = spec.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{after_name}"]]]/td[2]')
        assert len(ele) == 0

        ele = spec.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not spec.has_fail_message()
