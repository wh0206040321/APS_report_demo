import random
from time import sleep

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    page.click_button('(//span[text()="物控管理"])[1]')  # 点击计划管理
    page.click_button('(//span[text()="物控基础数据"])[1]')  # 点击计划基础数据
    page.click_button('(//span[text()="物料BOM"])[1]')  # 点击物料BOM
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("物料BOM测试用例")
@pytest.mark.run(order=102)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        # 必填新增输入框xpath
        self.req_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='ywz9q11i-sp3b']//input",
            "//div[@id='u2tgl5h9-otp1']//input",
            "//div[@id='xejahgz1-ks53']//input"
        ]
        # 必填编辑输入框xpath
        self.req_input_edit_xpath_list = [
            "//div[@id='eou5yf0n-u1tt']//input",
            "//div[@id='0brq2kv4-lece']//input",
            "//div[@id='am6vi9m0-9836']//input",
            "//div[@id='aesli5p3-jicr']//input",
            "//div[@id='z15t88ud-aroz']//input"
        ]

        # 全部新增输入框xpath
        self.all_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='x1k7t87i-tvc3']//input",
            "//div[@id='hpjqsv1m-5607']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='7z1rv7fs-trb6']//input",
            "//div[@id='hguo4esk-gii0']//input",
            "//div[@id='13j55ae1-8hj2']//input",
            "//div[@id='ywz9q11i-sp3b']//input",
            "//div[@id='u2tgl5h9-otp1']//input",
            "//div[@id='izykzohi-1l5u']//input",
            "//div[@id='ctfddy1k-hbmj']//input",
            "//div[@id='8sgoh6vh-0pz5']//input",
            "//div[@id='poxayyhi-9bss']//input",
            "//div[@id='zxc6ccwu-bnwe']//input",
            "//div[@id='15qig6pt-sj1x']//input",
            "//div[@id='vtxj45fl-aisi']//input",
            "//div[@id='owcpuvmy-it09']//input",
            "//div[@id='wcmoz0yh-ws7q']//input",
            "//div[@id='xieapx7h-udjh']//input",
            "//div[@id='nae4z5ad-cvle']//input",
            "//div[@id='06giwjn5-paij']//input",
            "//div[@id='vfn272xc-c16a']//input",
            "//div[@id='69p938gi-8t8g']//input",
            "//div[@id='z5cusmj6-zosk']//input",
            "//div[@id='37xq7un7-s4m5']//input",
            "//div[@id='va14hagj-w77v']//input",
            "//div[@id='r1rwj8xt-jaqj']//input",
            "//div[@id='4b9ntys5-lotn']//input",
            "//div[@id='zkbc6fjc-i50c']//input",
            "//div[@id='zt325ki7-6pso']//input",
            "//div[@id='xejahgz1-ks53']//input"
        ]
        # 全部新增日期xpath
        self.all_date_add_xpath_list = [
            "//div[@id='4fwb5kkc-4a37']//input",
            "//div[@id='egwab1fe-1ncy']//input",
            "//div[@id='whyngz23-29ot']//input",
            "//div[@id='p54v6ryt-lmx0']//input",
            "//div[@id='lunaeuye-y9i4']//input",
            "//div[@id='mpoms0y9-b1wu']//input",
            "//div[@id='14wpbyck-zz27']//input",
            "//div[@id='k3gbvyfm-bcmh']//input",
            "//div[@id='v4ofksk1-x5kb']//input",
            "//div[@id='657ublj9-rhil']//input",
            "//div[@id='zgogqqgr-5vgp']//input",
            "//div[@id='jk3ho4au-9cka']//input"
        ]
        # 全部编辑输入框xpath
        self.all_input_edit_xpath_list = [
            "//div[@id='eou5yf0n-u1tt']//input",
            "//div[@id='btaiy3pl-8e2q']//input",
            "//div[@id='th18ywl0-60sg']//input",
            "//div[@id='am6vi9m0-9836']//input",
            "//div[@id='q2y73oqm-0zt7']//input",
            "//div[@id='em0ttecf-umrn']//input",
            "//div[@id='430ao3yw-w2wo']//input",
            "//div[@id='0brq2kv4-lece']//input",
            "//div[@id='aesli5p3-jicr']//input",
            "//div[@id='sumtcyzx-5qsj']//input",
            "//div[@id='al83xmme-xima']//input",
            "//div[@id='o90g79eg-nvlj']//input",
            "//div[@id='mtxzhgfv-vljj']//input",
            "//div[@id='mo9dlclx-9s5c']//input",
            "//div[@id='ga98y6bw-5kc3']//input",
            "//div[@id='1oy0kbna-25fi']//input",
            "//div[@id='gzunvpxr-lxpm']//input",
            "//div[@id='2uvhk55g-siwh']//input",
            "//div[@id='r7tsvl9z-nhfc']//input",
            "//div[@id='6015h7p1-og8k']//input",
            "//div[@id='sxpusm6l-rmqt']//input",
            "//div[@id='qb76w14d-nvbs']//input",
            "//div[@id='p5g4s0g9-gn3f']//input",
            "//div[@id='hu9uqpx0-97mn']//input",
            "//div[@id='bn2aihab-9zkp']//input",
            "//div[@id='eh4h947k-8sdx']//input",
            "//div[@id='or7nsc09-soc8']//input",
            "//div[@id='ghgklss1-mo15']//input",
            "//div[@id='vd5sz592-6l5i']//input",
            "//div[@id='bpc2txxr-577c']//input",
            "//div[@id='z15t88ud-aroz']//input"
        ]
        # 全部编辑日期xpath
        self.all_date_edit_xpath_list = [
            "//div[@id='xwstbjw4-8ff5']//input",
            "//div[@id='ythcjnyt-gg3q']//input",
            "//div[@id='pxz7axqa-rah7']//input",
            "//div[@id='lco2pa6n-eg01']//input",
            "//div[@id='0j4m9gvk-jfv3']//input",
            "//div[@id='eg54vifr-mret']//input",
            "//div[@id='c3jx5j97-qm5n']//input",
            "//div[@id='mu08qey5-1fbt']//input",
            "//div[@id='vyeqz3s2-3a49']//input",
            "//div[@id='tym3fmvm-rzox']//input",
            "//div[@id='4vqkkuy7-vuda']//input",
            "//div[@id='6ctu16ue-n5nl']//input"
        ]

    @allure.story("添加物料BOM信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_materialBOM_addfail(self, login_to_item):
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none([
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='ywz9q11i-sp3b']//input",
            "//div[@id='u2tgl5h9-otp1']//div[1]"
        ], color_value)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加物料BOM信息，有多个必填只填写一项，不允许提交")
    # @pytest.mark.run(order=2)
    def test_materialBOM_addcodefail(self, login_to_item):
        # 点击新增按钮
        self.item.click_add_button()
        # 输入第一个必填项
        self.item.enter_texts("//div[@id='p34nag46-7evf']//input", "text1231")
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        xpath_list = [
            "//div[@id='ywz9q11i-sp3b']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='u2tgl5h9-otp1']//div[1]"
        ]
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none(xpath_list, color_value)
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='xejahgz1-ks53']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中新增行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_materialBOM_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"

        sleep(1)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            error_popup == "记录已存在,请检查！"
        ), f"预期数据是记录已存在,请检查，实际得到{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_materialBOM_delcancel(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.item.get_find_element_xpath(
            '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        ).text
        assert itemdata == "111", f"预期{itemdata}"
        assert not self.item.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_materialBOM_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "222"
        date_str = "2025/07/23 00:00:00"

        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='xejahgz1-ks53']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)
        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_add_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中新增行
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)

        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("修改测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_editcodesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "333"
        date_str = "2025/07/23 00:00:00"
        # 输入框的xpath


        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='z15t88ud-aroz']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)

        ele = self.item.get_find_element_xpath(
            "//div[@id='aesli5p3-jicr']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)

        # 批量修改输入框
        self.item.batch_modify_input(self.req_input_edit_xpath_list, text_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.req_input_edit_xpath_list, text_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_edit_xpath_list) == len(input_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("修改数据重复")
    # @pytest.mark.run(order=1)
    def test_materialBOM_editrepeat(self, login_to_item):

        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()

        # 物料代码等输入111
        text_str = "111"
        self.item.batch_modify_input(self.req_input_edit_xpath_list, text_str)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 获取重复弹窗文字
        error_popup = self.item.get_find_element_xpath(
            '//div[text()=" 记录已存在,请检查！ "]'
        ).text
        self.item.click_button('//button[@type="button"]/span[text()="关闭"]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert error_popup == "记录已存在,请检查！", f"预期数据{error_popup}"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_delsuccess1(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    @allure.story("编辑全部选项成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"

        # 选中编辑数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)
        ele = self.item.get_find_element_xpath(
            "//div[@id='z15t88ud-aroz']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)

        ele = self.item.get_find_element_xpath(
            "//div[@id='aesli5p3-jicr']//input"
        )
        # 清空数字输入框
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.BACK_SPACE)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_edit_xpath_list, text_str)
        self.item.batch_modify_input(self.all_date_edit_xpath_list, date_str)

        sleep(1)
        self.item.click_button("//div[@id='292o318z-93lz']")
        sleep(1)
        self.item.click_button(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[2]')
        sleep(1)
        self.item.enter_texts(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[2]//input',
            "1")
        sleep(1)
        self.item.click_button(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[3]')
        sleep(1)
        self.item.enter_texts(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[3]//input',
            "2")
        sleep(1)
        self.item.click_button(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[4]')
        sleep(1)
        self.item.enter_texts(
            '//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[4]//input',
            "3")
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[6]')
        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中刚刚编辑的数据行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.all_input_edit_xpath_list, text_str)
        input_values2 = self.item.batch_acquisition_input(self.all_date_edit_xpath_list, date_str)
        self.item.click_button("//div[@id='292o318z-93lz']")
        sleep(1)
        str1 = self.item.get_find_element_xpath('//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[2]//span').text
        str2 = self.item.get_find_element_xpath('//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[3]//span').text
        str3 = self.item.get_find_element_xpath('//span[text()=" 阶梯损耗起始"]/ancestor::div[@class="vxe-table--header-wrapper body--wrapper"]/following-sibling::div//td[4]//span').text
        print('str1', str1)
        print('str2', str2)
        print('str3', str3)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[6]')
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            (str1 == '1' and str2 == '2' and str3 == '3') and
            len(self.all_input_edit_xpath_list) == len(input_values) and
            len(self.all_date_edit_xpath_list) == len(input_values2)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_delsuccess2(self, login_to_item):

        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    # @allure.story("过滤刷新成功")
    # # @pytest.mark.run(order=1)
    # def test_materialBOM_refreshsuccess(self, login_to_item):
    #
    #     filter_results = self.item.filter_method('//span[text()=" 产品编码"]/ancestor::div[3]//span//span//span')
    #     print('filter_results', filter_results)
    #     assert filter_results
    #     assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_materialBOM_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        self.item.click_add_button()  # 点击添加
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_add_xpath_list, text_str)
        # 批量修改日期
        self.item.batch_modify_input(self.all_date_add_xpath_list, date_str)

        sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 选中物料代码
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        # 点击编辑按钮
        self.item.click_edi_button()
        sleep(1)
        # 批量获取输入框的value
        input_values = self.item.batch_acquisition_input(self.all_input_edit_xpath_list, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(self.all_date_edit_xpath_list, date_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.all_input_add_xpath_list) == len(input_values)
                and len(self.all_date_add_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="产品编码" and contains(@optid,"opt_")]')
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
            "111",
        )
        sleep(1)
        # 点击确认
        item.click_select_button()
        # 定位第一行是否为产品A
        itemcode = item.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]'
        ).text
        # 定位第二行没有数据
        itemcode2 = driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[2]/td[2]',
        )
        assert itemcode == "111" and len(itemcode2) == 0
        assert not item.has_fail_message()

    @allure.story("没有数据时显示正常")
    # @pytest.mark.run(order=1)
    def test_materialBOM_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="产品编码" and contains(@optid,"opt_")]')
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
        itemcode = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[1]/td[2]',
        )
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_materialBOM_delsuccess3(self, login_to_item):
        # 定位内容为‘111’的行
        self.item.click_button('//tr[./td[2][.//span[text()="111"]]]/td[2]')
        self.item.click_del_button()  # 点击删除
        sleep(1)
        # 点击确定
        # 找到共同的父元素
        parent = self.item.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()
        self.item.click_ref_button()
        sleep(1)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()
