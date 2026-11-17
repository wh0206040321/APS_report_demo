import random
import re
from time import sleep
from datetime import datetime

import allure
import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.materialPage.warehouseLocation_page import WarehouseLocationPage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, all_driver_instances


@pytest.fixture(scope="module")
def login_to_item():
    """初始化并返回 driver"""
    driver_path = DateDriver().driver_path
    driver = create_driver(driver_path)
    driver.implicitly_wait(3)

    # 初始化登录页面
    page = LoginPage(driver)  # 初始化登录页面
    page.navigate_to(DateDriver().url)  # 导航到登录页面
    page.login(DateDriver().username, DateDriver().password, DateDriver().planning)
    page.click_button('(//span[text()="物控管理"])[1]')
    page.click_button('(//span[text()="物控基础数据"])[1]')
    page.click_button('(//span[text()="物控工作日历"])[1]')  # 点击物控工作日历
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("物控工作日历测试用例")
@pytest.mark.run(order=108)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        self.item.wait_for_loading_to_disappear()

    @allure.story("添加信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_addfail(self, login_to_item):
        sleep(3)
        layout = "测试布局A"
        self.item.add_layout(layout)
        name = self.item.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        message = self.item.get_error_message()
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        # 检查元素是否包含子节点
        assert message == "校验不通过，请检查标红的表单字段！" and name == layout
        assert not self.item.has_fail_message()

    @allure.story("添加信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_addfail1(self, login_to_item):

        self.item.click_add_button()
        self.item.add_workCalendar('11', '2月')
        message = self.item.get_error_message()
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        # 检查元素是否包含子节点
        assert message == "需选择日"
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_addsuccess(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        day_list = ['1', '3']
        # 输入框要修改的值
        self.item.add_workCalendar('1测试日历A', '2月', day_list)
        self.item.wait_for_loading_to_disappear()
        sleep(1)
        # 点击修改按钮
        self.item.click_button('//tr[./td[2][.//span[text()="1测试日历A"]]]/td[2]')
        sleep(1)
        self.item.click_edi_button()
        # 批量获取输入框的value
        input_values = self.item.acquisition_input("//div[span[text()=' 日历类别 ']]/following-sibling::div//input")
        input_month = self.item.get_workCalendar_month()
        year = datetime.now().year
        values = self.item.get_workCalendar_dayclass(day_list)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert input_values == '1测试日历A' and input_month == f'{year}/02' and all(values)
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_delcancel(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="1测试日历A"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="1测试日历A"]]]/td[2]'
        ).text
        assert itemdata == "1测试日历A", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_addsuccess1(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        code = '1测试日历B'
        day_list = ['1', '3', '5']
        # 输入框要修改的值
        self.item.add_workCalendar(code, '3月', day_list)
        self.item.wait_for_loading_to_disappear()
        sleep(1)
        # 点击修改按钮
        self.item.click_button(f'//tr[./td[2][.//span[text()="{code}"]]]/td[2]')
        sleep(1)
        self.item.click_edi_button()
        # 批量获取输入框的value
        input_values = self.item.acquisition_input("//div[span[text()=' 日历类别 ']]/following-sibling::div//input")
        input_month = self.item.get_workCalendar_month()
        year = datetime.now().year
        values = self.item.get_workCalendar_dayclass(day_list)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert input_values == code and input_month == f'{year}/03' and all(values)
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_addrepeat(self, login_to_item):
        self.item.click_add_button()  # 检查点击添加
        code = '1测试日历B'
        day_list = ['1', '3', '5']
        # 输入框要修改的值
        self.item.add_workCalendar(code, '3月', day_list)
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).get_attribute('innerText')
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("修改测试数据成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_editcodesuccess(self, login_to_item):
        day_list = ['1', '2', '3']
        # 输入框要修改的值
        text_str = "1测试日历A"

        # 选中刚刚新增的测试数据
        self.item.click_button(f'//tr[./td[2][.//span[text()="{text_str}"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        self.item.add_workCalendar(day_list=day_list)
        sleep(1)
        # 选中刚刚编辑的数据
        self.item.click_button(f'//tr[./td[2][.//span[text()="{text_str}"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        values = self.item.get_workCalendar_dayclass(day_list)
        assert values == [False, True, False]
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_delsuccess1(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="1测试日历A"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="1测试日历A"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_add_success(self, login_to_item):
        code = '1测试日历A'
        day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        # 输入框要修改的值
        self.item.click_add_button()  # 点击添加
        self.item.enter_texts('//div[span[text()=" 备注 "]]/following-sibling::div//input', code)
        self.item.add_workCalendar(code, '7月', day_list)
        self.item.wait_for_loading_to_disappear()
        sleep(1)
        # 点击修改按钮
        self.item.click_button(f'//tr[./td[2][.//span[text()="{code}"]]]/td[2]')
        sleep(1)
        self.item.click_edi_button()
        # 批量获取输入框的value
        input_values = self.item.acquisition_input("//div[span[text()=' 日历类别 ']]/following-sibling::div//input")
        bz_values = self.item.acquisition_input("//div[span[text()=' 备注 ']]/following-sibling::div//input")
        input_month = self.item.get_workCalendar_month()
        year = datetime.now().year
        values = self.item.get_workCalendar_dayclass(day_list)
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert input_values == code and input_month == f'{year}/07' and all(values) and bz_values == code
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_selectcodesuccess(self, login_to_item):
        driver = login_to_item  # WebDriver 实例
        item = WarehouseLocationPage(driver)  # 用 driver 初始化 ItemPage

        # 点击查询
        item.click_sel_button()
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
        # 点击工厂代码
        item.click_button('//div[text()="日历类别" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "1测试日历A",
        )
        sleep(1)

        # 点击确认
        item.click_select_button()
        sleep(1)
        # 定位第一行是否为产品A
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        # 点击刷新
        self.item.click_ref_button()
        assert itemcode == "1测试日历A" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_selectnodatasuccess(self, login_to_item):

        # 点击查询
        self.item.click_sel_button()
        sleep(1)
        # 定位名称输入框
        element_to_double_click = self.driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(self.driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        sleep(1)
        # 点击交付单号
        self.item.click_button('//div[text()="日历类别" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        self.item.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        self.item.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        self.item.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "没有数据",
        )
        sleep(1)

        # 点击确认
        self.item.click_select_button()
        sleep(2)
        itemcode = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        sleep(1)

        # 点击刷新
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_select2(self, login_to_item):
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = self.item.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            self.item.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            self.item.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//input')
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        self.item.right_refresh('物控工作日历')
        assert len(eles) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_select3(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('日历类别', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        self.item.right_refresh('物控工作日历')
        assert all(first_char.lower() in text.lower() for text in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_select4(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合开头")
        sleep(1)
        self.item.select_input('日历类别', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        self.item.right_refresh('物控工作日历')
        assert all(str(item).lower().startswith(first_char.lower()) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_select5(self, login_to_item):
        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合结尾")
        sleep(1)
        self.item.select_input('日历类别', last_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.get_attribute('innerText') for ele in eles]
        self.item.right_refresh('物控工作日历')
        assert all(str(item).lower().endswith(last_char.lower()) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_clear(self, login_to_item):
        name = "3"
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('日历类别', name)
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("清除所有筛选条件")
        sleep(1)
        ele = self.item.get_find_element_xpath(
            '//div[div[span[text()=" 日历类别"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        self.item.right_refresh('物控工作日历')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not self.item.has_fail_message()

    # @allure.story("模拟ctrl+i添加重复")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_ctrlIrepeat(self, login_to_item):
    #     self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
    #     ele1 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
    #         "innerText")
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     message = self.item.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
    #     self.item.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
    #     assert message == '记录已存在,请检查！'
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟ctrl+i添加")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_ctrlI(self, login_to_item):
    #     self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
    #     self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
    #     self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
    #     sleep(1)
    #     ele1 = self.item.get_find_element_xpath(
    #         '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
    #         "value")
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     self.item.get_find_message()
    #     self.item.select_input('日历类别', '1没有数据添加')
    #     ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
    #         "innerText")
    #     assert ele1 == ele2 == '1没有数据添加'
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟ctrl+m修改")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_ctrlM(self, login_to_item):
    #     self.item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
    #     self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
    #     self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
    #     ele1 = self.item.get_find_element_xpath(
    #         '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
    #         "value")
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     self.item.get_find_message()
    #     self.item.select_input('日历类别', '1没有数据修改')
    #     ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
    #         "innerText")
    #     assert ele1 == ele2
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟多选删除")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_shiftdel(self, login_to_item):
    #     self.item.right_refresh('物控工作日历')
    #     elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
    #                 '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]']
    #     self.item.click_button(elements[0])
    #     # 第二个单元格 Shift+点击（选择范围）
    #     cell2 = self.item.get_find_element_xpath(elements[1])
    #     ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
    #     sleep(1)
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
    #     sleep(1)
    #     self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
    #     self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改1')
    #     self.item.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
    #     self.item.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
    #     self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据修改12')
    #     sleep(1)
    #     ele1 = self.item.get_find_element_xpath(
    #         '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
    #     ele2 = self.item.get_find_element_xpath(
    #         '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     self.item.get_find_message()
    #     self.item.select_input('日历类别', '1没有数据修改1')
    #     ele11 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
    #         "innerText")
    #     ele22 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
    #         "innerText")
    #     assert ele1 == ele11 and ele2 == ele22
    #     assert not self.item.has_fail_message()
    #     self.item.select_input('日历类别', '1没有数据修改')
    #     before_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
    #     before_count = int(re.search(r'\d+', before_data).group())
    #     elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[1]',
    #                 '(//table[@class="vxe-table--body"]//tr[2]//td[1])[1]',
    #                 '(//table[@class="vxe-table--body"]//tr[3]//td[1])[1]']
    #     self.item.click_button(elements[0])
    #     # 第二个单元格 Shift+点击（选择范围）
    #     cell2 = self.item.get_find_element_xpath(elements[2])
    #     ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
    #     sleep(1)
    #     self.item.click_del_button()
    #     self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
    #     message = self.item.get_find_message()
    #     self.item.wait_for_loading_to_disappear()
    #     after_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
    #     after_count = int(re.search(r'\d+', after_data).group())
    #     assert message == "删除成功！"
    #     assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟ctrl+c复制可查询")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_ctrlC(self, login_to_item):
    #     self.item.right_refresh('物控工作日历')
    #     self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
    #     before_data = self.item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
    #     sleep(1)
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
    #     self.item.click_button('//div[div[span[text()=" 日历类别"]]]//input')
    #     sleep(1)
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    #     eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
    #     eles = [ele.get_attribute('innerText') for ele in eles]
    #     self.item.right_refresh('物控工作日历')
    #     assert all(before_data in ele for ele in eles)
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_shift(self, login_to_item):
    #     elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
    #                 '//table[@class="vxe-table--body"]//tr[2]//td[1]']
    #     self.item.click_button(elements[0])
    #     # 第二个单元格 Shift+点击（选择范围）
    #     cell2 = self.item.get_find_element_xpath(elements[1])
    #     ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
    #     sleep(1)
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
    #     num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
    #     assert len(num) == 2
    #     assert not self.item.has_fail_message()
    #
    # @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # # @pytest.mark.run(order=1)
    # def test_WorkCalendar_ctrls(self, login_to_item):
    #     elements = ['//table[@class="vxe-table--body"]//tr[1]//td[1]',
    #                 '//table[@class="vxe-table--body"]//tr[2]//td[1]']
    #     self.item.click_button(elements[0])
    #     # 第二个单元格 Shift+点击（选择范围）
    #     cell2 = self.item.get_find_element_xpath(elements[1])
    #     ActionChains(self.driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
    #     sleep(1)
    #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
    #     num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
    #     self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
    #     message = self.item.get_find_message()
    #     assert len(num) == 2 and message == "保存成功"
    #     assert not self.item.has_fail_message()
    #
    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_WorkCalendar_delsuccess3(self, login_to_item):
        value = ['1测试日历A', '1测试日历B']
        self.item.del_all(value, xpath='//div[div[span[text()=" 日历类别"]]]//input')

        self.item.right_refresh('物控工作日历')
        itemdata = [
            self.driver.find_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
            for v in value[:2]
        ]
        assert all(len(elements) == 0 for elements in itemdata)
        layout_name = "测试布局A"
        sleep(2)
        self.item.del_layout(layout_name)
        sleep(1)
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = self.driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout_name} "]'
        )
        assert 0 == len(after_layout)
        assert not self.item.has_fail_message()
