import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.production_page import ProductionPage
from Utils.data_driven import DateDriver
from Utils.shared_data_util import SharedDataUtil
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_production():
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
        page.click_button('(//span[text()="生产报工"])[1]')  # 点击生产报工
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("生产报工测试用例")
@pytest.mark.run(order=24)
class TestProductionPage:

    @allure.story("添加布局")
    # @pytest.mark.run(order=1)
    def test_production_addlayout(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        layout = "测试布局A"
        production.add_layout(layout)
        # 获取布局名称的文本元素
        name = production.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        assert layout == name
        assert not production.has_fail_message()

    @allure.story("添加工作代码 直接点击确定 不允许提交")
    # @pytest.mark.run(order=1)
    def test_production_addfail1(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()

        # 点击提交按钮
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

        # 获取提示信息
        message = production.get_error_message()
        # 断言提示信息为“请先填写表单”
        assert message == "请先填写表单"
        assert not production.has_fail_message()

    @allure.story("添加工作代码 不填写报告数量 不允许提交")
    # @pytest.mark.run(order=1)
    def test_production_addfail2(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()
        name = "1测试C订单"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )
        # 选择搜索到的第一个订单“1测试C订单”
        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:1"]]]//td[3]//span[text()="{name}:1"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')

        sleep(1)
        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容

        # 点击提交按钮
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

        # 获取提示信息
        message = production.get_error_message()
        # 断言提示信息为“请先填写表单”
        assert message == "请先填写表单"
        assert not production.has_fail_message()

    @allure.story("添加工作代码 修改资源会弹出提示，并且表格颜色发生改变")
    # @pytest.mark.run(order=1)
    def test_production_editresource(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        production.click_add_button()

        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )
        # 选择搜索到的第一个订单“1测试C订单”
        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:1"]]]//td[3]//span[text()="{name}:1"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')

        sleep(1)
        # 定位输入框元素
        production.click_button(
            '//label[text()="报工资源"]/following-sibling::div//input[@type="text"]'
        )
        input_sel = production.get_find_element_xpath(
            '//label[text()="报工资源"]/following-sibling::div//input[@type="text"]'
        ).get_attribute("value")
        eles = driver.find_elements(
            By.XPATH,
            '//ul[@class="ivu-select-dropdown-list"and .//span[contains(text(),"/")]]/li',
        )
        eles[0].click()
        afert_input = production.get_find_element_xpath(
            '//label[text()="报工资源"]/following-sibling::div//input[@type="text"]'
        ).get_attribute("value")
        i = 0
        # 循环点击，直到输入框内容发生变化
        while afert_input == input_sel:
            i += 1
            eles[i].click()
            afert_input = production.get_find_element_xpath(
                '//label[text()="报工资源"]/following-sibling::div//input[@type="text"]'
            ).get_attribute("value")

        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 弹出提示框 点击是
        production.click_button(
            '//div[.//p[text()="当前选择的报工资源与资源代码不一致，是否继续？"] and @class="el-message-box__content"]/following-sibling::div/button[2]'
        )
        production.wait_for_loading_to_disappear()
        color = production.get_find_element_xpath(
            '//tr[./td[9]//span[text()="1测试C订单"]]/td[4]'
        ).value_of_css_property("background-color")
        # 断言提示信息为“请先填写表单”
        assert color == "rgba(255, 165, 0, 1)"
        assert not production.has_fail_message()

    @allure.story("删除数据")
    # @pytest.mark.run(order=1)
    def test_production_delete(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        production.click_button(f'//tr[./td[9]//span[text()="{name}"]]/td[4]')
        production.click_del_button()

        production.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        production.wait_for_loading_to_disappear()
        ele = driver.find_elements(By.XPATH, f'//tr[./td[9]//span[text()="{name}"]]')

        assert len(ele) == 0
        assert not production.has_fail_message()

    @allure.story("添加生产报工成功")
    # @pytest.mark.run(order=1)
    def test_production_add1(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()
        name = "1测试C订单"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )
        # 选择搜索到的第一个订单“1测试C订单”
        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:1"]]]//td[3]//span[text()="{name}:1"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        production.wait_for_loading_to_disappear()
        ele1 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:1"]]/td[9]'
        )
        ele2 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:1"]]/td[2]'
        )
        # 断言提示信息为“请先填写表单”
        assert ele1.text == name and ele2.text == f"{name}:1"
        assert not production.has_fail_message()

    @allure.story(
        "添加生产报工完成，继续添加同一个生产报工输入报告数量会弹出提示并且实绩状态变为结束"
    )
    # @pytest.mark.run(order=1)
    def test_production_add2(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()
        name = "1测试C订单"
        num = "100"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )
        sleep(1)
        # 选择搜索到的第一个订单“1测试C订单”
        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:1"]]]//td[3]//span[text()="{name}:1"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')

        sleep(1)
        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input', num
        )

        # 点击提交按钮
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 获取提示信息
        sleep(1)
        message = production.get_find_element_xpath(
            '//p[text()="当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"]'
        ).text
        production.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="是"]')
        production.wait_for_loading_to_disappear()

        ele = production.get_find_element_xpath(
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]'
        ).text
        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:1"]]/td[10]'
        )
        # 断言提示信息为“请先填写表单”
        assert (
            message == "当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"
            and ele == num
            and after_text.text == "结束"
        )
        assert not production.has_fail_message()

    @allure.story(
        "弹出是否删除工作，点击取消不会删除数据"
    )
    # @pytest.mark.run(order=1)
    def test_production_canceldelete(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "100"
        production.click_button(
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]'
        )
        production.click_del_button()
        sleep(1)
        text = production.get_find_element_xpath(
            '//p[text()="当前工作已【结束】，是否需要修改成【开始生产】？"]'
        ).text
        # 点击是
        production.click_button('//div[@class="el-message-box__header"]/button')
        sleep(1)
        ele = driver.find_elements(
            By.XPATH,
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]',
        )
        assert (
                text == "当前工作已【结束】，是否需要修改成【开始生产】？"
                and len(ele) == 1
        )
        assert not production.has_fail_message()

    @allure.story(
        "删除超出的报工数量点击删除弹出弹窗，点击是报工状态会变为开始生产，数据会删除"
    )
    # @pytest.mark.run(order=1)
    def test_production_delete1(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "100"
        production.click_button(
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]'
        )
        production.click_del_button()
        text = production.get_find_element_xpath(
            '//p[text()="当前工作已【结束】，是否需要修改成【开始生产】？"]'
        ).get_attribute('innerText')
        # 点击是
        production.click_button('//div[@class="el-message-box__btns"]/button[2]')
        sleep(1)
        ele = driver.find_elements(
            By.XPATH,
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]',
        )
        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:1"]]/td[10]'
        )
        assert (
            text == "当前工作已【结束】，是否需要修改成【开始生产】？"
            and len(ele) == 0
            and after_text.text == "开始生产"
        )
        assert not production.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_production_add3(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()
        name = "1测试C订单"
        num = "100"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )
        sleep(1)
        # 选择搜索到的第一个订单“1测试C订单”
        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:1"]]]//td[3]//span[text()="{name}:1"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')

        sleep(1)
        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input', num
        )

        # 点击提交按钮
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 获取提示信息
        sleep(1)
        message = production.get_find_element_xpath(
            '//p[text()="当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"]'
        ).text
        production.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="是"]')
        production.wait_for_loading_to_disappear()
        ele = production.get_find_element_xpath(
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]'
        ).text
        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:1"]]/td[10]'
        )
        # 断言提示信息为“请先填写表单”
        assert (
            message == "当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"
            and ele == num
            and after_text.text == "结束"
        )
        assert not production.has_fail_message()

    @allure.story(
        "删除超出的报工数量点击删除弹出弹窗，点击否报工状态不会发生变化还是结束状态，但是数据会删除"
    )
    # @pytest.mark.run(order=1)
    def test_production_delete2(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "100"
        production.click_button(
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]'
        )
        production.click_del_button()
        sleep(1)
        text = production.get_find_element_xpath(
            '//p[text()="当前工作已【结束】，是否需要修改成【开始生产】？"]'
        ).text
        # 点击否
        production.click_button('//div[@class="el-message-box__btns"]/button[1]')
        production.wait_for_loading_to_disappear()
        ele = driver.find_elements(
            By.XPATH,
            f'//tr[./td[6]//span[text()="{num}"] and ./td[2]//span[text()="{name}:1"]]/td[6]',
        )
        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:1"]]/td[10]'
        )
        assert (
            text == "当前工作已【结束】，是否需要修改成【开始生产】？"
            and len(ele) == 0
            and after_text.text == "结束"
        )
        assert not production.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_production_textverify(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        production.click_add_button()
        name = "1测试C订单"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )

        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:2"]]]//td[3]//span[text()="{name}:2"]'
        )
        # 点击确认按钮
        production.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input',
            num,
        )
        production.enter_texts(
            '//label[text()="异常原因"]/following-sibling::div//input',
            num,
        )
        production.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        production.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="返回"]')
        num_ = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        ).get_attribute("value")
        text_ = production.get_find_element_xpath(
            '//label[text()="异常原因"]/following-sibling::div//input'
        ).get_attribute("value")
        assert num_ == '9999999999' and text_ == num
        assert not production.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_production_add4(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_add_button()
        name = "1测试C订单"
        # 点击工作代码对话框
        production.click_button('//label[text()="工作代码"]/following-sibling::div//i')
        # 在订单代码输入框中输入“1测试C订单”
        production.enter_texts(
            '(//div[./p[text()="订单代码"]])[2]/parent::div//input',
            name,
        )

        production.click_button(
            f'//table[.//tr[./td[3]//span[text()="{name}:2"]]]//td[3]//span[text()="{name}:2"]'
        )
        # 点击确认按钮
        production.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        production.wait_for_loading_to_disappear()
        ele1 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[9]'
        )
        ele2 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[2]'
        )
        # 断言提示信息为“请先填写表单”
        assert ele1.text == name and ele2.text == f"{name}:2"
        assert not production.has_fail_message()

    @allure.story("数字文本框只允许输入数字")
    # @pytest.mark.run(order=1)
    def test_production_editnum(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        production.click_button(f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]')
        production.click_edi_button()
        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        sleep(1)
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input',
            "e1+2=。，、.？w’；6",
        )
        assert input_num.get_attribute("value") == "126"
        assert not production.has_fail_message()

    @allure.story("选择下拉框成功，将开始生产改为结束")
    # @pytest.mark.run(order=1)
    def test_production_editsele(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        production.click_button(f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]')
        production.click_edi_button()

        before_input = production.get_find_element_xpath(
            '//label[text()="实绩状态"]/following-sibling::div//input'
        ).get_attribute("value")
        production.click_button('//label[text()="实绩状态"]/following-sibling::div//i')
        production.click_button(
            '//ul[@class="ivu-select-dropdown-list" and ./li[text()="结束"]]/li[text()="结束"]'
        )
        afert_input = production.get_find_element_xpath(
            '//label[text()="实绩状态"]/following-sibling::div//input'
        ).get_attribute("value")
        assert before_input == "T" and afert_input == "B"
        assert not production.has_fail_message()

    @allure.story("当报工数量小于实绩报工数量 修改报工数量成功")
    # @pytest.mark.run(order=1)
    def test_production_editnum1(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "100"
        production.click_button(f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]')
        production.click_edi_button()

        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        sleep(1)
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input', num
        )

        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        production.wait_for_loading_to_disappear()
        ele1 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]'
        ).text
        ele2 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[2]'
        ).text

        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:2"]]/td[10]'
        )
        # 断言提示信息为“请先填写表单”
        assert (
                ele1 == num
                and ele2 == f"{name}:2"
                and after_text.text == "开始生产"
        )
        assert not production.has_fail_message()

    @allure.story(
        "当修改的报工数量大于实绩报工数量 弹出弹窗 点击“否”报工状态会变为开始生产"
    )
    # @pytest.mark.run(order=1)
    def test_production_editnum2(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "300"
        production.click_button(f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]')
        production.click_edi_button()

        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        sleep(1)
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input', num
        )

        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

        # 获取提示信息
        sleep(1)
        message = production.get_find_element_xpath(
            '//p[text()="当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"]'
        ).text
        production.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="否"]')
        production.wait_for_loading_to_disappear()

        ele1 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]'
        ).text
        ele2 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[2]'
        ).text

        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:2"]]/td[10]'
        )
        # 断言提示信息为“请先填写表单”
        assert (
            ele1 == num
            and ele2 == f"{name}:2"
            and message
            == "当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"
            and after_text.text == "开始生产"
        )
        assert not production.has_fail_message()

    @allure.story("当修改的报工数量大于实绩报工数量 弹出弹窗 点击“是”报工状态会变为结束")
    # @pytest.mark.run(order=1)
    def test_production_editnum3(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        num = "300"
        production.click_button(f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]')
        production.click_edi_button()

        # 定位“报工数量”输入框，并清空已填写内容
        input_num = production.get_find_element_xpath(
            '//label[text()="报工数量"]/following-sibling::div//input'
        )
        input_num.send_keys(Keys.CONTROL, "a")  # 全选输入框内容
        input_num.send_keys(Keys.BACK_SPACE)  # 删除已填写的内容
        sleep(1)
        production.enter_texts(
            '//label[text()="报工数量"]/following-sibling::div//input', num
        )

        production.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

        # 获取提示信息
        sleep(1)
        message = production.get_find_element_xpath(
            '//p[text()="当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"]'
        ).text
        production.click_button('//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="是"]')
        production.wait_for_loading_to_disappear()

        ele1 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[6]'
        ).text
        ele2 = production.get_find_element_xpath(
            f'//tr[./td[2]//span[text()="{name}:2"]]/td[2]'
        ).text

        production.click_button('(//span[text()="工作指示一览"])[1]')
        production.wait_for_loading_to_disappear()
        after_text = production.get_find_element_xpath(
            f'//tr[.//span[text()="{name}:2"]]/td[10]'
        )
        # 断言提示信息为“请先填写表单”
        assert (
            ele1 == num
            and ele2 == f"{name}:2"
            and message
            == "当前工作报工数量加完成数量大于计划数量，是否将实绩状态改为结束"
            and after_text.text == "结束"
        )
        assert not production.has_fail_message()

    @allure.story("查询工作代码成功")
    # @pytest.mark.run(order=1)
    def test_production_selectcode(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        production.click_button(
            '(//input[@placeholder="请选择" and @class="ivu-select-input"])[1]'
        )
        production.click_button(f'//li[text()="{name}:2"]')
        production.click_button('//span[text()="查询"]')
        sleep(1)
        ele1 = production.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]/tbody/tr[1]/td[2]'
        ).text
        ele2 = driver.find_elements(
            By.XPATH, '(//table[@class="vxe-table--body"])[2]/tbody/tr[2]/td[3]'
        )
        assert ele1 == f"{name}:2" and len(ele2) == 0
        assert not production.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_production_selectresource(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"
        shared_data = SharedDataUtil.load_data()
        resource2 = shared_data.get("master_res2")
        production.click_button(
            '(//input[@placeholder="请选择" and @class="ivu-select-input"])[2]'
        )
        production.click_button(f'//li[text()="{resource2}"]')
        production.click_button('//span[text()="查询"]')
        sleep(1)
        ele1 = production.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]/tbody/tr[1]/td[2]'
        ).text
        ele2 = production.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]/tbody/tr[1]/td[4]'
        ).text
        ele3 = driver.find_elements(
            By.XPATH, '(//table[@class="vxe-table--body"])[2]/tbody/tr[2]/td[3]'
        )
        assert ele1 == f"{name}:2" and ele2 == resource2 and len(ele3) == 0
        assert not production.has_fail_message()

    @allure.story("查询物料代码成功")
    # @pytest.mark.run(order=1)
    def test_production_selectitem(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        production.click_button(
            '(//input[@placeholder="请选择" and @class="ivu-select-input"])[3]'
        )
        production.click_button('//li[text()="1测试B"]')
        production.click_button('//span[text()="查询"]')
        sleep(1)
        ele1 = production.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]/tbody/tr[1]/td[2]'
        ).text
        ele2 = production.get_find_element_xpath(
            '(//table[@class="vxe-table--body"])[2]/tbody/tr[1]/td[3]'
        ).text
        ele3 = driver.find_elements(
            By.XPATH, '(//table[@class="vxe-table--body"])[2]/tbody/tr[2]/td[3]'
        )
        assert ele1 == "1测试C订单:1" and ele2 == "1测试B" and len(ele3) == 0
        assert not production.has_fail_message()

    @allure.story("删除数据")
    # @pytest.mark.run(order=1)
    def test_production_delete3(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        name = "1测试C订单"

        ele = driver.find_elements(By.XPATH, f'//tr[./td[9]//span[text()="{name}"]]')
        while len(ele) > 0:
            production.click_button(f'//tr[./td[9]//span[text()="{name}"]]/td[4]')
            production.click_del_button()

            production.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            sleep(1)
            ele = driver.find_elements(
                By.XPATH, f'//tr[./td[9]//span[text()="{name}"]]'
            )

        assert len(ele) == 0
        assert not production.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_production_delsuccess(self, login_to_production):
        driver = login_to_production  # WebDriver 实例
        production = ProductionPage(driver)  # 用 driver 初始化 ProductionPage
        layout = "测试布局A"
        production.del_layout(layout)
        sleep(2)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not production.has_fail_message()
