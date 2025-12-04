import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.sched_page import SchedPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_materialSched():
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
        page.click_button('(//span[text()="计划运行"])[1]')  # 点击计划运行
        page.click_button('(//span[text()="方案管理"])[1]')  # 点击方案管理
        page.click_button('(//span[text()="物控方案管理"])[1]')  # 点击物控方案管理
        page.wait_for_el_loading_mask()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("物控方案管理表测试用例")
@pytest.mark.run(order=142)
class TestMaterialSchedPage:
    @allure.story("添加物控方案管理信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialsched_addfail1(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        sched.click_add_schedbutton()  # 点击添加方案

        sched.click_ok_schedbutton()  # 点击确定
        message = sched.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请输入"
        assert not sched.has_fail_message()

    @allure.story("添加物控方案管理信息 只填写复制方案 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialsched_addfail2(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        sched.click_add_schedbutton()  # 点击添加方案
        sched.click_button(
            '//label[text()="选择复制的方案"]/following-sibling::div/div'
        )  # 点击下拉框
        sched.click_button('//div[label[text()="选择复制的方案"]]//ul[@class="ivu-select-dropdown-list"]/li[1]')

        sched.click_ok_schedbutton()  # 点击确定
        message = sched.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请输入"
        assert not sched.has_fail_message()

    @allure.story("添加物控方案管理信息 添加重复 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialsched_addrepeat(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        sched.wait_for_el_loading_mask()
        ele = sched.get_find_element_xpath(
            '//div[@class="h-69 background-ffffff"]//label[1]'
        ).text

        sched.click_add_schedbutton()  # 点击添加方案
        sched.enter_texts(
            '//label[text()="名称"]/following-sibling::div//input', ele
        )

        sched.click_ok_schedbutton()  # 点击确定
        message = sched.get_error_message()
        # 检查元素是否包含子节点
        assert message == "物控方案已存在"
        assert not sched.has_fail_message()

    @allure.story("添加复制方案成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_addrepeatsuccess(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        sched.wait_for_el_loading_mask()
        ele = sched.get_find_element_xpath(
            '//div[@class="h-69 background-ffffff"]//label[1]'
        ).text

        sched.click_add_schedbutton()  # 点击添加方案
        name = "22"
        sched.enter_texts(
            '//label[text()="名称"]/following-sibling::div//input', f"{name}"
        )

        sched.click_button(
            '//label[text()="选择复制的方案"]/following-sibling::div/div'
        )  # 点击下拉框
        sched.click_button(f'//li[text()="{ele}"]')
        sched.click_ok_schedbutton()  # 点击确定
        sched.click_save_button()  # 点击保存
        sleep(1)

        element = driver.find_element(
            By.XPATH, f'//span[span[text()="{name}"]]/preceding-sibling::span'
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # 判断下拉框为打开还是关闭
        sleep(1)
        sel = sched.get_find_element_xpath(
            f'//span[span[text()="{name}"]]/preceding-sibling::span'
        )
        if "ivu-tree-arrow" in sel.get_attribute("class"):
            sched.click_button(f'//span[span[text()="{name}"]]/preceding-sibling::span')

        addtext = sched.get_find_element_xpath(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[last()]'
        )
        addtext1 = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/span[2]'
        )
        addul = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        assert addtext.text == name and addtext1.text == name and len(addul) > 0
        assert not sched.has_fail_message()

    @allure.story("删除刚才添加的方案")
    # @pytest.mark.run(order=1)
    def test_materialsched_delsched1(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        # 选中为22的方案
        sched.click_button(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="22"]'
        )
        sched.click_del_schedbutton()  # 点击删除
        sched.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[2]')

        # 点击保存
        sched.click_save_button()
        ele = sched.finds_elements(
            By.XPATH,
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="22"]',
        )
        assert len(ele) == 0
        assert not sched.has_fail_message()

    @allure.story("添加方案成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_addsuccess(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        sched.click_add_schedbutton()  # 点击添加方案
        sched.enter_texts('//label[text()="名称"]/following-sibling::div//input', "33")
        sched.click_ok_schedbutton()  # 点击确定
        sched.click_save_button()  # 点击保存
        sleep(1)
        addtext = sched.get_find_element_xpath(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[last()]'
        )
        addtext1 = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/span[2]'
        )
        addul = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        assert addtext.text == "33" and addtext1.text == "33" and len(addul) == 0
        assert not sched.has_fail_message()

    @allure.story("没有选中行 添加命令 不允许添加")
    # @pytest.mark.run(order=1)
    def test_materialsched_addcommandfail(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        sched.wait_for_el_loading_mask()

        # 选中命令点击添加
        sched.click_button(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[1]/label[1]'
        )
        ele = sched.get_find_element_xpath('//button[i[@class="ivu-icon ivu-icon-md-add"]]')
        sleep(1)
        assert not ele.is_enabled()
        assert not sched.has_fail_message()

    @allure.story("添加命令成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_addcommandsuccess(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        # 选中命令点击添加
        addul1 = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        # 第一个命令 xpth
        command = '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[1]/label[1]'
        sched.click_button(command)
        command_text = sched.get_find_element_xpath(command)

        element = driver.find_element(
            By.XPATH, '//span[span[text()="33"]]/preceding-sibling::span'
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # 选中33方案
        sched.click_button(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/span[2]'
        )
        driver.execute_script("window.scrollTo(0, 0);")
        sched.click_add_commandbutton()
        sched.click_save_button()
        addul2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]',
                )
            )
        )
        # 判断添加前列表为空 ，添加后命令相同
        sleep(1)
        assert len(addul1) == 0 and addul2.text == command_text.text
        assert not sched.has_fail_message()

    @allure.story("删除命令成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_delcommandsuccess(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        while True:
            sleep(1)
            addul1 = driver.find_elements(
                By.XPATH,
                '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]//span[2]',
            )
            if not addul1:
                break  # 没有找到元素时退出循环
                # 存在元素，点击删除按钮
            element = driver.find_element(
                By.XPATH, '//span[span[text()="33"]]/preceding-sibling::span'
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            addul1[0].click()
            driver.execute_script("window.scrollTo(0, 0);")
            sched.click_del_commandbutton()
            sched.click_ok_schedbutton()

        # 再次确认，元素已删除
        sched.click_save_button()
        addul1_after = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        sleep(1)
        assert len(addul1_after) == 0
        assert not sched.has_fail_message()

    @allure.story("添加2个命令成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_addcommandsuccess2(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        # 选中命令点击添加
        addul1 = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        # 第一个命令 xpth
        command = '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[1]/label'
        command_text = driver.find_elements(By.XPATH, command)
        command_text[0].click()

        element = driver.find_element(
            By.XPATH, '//span[span[text()="33"]]/preceding-sibling::span'
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # 选中33方案
        sched.click_button(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/span[2]'
        )
        driver.execute_script("window.scrollTo(0, 0);")
        sched.click_add_commandbutton()

        # 添加第二个命令
        command_text[1].click()
        sched.click_add_commandbutton()

        sched.click_save_button()
        addul2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                # 查找第一个命令
                (
                    By.XPATH,
                    '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]',
                )
            )
        )
        addul3 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                # 查找第二个命令
                (
                    By.XPATH,
                    '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[2]',
                )
            )
        )
        sleep(1)
        # 判断刚开始的命令为0，并且添加的两个命令名称都相等
        assert (
            len(addul1) == 0
            and addul2.text == command_text[0].text
            and addul3.text == command_text[1].text
        )
        assert not sched.has_fail_message()

    @allure.story("向上移动命令")
    # @pytest.mark.run(order=1)
    def test_materialsched_upcommand(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        sched.wait_for_el_loading_mask()
        command = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[2]//span[2]'
        ).text

        element = driver.find_element(
            By.XPATH, '//span[span[text()="33"]]/preceding-sibling::span'
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # 选中第二个命令
        sched.click_button(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[2]//span[2]'
        )
        driver.execute_script("window.scrollTo(0, 0);")
        sched.click_up_commandbutton()
        sched.click_save_button()
        sleep(1)
        after_command = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]//span[2]'
        ).text
        assert command == after_command
        assert not sched.has_fail_message()

    @allure.story("向下移动命令")
    # @pytest.mark.run(order=1)
    def test_materialsched_downcommand(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        sched.wait_for_el_loading_mask()
        command = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]//span[2]'
        ).text
        # 选中第一个命令
        sched.click_button(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[1]//span[2]'
        )
        driver.execute_script("window.scrollTo(0, 0);")
        sched.click_down_commandbutton()
        sched.click_save_button()
        sleep(2)
        after_command = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul[2]//span[2]'
        ).text
        assert command == after_command
        assert not sched.has_fail_message()

    @allure.story("删除刚才添加的方案")
    # @pytest.mark.run(order=1)
    def test_materialsched_delsched2(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage

        # 选中为33的方案
        sched.click_button(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="33"]'
        )
        sched.click_del_schedbutton()  # 点击删除
        sched.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[2]')

        # 点击保存
        sched.click_save_button()
        ele = driver.find_elements(
            By.XPATH,
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="22"]',
        )
        assert len(ele) == 0
        assert not sched.has_fail_message()

    @allure.story("添加复制测试方案成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_addrepeatsuccess1(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        ele = sched.get_find_element_xpath(
            '//div[@class="h-69 background-ffffff"]//label[1]'
        ).text
        sched.click_add_schedbutton()  # 点击添加方案
        name = "排产方案(订单级)复制"
        sched.enter_texts(
            '//label[text()="名称"]/following-sibling::div//input', f"{name}"
        )

        sched.click_button(
            '//label[text()="选择复制的方案"]/following-sibling::div/div'
        )  # 点击下拉框
        sched.click_button(f'//li[text()="{ele}"]')
        sched.click_ok_schedbutton()  # 点击确定
        sched.click_save_button()  # 点击保存
        sleep(1)

        element = driver.find_element(
            By.XPATH, f'//span[span[text()="{name}"]]/preceding-sibling::span'
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # 判断下拉框为打开还是关闭
        sleep(1)
        sel = sched.get_find_element_xpath(
            f'//span[span[text()="{name}"]]/preceding-sibling::span'
        )
        if "ivu-tree-arrow" in sel.get_attribute("class"):
            sched.click_button(f'//span[span[text()="{name}"]]/preceding-sibling::span')

        addtext = sched.get_find_element_xpath(
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[last()]'
        )
        addtext1 = sched.get_find_element_xpath(
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/span[2]'
        )
        addul = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-tree-children" and @visible="visible"]/li/ul[last()]/li/ul',
        )
        assert addtext.text == name and addtext1.text == name and len(addul) > 0
        assert not sched.has_fail_message()

    @allure.story("齐套供应设置-公共数据计划单元，物料需求计算公式，需求源选择及数据过滤，供应源选择及数据过滤选择成功")
    # @pytest.mark.run(order=1)
    def test_materialsched_attribute1(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        adds = AddsPages(driver)
        name = "排产方案(订单级)复制"
        # 选择排产方案(订单级)复制方案
        sched.click_button(f'//ul[@visible="visible"]//ul//span[text()="{name}"]')
        sched.click_attribute_button()
        select_list = [
            {"select": '//div[div[text()="公共数据计划单元 "]]//input[@class="ivu-select-input"]', "value": '//div[div[text()="公共数据计划单元 "]]//ul[@class="ivu-select-dropdown-list"]/li[1]'},
            {"select": '//div[div[text()="物料需求计算公式 "]]//input[@class="ivu-select-input"]', "value": '//div[div[text()="物料需求计算公式 "]]//ul[@class="ivu-select-dropdown-list"]/li[1]'},
        ]
        adds.batch_modify_select_input(select_list)

        text_list = [
            '//div[div[text()="供应源选择及数据过滤 "]]/div[2]',
            '//div[div[text()="需求源选择及数据过滤 "]]/div[2]',
        ]
        sched.batch_sched_dialog_box(text_list)


        sleep(2)
        # 提取 select_list 中的 select 字段
        select_only = [item["select"] for item in select_list]
        before_all_value1 = adds.batch_acquisition_input(select_only)
        before_all_value2 = adds.batch_acquisition_text(text_list)
        all_value1 = [before_all_value1, before_all_value2]

        sched.click_button('//div[text()=" 齐套指标输出 "]')
        sched.click_button('//div[div[text()="用户自定义指标项输出 "]]/div[2]')
        ele = sched.get_find_element_xpath(
            '//label[span[text()=" 1.常规齐套率 "]]/span[1]'
        ).get_attribute('class')
        if 'is--checked' not in ele:
            sched.click_button('//label[span[text()=" 1.常规齐套率 "]]/span[1]')
        sched.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[4]')
        sleep(1)
        before_value = sched.get_find_element_xpath('//div[div[text()="用户自定义指标项输出 "]]/div[2]').text

        sched.get_after_value(name)
        sleep(2)
        before_all_value1 = adds.batch_acquisition_input(select_only)
        before_all_value2 = adds.batch_acquisition_text(text_list)
        all_value2 = [before_all_value1, before_all_value2]

        sched.click_button('//div[text()=" 齐套指标输出 "]')
        after_value = sched.get_find_element_xpath('//div[div[text()="用户自定义指标项输出 "]]/div[2]').text
        assert all_value1 == all_value2 and after_value in before_value
        assert not sched.has_fail_message()

    @allure.story("删除测试方案")
    # @pytest.mark.run(order=1)
    def test_materialsched_delsched3(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        name = ["排产方案(订单级)复制"]
        sched.del_all_sched(name)
        ele = driver.find_elements(
            By.XPATH,
            '(//div[@class="ivu-radio-group ivu-radio-group-small ivu-radio-small ivu-radio-group-button"])[2]/label[text()="22"]',
        )
        assert len(ele) == 0
        assert not sched.has_fail_message()

    @allure.story("添加复制测试方案，配置同步使用")
    # @pytest.mark.run(order=1)
    def test_materialsched_addrepeatsuccess2(self, login_to_materialSched):
        driver = login_to_materialSched  # WebDriver 实例
        sched = SchedPage(driver)  # 用 driver 初始化 SchedPage
        name = [
            "物控方案(订单级)同步1",
            "物控方案(订单级)同步2",
            "物控方案(订单级)同步3",
        ]
        sched.add_copy_materialsched(name)
        eles = sched.finds_elements(By.XPATH, '//span[@class="ivu-tree-title"]')
        all_texts = [ele.text for ele in eles]
        assert all(n in all_texts for n in name), f"不是所有名称都存在。现有的元素: {all_texts}"
        assert not sched.has_fail_message()
