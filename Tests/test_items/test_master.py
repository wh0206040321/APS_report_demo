import logging
import random
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.master_page import MasterPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_master():
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
        page.click_button('(//span[text()="计划基础数据"])[1]')  # 点击计划基础数据
        page.click_button('(//span[text()="工艺产能"])[1]')  # 点击工艺产能
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("工艺产能表测试用例")
@pytest.mark.run(order=16)
class TestMasterPage:

    @allure.story("添加布局")
    # @pytest.mark.run(order=1)
    def test_master_addlayout(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        layout = "测试布局A"
        master.add_layout(layout)
        # 获取布局名称的文本元素
        name = master.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        assert layout == name
        assert not master.has_fail_message()

    @allure.story("添加工艺产能信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_master_addfail(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()

        master.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        message = master.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请根据必填项填写信息"
        assert not master.has_fail_message()

    @allure.story("添加工艺产能信息，只填写物料，不允许提交")
    # @pytest.mark.run(order=2)
    def test_master_addcodefail(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        sleep(1)
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)

        # 点击确定
        master.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = master.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请根据必填项填写信息"
        assert not master.has_fail_message()

    @allure.story("添加工艺产能信息，只填写物料和工序选定器和工序编号，不允许提交")
    # @pytest.mark.run(order=3)
    def test_master_addserialfail(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        sleep(1)
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[1]'
        )

        # 点击确定
        master.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = master.get_error_message()
        # 检查元素是否包含子节点
        assert message == "请根据必填项填写信息"
        assert not master.has_fail_message()

    @allure.story(
        "添加工艺产能信息，只填写物料，工序选定器和工序编号，输入指令，新增成功,校验文本框"
    )
    # @pytest.mark.run(order=3)
    def test_master_addserial2(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        name = "11111111111111113evf饿。+/.3.331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        # 清空之前的共享数据
        SharedDataUtil.clear_data()
        master.click_add_button()

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        item = master.get_find_element_xpath(
            '//span[text()=" 物料代码： "]/parent::div//input'
        ).get_attribute("value")

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            name,
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.add_serial3()
        # 获取物料名称
        master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
        random_int = random.randint(1, 4)
        master.wait_for_loading_to_disappear()
        master.click_button(
            f'(//table[.//span[@class="vxe-cell--label"]])[2]//tr[{random_int}]/td[2]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        # 获取物料数量
        random_int = random.randint(1, 100)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
            f"{random_int}",
        )
        # 点击使用指令
        master.click_button(
            '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
        )
        # 点击第一个输入指令点击删除
        master.click_button(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[2]//input'
        )
        master.del_serial4()
        master.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        # 点击确定
        master.add_ok_button()
        adddata = master.get_find_element_xpath(
            f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        ).text
        addtext = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]]/td[9]'
        ).text
        text_ = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]]/td[5]'
        ).text
        # 获取重复弹窗文字
        error_popup = driver.find_elements(
            By.XPATH, '//div[text()=" 记录已存在,请检查！ "]'
        )
        SharedDataUtil.save_data(
            {"item": item}
        )
        assert text_ == '999999999'
        assert item == adddata and addtext == "输入指令" and len(error_popup) == 0
        assert not master.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccess1(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data().get("item")
        master.delete_material(item)

        # 断言元素已经不存在
        final_eles = driver.find_elements(
            By.XPATH, f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        )
        assert len(final_eles) == 0, "元素仍然存在，删除失败！"
        assert not master.has_fail_message()

    @allure.story(
        "添加工艺产能信息，只填写物料，工序选定器和工序编号，使用指令，新增成功"
    )
    # @pytest.mark.run(order=3)
    def test_master_addserial3(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        SharedDataUtil.clear_data()
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        item = master.get_find_element_xpath(
            '//span[text()=" 物料代码： "]/parent::div//input'
        ).get_attribute("value")

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击使用指令 放大按钮
        master.click_button(
            '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
        )
        # 放大页面
        master.click_button('(//div[text()="新增工艺产能"])[2]/parent::div//i[1]')

        # 输入指令 点击对话框按钮 获取资源名称
        master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[1]/td[5]//i',
        )
        random_int = random.randint(1, 8)
        master.wait_for_loading_to_disappear()
        master.click_button(
            f'//tr[{random_int}]/td//span[@class="vxe-cell--checkbox"]'
        )
        # 点击对话框按钮
        master.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]/button[1]',
        )
        # 获取资源能力
        random_int = random.randint(1, 4)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[1]/td[7]//input',
            f"{random_int}pm",
        )
        sleep(1)

        # 点击确定
        master.add_ok_button()

        adddata = master.get_find_element_xpath(
            f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        ).text
        addtext = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]]/td[9]'
        ).text
        # 获取重复弹窗文字
        error_popup = driver.find_elements(
            By.XPATH, '//div[text()=" 记录已存在,请检查！ "]'
        )
        SharedDataUtil.save_data(
            {"item": item}
        )
        assert item == adddata and addtext == "使用指令" and len(error_popup) == 0
        assert not master.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_master_addrepeat(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.add_serial3()
        # 获取物料名称
        master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
        random_int = random.randint(1, 4)
        master.wait_for_loading_to_disappear()
        master.click_button(
            f'(//table[.//span[@class="vxe-cell--label"]])[2]//tr[{random_int}]/td[2]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        # 获取物料数量
        random_int = random.randint(1, 100)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
            f"{random_int}",
        )

        # 点击使用指令 放大按钮
        master.click_button(
            '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
        )
        # 放大页面
        master.click_button('(//div[text()="新增工艺产能"])[2]/parent::div//i[1]')

        # 点击对话框按钮 获取资源名称
        master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i')
        random_int = random.randint(1, 8)
        master.click_button(
            f'//tr[{random_int}]/td//span[@class="vxe-cell--checkbox"]'
        )
        # 点击对话框按钮
        master.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]/button[1]')
        # 获取资源能力
        random_int = random.randint(1, 4)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[7]//input',
            f"{random_int}pm",
        )

        # 点击确定
        master.add_ok_button()
        sleep(1)
        # 获取重复弹窗文字
        error_popup = master.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute("innerText")
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not master.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccess2(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.delete_material(item)

        # 断言元素已经不存在
        final_eles = driver.find_elements(
            By.XPATH, f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        )
        assert len(final_eles) == 0, "元素仍然存在，删除失败！"
        assert not master.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_master_addsuccess(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        SharedDataUtil.clear_data()
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        item = master.get_find_element_xpath(
            '//span[text()=" 物料代码： "]/parent::div//input'
        ).get_attribute("value")

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.add_serial3()
        master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
        random_int = random.randint(1, 4)
        sleep(1)
        master.click_button(
            f'(//table[.//span[@class="vxe-cell--label"]])[2]//tr[{random_int}]/td[2]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        # 获取物料数量
        random_int = random.randint(1, 100)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
            f"{random_int}",
        )

        # 点击使用指令 放大按钮
        master.click_button(
            '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
        )
        # 放大页面
        master.click_button('(//div[text()="新增工艺产能"])[2]/parent::div//i[1]')

        # 点击对话框按钮 获取资源名称
        master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i')
        random_int = random.randint(1, 8)
        master.wait_for_loading_to_disappear()
        master.click_button(
            f'//tr[{random_int}]/td//span[@class="vxe-cell--checkbox"]'
        )
        # 点击对话框按钮
        master.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]/button[1]')
        # 获取资源能力
        random_int = random.randint(1, 4)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[7]//input',
            f"{random_int}pm",
        )

        # 点击确定
        master.add_ok_button()

        adddata = master.get_find_element_xpath(
            f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        ).text
        # 获取重复弹窗文字
        error_popup = driver.find_elements(
            By.XPATH, '//div[text()=" 记录已存在,请检查！ "]'
        )
        SharedDataUtil.save_data({"item": item})
        assert item == adddata and len(error_popup) == 0
        assert not master.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccess3(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.delete_material(item)

        # 断言元素已经不存在
        final_eles = driver.find_elements(
            By.XPATH, f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        )
        assert len(final_eles) == 0, "元素仍然存在，删除失败！"
        assert not master.has_fail_message()

    @allure.story("删除工序选定器成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccessserial1(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

        # 点击工序选定器
        master.add_serial1()
        input_text = master.get_find_element_xpath(
            '//table[.//div[@class="vxe-input type--text size--mini is--controls"]]//tr[2]/td[2]//input'
        )
        input_text.send_keys(Keys.CONTROL, "a")
        input_text.send_keys(Keys.BACK_SPACE)
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--text size--mini is--controls"]]//tr[2]/td[2]//input',
            "2",
        )
        # 选中工序选定器1 点击删除
        master.click_button(
            '//table[.//div[@class="vxe-input type--text size--mini is--controls"]]//tr[1]/td[2]//input'
        )
        master.del_serial1()
        master.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        input_after = master.get_find_element_xpath(
            '//table[.//div[@class="vxe-input type--text size--mini is--controls"]]//tr[1]/td[2]//input'
        ).get_attribute("value")
        assert input_after == "2", f"实际得到{input_after}"
        assert not master.has_fail_message()

    @allure.story("删除工序编号成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccessserial2(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        master.add_serial2()
        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[2]/td[2]//input',
            "2",
        )

        # 点击第一个工序编号点击删除
        master.click_button(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input'
        )
        master.del_serial2()
        master.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        master.wait_for_loading_to_disappear()
        input_after = master.get_find_element_xpath(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input'
        ).get_attribute("value")
        assert input_after == "2", f"实际得到{input_after}"
        assert not master.has_fail_message()

    @allure.story("删除输入指令成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccessserial3(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.add_serial3()
        master.add_serial3()
        # 获取指令代码
        input_text = master.get_find_element_xpath(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[2]/td[4]//input'
        )
        input_text.send_keys(Keys.CONTROL, "a")
        input_text.send_keys(Keys.BACK_SPACE)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[2]/td[4]//input',
            "In2",
        )

        # 点击第一个输入指令点击删除
        master.click_button(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[4]//input'
        )
        master.del_serial3()
        master.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        input_after = master.get_find_element_xpath(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[4]//input'
        ).get_attribute("value")
        assert input_after == "In2", f"实际得到{input_after}"
        assert not master.has_fail_message()

    @allure.story("删除使用指令成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccessserial4(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        item = master.get_find_element_xpath(
            '//span[text()=" 物料代码： "]/parent::div//input'
        ).get_attribute("value")

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.click_button('(//div[@class="ivu-tabs-nav"])[2]/div[3]')
        master.add_serial4()
        # 获取物料名称
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[1]/td[2]//input',
            "1",
        )
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[2]/td[2]//input',
            "2",
        )

        # 点击第一个输入指令点击删除
        master.click_button(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[1]/td[2]//input'
        )
        master.del_serial4()
        master.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        input_after = master.get_find_element_xpath(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[2]//tr[1]/td[2]//input'
        ).get_attribute("value")
        assert input_after == "2", f"实际得到{input_after}"
        assert not master.has_fail_message()

    @allure.story("添加测试数据成功")
    # @pytest.mark.run(order=1)
    def test_master_addsuccess1(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        SharedDataUtil.clear_data()
        master.click_add_button()  # 检查点击添加

        # 填写订物料代码
        master.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        master.wait_for_loading_to_disappear()
        master.click_button(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[last()]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1)
        item = master.get_find_element_xpath(
            '//span[text()=" 物料代码： "]/parent::div//input'
        ).get_attribute("value")

        # 填写工序编号
        master.enter_texts(
            '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[1]/td[2]//input',
            "1",
        )
        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )

        # 点击新增输入指令
        master.add_serial3()
        # 获取物料名称
        master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
        random_int = random.randint(1, 4)
        sleep(1)
        master.click_button(
            f'(//table[.//span[@class="vxe-cell--label"]])[2]//tr[{random_int}]/td[2]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        # 获取物料数量
        random_int = random.randint(1, 100)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
            f"{random_int}",
        )

        # 点击使用指令 放大按钮
        master.click_button(
            '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
        )
        # 放大页面
        master.click_button('(//div[text()="新增工艺产能"])[2]/parent::div//i[1]')

        # 点击对话框按钮 获取资源名称
        master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i')
        random_int = random.randint(1, 8)
        master.click_button(
            f'//tr[{random_int}]/td//span[@class="vxe-cell--checkbox"]'
        )
        # 点击对话框按钮
        master.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]/button[1]')
        # 获取资源能力
        random_int = random.randint(1, 4)
        master.enter_texts(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[7]//input',
            f"{random_int}pm",
        )

        # 点击确定
        master.add_ok_button()

        adddata = master.get_find_element_xpath(
            f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        ).text
        # 获取重复弹窗文字
        error_popup = driver.find_elements(
            By.XPATH, '//div[text()=" 记录已存在,请检查！ "]'
        )
        SharedDataUtil.save_data({"item": item})
        assert item == adddata and len(error_popup) == 0
        assert not master.has_fail_message()

    @allure.story("修改工艺产能工序代码")
    # @pytest.mark.run(order=1)
    def test_master_editprocess(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.wait_for_loading_to_disappear()
        # 选中物料代码点击编辑
        master.click_button(f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]')
        master.click_edi_button()

        # 点击下拉框
        master.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        )
        random_int = random.randint(1, 4)
        # 输入工序代码
        master.click_button(
            f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_int}]'
        )
        sleep(1)
        # 获取工序代码
        process_input = master.get_find_element_xpath(
            '//table[@class="vxe-table--body"]//tr[1]/td[3]//input[@placeholder="请选择"]'
        ).get_attribute("value")
        master.add_ok_button()
        edittext = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]]/td[6]'
        ).text
        assert edittext in process_input
        assert not master.has_fail_message()

    @allure.story("修改工艺产能输入物料")
    # @pytest.mark.run(order=1)
    def test_master_edititem(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.wait_for_loading_to_disappear()
        # 选中物料代码点击编辑
        master.click_button(f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]')
        master.click_edi_button()

        # 获取物料名称
        master.click_button(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i'
        )
        random_int = random.randint(1, 4)
        sleep(1)
        master.click_button(
            f'(//table[.//span[@class="vxe-cell--label"]])[2]//tr[{random_int}]/td[2]'
        )
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        sleep(1.5)
        # 获取物料代码
        item_input = master.get_find_element_xpath(
            '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//input'
        ).get_attribute("value")
        master.add_ok_button()
        edittext = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]]/td[11]'
        ).text
        assert item_input == edittext
        assert not master.has_fail_message()

    @allure.story("修改工艺产能使用指令资源")
    # @pytest.mark.run(order=1)
    def test_master_editresource(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.wait_for_loading_to_disappear()
        # 选中物料代码点击编辑
        master.click_button(f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]')
        master.click_edi_button()

        # 点击使用指令 放大按钮
        master.click_button('(//div[@class="ivu-tabs-nav"])[2]/div[3]')
        # 放大页面
        master.click_button('(//div[text()="编辑工艺产能"])[1]/parent::div//i[1]')

        # 使用指令 点击对话框按钮 获取资源名称
        master.click(
            By.XPATH,
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i',
        )
        random_int = random.randint(1, 8)
        master.click_button(
            '(//span[@class="vxe-checkbox--icon iconfont icon-fuxuankuangdaiding"])[2]'
        )
        master.click_button(
            '(//span[@class="vxe-checkbox--icon vxe-icon-checkbox-checked-fill"])[2]'
        )

        master.click_button(
            f'//tr[{random_int}]/td//span[@class="vxe-cell--checkbox"]'
        )
        # 点击对话框按钮
        master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')
        # 获取资源代码
        sleep(1)
        resource_input = master.get_find_element_xpath(
            '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//input'
        ).get_attribute("value")
        master.add_ok_button()
        edittext = master.get_find_element_xpath(
            f'//tr[.//td[2]//span[text()="{item}"]][2]/td[11]'
        ).text
        assert resource_input == edittext
        assert not master.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_master_refreshsuccess(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        master.wait_for_loading_to_disappear()
        # 筛选框输入123
        master.enter_texts(
            '//p[text()="物料代码"]/ancestor::div[2]//input', "123"
        )
        master.click_ref_button()
        ordertext = master.get_find_element_xpath(
            '//p[text()="物料代码"]/ancestor::div[2]//input'
        ).text
        assert ordertext == "", f"预期{ordertext}"
        assert not master.has_fail_message()

    @allure.story("查询物料代码成功")
    # @pytest.mark.run(order=1)
    def test_master_selectcodesuccess(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        # 点击查询
        master.click_sel_button()
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
        # 点击工艺产能代码
        master.click_button('//div[text()="物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        master.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        master.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        master.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            item,
        )
        sleep(1)

        # 点击确认
        master.click_select_button()
        # 定位第一行是
        ordercode = master.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 第3行数据
        notext = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[3]/td[2]',
        )
        assert ordercode == item and len(notext) == 0
        assert not master.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccess4(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        item = SharedDataUtil.load_data()["item"]
        master.wait_for_loading_to_disappear()
        master.delete_material(item)
        # 断言元素已经不存在
        final_eles = driver.find_elements(
            By.XPATH, f'//tr[.//span[text()="{item}"]]/td[2]//span[text()="{item}"]'
        )
        assert len(final_eles) == 0, "元素仍然存在，删除失败！"
        assert not master.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_master_delsuccess(self, login_to_master):
        driver = login_to_master  # WebDriver 实例
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        layout = "测试布局A"
        master.del_layout(layout)
        master.wait_for_loading_to_disappear()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert 0 == len(after_layout)
        assert not master.has_fail_message()