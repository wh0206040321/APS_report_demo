import random
import re
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
    page.click_button('(//span[text()="物料CTB"])[1]')  # 点击物料交付答复
    yield driver  # 提供给测试用例使用
    safe_quit(driver)


@allure.feature("物料CTB测试用例")
@pytest.mark.run(order=101)
class TestItemPage:
    @pytest.fixture(autouse=True)
    def setup(self, login_to_item):
        self.driver = login_to_item
        self.item = WarehouseLocationPage(self.driver)
        # 必填新增输入框xpath
        self.req_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input"
        ]
        # 必填编辑输入框xpath
        self.req_input_edit_xpath_list = [
            "//div[@id='xxdm4hwb-88oz']//input"
        ]

        # 全部新增输入框xpath
        self.all_input_add_xpath_list = [
            "//div[@id='p34nag46-7evf']//input",
            "//div[@id='x1k7t87i-tvc3']//input",
            "//div[@id='hpjqsv1m-5607']//input",
            "//div[@id='o7c9sdve-vat3']//input",
            "//div[@id='z0h20cps-xzrs']//input",
            "//div[@id='7z1rv7fs-trb6']//input",
            "//div[@id='hguo4esk-gii0']//input",
            "//div[@id='13j55ae1-8hj2']//input",
            "//div[@id='u2tgl5h9-otp1']//input",
            "//div[@id='izykzohi-1l5u']//input",
            "//div[@id='ctfddy1k-hbmj']//input",
            "//div[@id='0t8pfkrw-y5i1']//input",
            "//div[@id='8sgoh6vh-0pz5']//input",
            "//div[@id='poxayyhi-9bss']//input",
            "//div[@id='zxc6ccwu-bnwe']//input",
            "//div[@id='15qig6pt-sj1x']//input",
            "//div[@id='vtxj45fl-aisi']//input",
            "//div[@id='owcpuvmy-it09']//input",
            "//div[@id='er1s533b-0paw']//input",
            "//div[@id='wfvjlw8j-lsr3']//input",
            "//div[@id='54dzbof5-6mq9']//input",
            "//div[@id='bq6dy8uc-2f58']//input",
            "//div[@id='f4s9lqcm-b3vk']//input",
            "//div[@id='xieapx7h-udjh']//input",
            "//div[@id='06giwjn5-paij']//input",
            "//div[@id='vfn272xc-c16a']//input",
            "//div[@id='69p938gi-8t8g']//input",
            "//div[@id='z5cusmj6-zosk']//input",
            "//div[@id='37xq7un7-s4m5']//input",
            "//div[@id='va14hagj-w77v']//input",
            "//div[@id='e36ys4xo-01oy']//input",
            "//div[@id='dzvafbkd-hwk9']//input",
            "//div[@id='974x2e7b-rx1m']//input",
            "//div[@id='ij6k2eer-xb3u']//input",
            "//div[@id='28hqxacj-chmp']//input",
            "//div[@id='e1fyxz6h-mj9x']//input",
            "//div[@id='uiun978m-mdn3']//input",
            "//div[@id='jzirnz2w-6fem']//input",
            "//div[@id='zm89zk0r-e782']//input",
            "//div[@id='e1pyaon3-k1eh']//input",
            "//div[@id='drb3rov9-q8f2']//input",
            "//div[@id='5tzijetj-ob6n']//input",
            "//div[@id='kujkk9tn-bnmn']//input",
            "//div[@id='qvrhe2xd-s6uu']//input",
            "//div[@id='rmeuzwr0-gtqy']//input",
            "//div[@id='asdsp21x-qbka']//input",
            "//div[@id='hgtdih0s-1ie4']//input",
            "//div[@id='8rlm7oth-yi3r']//input",
            "//div[@id='uafv1de6-k77k']//input",
            "//div[@id='d9uep78z-5zxc']//input",
            "//div[@id='6af64sxo-b2ac']//input",
            "//div[@id='n7053czm-srdl']//input",
            "//div[@id='ik0s12ng-ska9']//input",
            "//div[@id='l48g7h0f-85cj']//input",
            "//div[@id='otvthk5d-czv1']//input",
            "//div[@id='kcv87dqw-sm22']//input",
            "//div[@id='ux7yaskm-71t5']//input",
            "//div[@id='t56y6w72-40i2']//input",
            "//div[@id='tyzfbwoo-ys88']//input",
            "//div[@id='twgt8chq-ctoa']//input",
            "//div[@id='1x7g7tj2-0vuk']//input",
            "//div[@id='0rvbf2z1-q39y']//input",
            "//div[@id='24nfdfen-dz26']//input",
            "//div[@id='rokfnb8f-gymo']//input",
            "//div[@id='wq6ze0wy-fyf1']//input",
            "//div[@id='tngz2fut-wx40']//input",
            "//div[@id='9v6h3scy-532s']//input"
        ]
        # 全部新增日期xpath
        self.all_date_add_xpath_list = [
            "//div[@id='ve4rvcq7-uzud']//input",
            "//div[@id='uxa4hsnc-hgho']//input",
            "//div[@id='zqn5nb1p-yfa1']//input",
            "//div[@id='g54lrvnf-fppt']//input",
            "//div[@id='cjkrwbsl-2cvp']//input",
            "//div[@id='0l3qmi9w-0dwn']//input",
            "//div[@id='40icw6bw-08lt']//input",
            "//div[@id='6mqa6ruc-zbkc']//input",
            "//div[@id='cw46u1dl-cbr0']//input",
            "//div[@id='4fvh0y7p-obtj']//input",
            "//div[@id='1x775ocr-yhtz']//input",
        ]
        # 全部编辑输入框xpath
        self.all_input_edit_xpath_list = [
            "//div[@id='xxdm4hwb-88oz']//input",
            "//div[@id='raw8hfaq-k2du']//input",
            "//div[@id='yk77ugj2-s586']//input",
            "//div[@id='xgz8rq0k-htcj']//input",
            "//div[@id='96arnxwl-dxue']//input",
            "//div[@id='nw0df8kh-5920']//input",
            "//div[@id='757sfdzn-wjou']//input",
            "//div[@id='g8fcite7-19u8']//input",
            "//div[@id='nzgv0lp6-z1sy']//input",
            "//div[@id='nug866o8-ppek']//input",
            "//div[@id='v9gg0ude-l9tg']//input",
            "//div[@id='pgpztke9-p9qp']//input",
            "//div[@id='hev11z9g-574p']//input",
            "//div[@id='ag1nw49w-c02s']//input",
            "//div[@id='3cbzhsv2-x7r0']//input",
            "//div[@id='ry68apal-hwqd']//input",
            "//div[@id='80gk8mpo-f65l']//input",
            "//div[@id='80ahaedh-cesq']//input",
            "//div[@id='s7a6wh6g-v8cj']//input",
            "//div[@id='rzvic0i6-3ek6']//input",
            "//div[@id='9rf9bu0s-s8yz']//input",
            "//div[@id='b2b0zksr-iv7u']//input",
            "//div[@id='kusb5kyi-ru6a']//input",
            "//div[@id='gtml8d0f-z1yy']//input",
            "//div[@id='efy4fie1-rliv']//input",
            "//div[@id='x3k6cozy-x0s7']//input",
            "//div[@id='7rl5uad4-cjiw']//input",
            "//div[@id='gyhfuhz1-bsl1']//input",
            "//div[@id='uaj49u6z-oqlz']//input",
            "//div[@id='a8ct2kiu-p48b']//input",
            "//div[@id='9hluy7kb-rwn3']//input",
            "//div[@id='8qexj2ui-3sb4']//input",
            "//div[@id='x6zxd0cu-o1dj']//input",
            "//div[@id='ylp3wb1v-vncf']//input",
            "//div[@id='h8ekc2m1-z44m']//input",
            "//div[@id='so512s23-diin']//input",
            "//div[@id='ddim6piu-n0x6']//input",
            "//div[@id='iplqpnwh-fn0j']//input",
            "//div[@id='zslw6tid-oujk']//input",
            "//div[@id='4mektpw7-mry2']//input",
            "//div[@id='wrw3u200-wyaz']//input",
            "//div[@id='rkr1yx9b-mzzv']//input",
            "//div[@id='sg9x6475-8pgr']//input",
            "//div[@id='d3623sfb-ktv0']//input",
            "//div[@id='lv6f9d3n-oulm']//input",
            "//div[@id='lw71uzna-jmlc']//input",
            "//div[@id='s28wce4z-pxkk']//input",
            "//div[@id='btnxhwl0-64d6']//input",
            "//div[@id='qp3jbw9z-ajkg']//input",
            "//div[@id='665mq0if-whp5']//input",
            "//div[@id='dex3z32o-2i2c']//input",
            "//div[@id='repl1x27-7hfb']//input",
            "//div[@id='3j7w51rl-fssc']//input",
            "//div[@id='3ud1gsyk-4rn2']//input",
            "//div[@id='1r8a0m59-e678']//input",
            "//div[@id='rjwdg8c0-15ax']//input",
            "//div[@id='w1hwv12d-tnw7']//input",
            "//div[@id='48f57lw6-ggc1']//input",
            "//div[@id='1juinoup-ickh']//input",
            "//div[@id='0pgi6czf-cwmk']//input",
            "//div[@id='j1f816zc-awi1']//input",
            "//div[@id='o1s3va2l-rq90']//input",
            "//div[@id='t0754a74-2hki']//input",
            "//div[@id='rrok0r9m-rd1h']//input",
            "//div[@id='w7q7duxg-fcvc']//input",
            "//div[@id='0x3ofjrd-lyqi']//input",
            "//div[@id='pkd086zj-cgum']//input"
        ]
        # 全部编辑输入框xpath
        self.all_input_edit_xpath_list2 = [
            "//div[@id='xxdm4hwb-88oz']//input",
            "//div[@id='raw8hfaq-k2du']//input",
            "//div[@id='yk77ugj2-s586']//input",
            "//div[@id='xgz8rq0k-htcj']//input",
            "//div[@id='96arnxwl-dxue']//input",
            "//div[@id='nw0df8kh-5920']//input",
            "//div[@id='757sfdzn-wjou']//input",
            "//div[@id='g8fcite7-19u8']//input",
            "//div[@id='nzgv0lp6-z1sy']//input",
            "//div[@id='nug866o8-ppek']//input",
            "//div[@id='v9gg0ude-l9tg']//input",
            "//div[@id='pgpztke9-p9qp']//input",
            "//div[@id='hev11z9g-574p']//input",
            "//div[@id='ag1nw49w-c02s']//input",
            "//div[@id='3cbzhsv2-x7r0']//input",
            "//div[@id='ry68apal-hwqd']//input",
            "//div[@id='80gk8mpo-f65l']//input",
            "//div[@id='80ahaedh-cesq']//input",
            "//div[@id='s7a6wh6g-v8cj']//input",
            "//div[@id='rzvic0i6-3ek6']//input",
            "//div[@id='9rf9bu0s-s8yz']//input",
            "//div[@id='b2b0zksr-iv7u']//input",
            "//div[@id='kusb5kyi-ru6a']//input",
            "//div[@id='gtml8d0f-z1yy']//input",
            "//div[@id='efy4fie1-rliv']//input",
            "//div[@id='x3k6cozy-x0s7']//input",
            "//div[@id='7rl5uad4-cjiw']//input",
            "//div[@id='gyhfuhz1-bsl1']//input",
            "//div[@id='uaj49u6z-oqlz']//input",
            "//div[@id='a8ct2kiu-p48b']//input",
            "//div[@id='9hluy7kb-rwn3']//input",
            "//div[@id='8qexj2ui-3sb4']//input",
            "//div[@id='x6zxd0cu-o1dj']//input",
            "//div[@id='ylp3wb1v-vncf']//input",
            "//div[@id='h8ekc2m1-z44m']//input",
            "//div[@id='so512s23-diin']//input",
            "//div[@id='ddim6piu-n0x6']//input",
            "//div[@id='iplqpnwh-fn0j']//input",
            "//div[@id='zslw6tid-oujk']//input",
            "//div[@id='4mektpw7-mry2']//input",
            "//div[@id='wrw3u200-wyaz']//input",
            "//div[@id='rkr1yx9b-mzzv']//input",
            "//div[@id='sg9x6475-8pgr']//input",
            "//div[@id='d3623sfb-ktv0']//input",
            "//div[@id='lv6f9d3n-oulm']//input",
            "//div[@id='lw71uzna-jmlc']//input",
            "//div[@id='s28wce4z-pxkk']//input",
            "//div[@id='btnxhwl0-64d6']//input",
            "//div[@id='qp3jbw9z-ajkg']//input",
            "//div[@id='665mq0if-whp5']//input",
            "//div[@id='dex3z32o-2i2c']//input",
            "//div[@id='repl1x27-7hfb']//input",
            "//div[@id='3j7w51rl-fssc']//input",
            "//div[@id='3ud1gsyk-4rn2']//input",
            "//div[@id='1r8a0m59-e678']//input",
            "//div[@id='rjwdg8c0-15ax']//input",
            "//div[@id='w1hwv12d-tnw7']//input",
            "//div[@id='48f57lw6-ggc1']//input",
            "//div[@id='1juinoup-ickh']//input",
            "//div[@id='0pgi6czf-cwmk']//input",
            "//div[@id='j1f816zc-awi1']//input",
            "//div[@id='o1s3va2l-rq90']//input",
            "//div[@id='t0754a74-2hki']//input",
            "//div[@id='rrok0r9m-rd1h']//input",
            "//div[@id='w7q7duxg-fcvc']//input",
            "//div[@id='0x3ofjrd-lyqi']//input",
            "//div[@id='pkd086zj-cgum']//input"
        ]
        # 全部编辑日期xpath
        self.all_date_edit_xpath_list = [
            "//div[@id='fgyxquch-4wje']//input",
            "//div[@id='ua4j0146-u49a']//input",
            "//div[@id='jnr283ac-yux7']//input",
            "//div[@id='rb98vw8g-701r']//input",
            "//div[@id='1xnkkpo2-rj2i']//input",
            "//div[@id='8181e2fc-986o']//input",
            "//div[@id='lqujatyp-fedp']//input",
            "//div[@id='919pggd3-r3uk']//input",
            "//div[@id='grn33r4t-udxe']//input",
            "//div[@id='2iq92l05-r4r3']//input",
            "//div[@id='s6y8mqwq-bmje']//input"
        ]
        self.all_date_edit_xpath_list2 = [
            "//div[@id='fgyxquch-4wje']//input",
            "//div[@id='ua4j0146-u49a']//input",
            "//div[@id='jnr283ac-yux7']//input",
            "//div[@id='rb98vw8g-701r']//input",
            "//div[@id='1xnkkpo2-rj2i']//input",
            "//div[@id='8181e2fc-986o']//input",
            "//div[@id='lqujatyp-fedp']//input",
            "//div[@id='919pggd3-r3uk']//input",
            "//div[@id='grn33r4t-udxe']//input",
            "//div[@id='2iq92l05-r4r3']//input",
            "//div[@id='s6y8mqwq-bmje']//input"
        ]

    @allure.story("添加采购PO信息 不填写数据点击确认 不允许提交")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_addfail(self, login_to_item):
        sleep(3)
        find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
        if len(find_layout) == 0:
            layout = "测试布局A"
            self.item.add_layout(layout)
            # 获取布局名称的文本元素
            name = self.item.get_find_element_xpath(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
            ).text
        # 点击新增按钮
        self.item.click_add_button()
        # # 清空数字输入框
        # ele.send_keys(Keys.CONTROL, "a")
        # ele.send_keys(Keys.BACK_SPACE)
        # sleep(1)
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none(self.req_input_add_xpath_list, color_value)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加交付需求明细信息，有多个必填只填写一项，不允许提交")
    # @pytest.mark.run(order=2)
    def test_MaterialCTB_addcodefail(self, login_to_item):
        # 点击新增按钮
        self.item.click_add_button()
        # 点击确定
        self.item.click_button('(//button[@type="button"]/span[text()="确定"])[5]')
        sleep(1)
        # 声明必填项的xpath和判断的边框颜色
        xpath_list = [
            "//div[@id='p34nag46-7evf']//input"
        ]
        color_value = "rgb(255, 0, 0)"
        # 获取必填项公共方法判断颜色的结果
        val = self.item.add_none(xpath_list, color_value)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert val
        assert not self.item.has_fail_message()

    @allure.story("添加必填数据成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_addsuccess(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(1)
        # ele = self.item.get_find_element_xpath(
        #     "//div[@id='ywz9q11i-sp3b']//input"
        # )
        # # 清空数字输入框
        # ele.send_keys(Keys.CONTROL, "a")
        # ele.send_keys(Keys.BACK_SPACE)
        self.item.click_button("//div[@id='sx71la2d-fxkx']")
        sleep(1)
        self.item.click_button('//span[text()="半成品"]')

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
        input_values2 = self.item.batch_acquisition_input(["//div[@id='ynwjewx5-p2ol']//input"], '半成品')
        # 批量获取日期选择框的value

        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.req_input_add_xpath_list) == len(input_values) and
                len(input_values2) == 1
        )
        assert not self.item.has_fail_message()

    @allure.story("添加数据重复")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_addrepeat(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"

        sleep(1)
        # ele = self.item.get_find_element_xpath(
        #     "//div[@id='ywz9q11i-sp3b']//input"
        # )
        # # 清空数字输入框
        # ele.send_keys(Keys.CONTROL, "a")
        # ele.send_keys(Keys.BACK_SPACE)
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
    def test_MaterialCTB_delcancel(self, login_to_item):

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
    def test_MaterialCTB_addsuccess1(self, login_to_item):

        self.item.click_add_button()  # 检查点击添加
        # 输入框要修改的值
        text_str = "222"
        # ele = self.item.get_find_element_xpath(
        #     "//div[@id='ywz9q11i-sp3b']//input"
        # )
        # # 清空数字输入框
        # ele.send_keys(Keys.CONTROL, "a")
        # ele.send_keys(Keys.BACK_SPACE)
        sleep(1)
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
    def test_MaterialCTB_editcodesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "333"
        # 输入框的xpath

        sleep(3)
        # 选中刚刚新增的测试数据
        self.item.click_button('//tr[./td[2][.//span[text()="222"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

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
    def test_MaterialCTB_editrepeat(self, login_to_item):
        # 选中1测试A工厂代码
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

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
    def test_MaterialCTB_delsuccess1(self, login_to_item):
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
    def test_MaterialCTB_editnamesuccess(self, login_to_item):

        # 输入框要修改的值
        text_str = "111"
        date_str = "2025/07/23 00:00:00"
        sleep(4)
        # 选中编辑数据
        self.item.click_button('//tr[./td[2][.//span[text()="333"]]]/td[2]')
        # 点击修改按钮
        self.item.click_edi_button()
        sleep(1)

        # 批量修改输入框
        self.item.batch_modify_input(self.all_input_edit_xpath_list, text_str)
        self.item.batch_modify_input(self.all_date_edit_xpath_list, date_str)

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
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
            len(self.all_input_edit_xpath_list) == len(input_values) and
            len(self.all_date_edit_xpath_list) == len(input_values2)
        )
        assert not self.item.has_fail_message()

    @allure.story("删除测试数据成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_delsuccess2(self, login_to_item):
        sleep(4)
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

    @allure.story("过滤刷新成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_refreshsuccess(self, login_to_item):
        sleep(4)
        filter_results = self.item.filter_method('//span[text()=" 物料编号"]/ancestor::div[3]//span//span//span')
        print('filter_results', filter_results)
        assert filter_results
        assert not self.item.has_fail_message()

    @allure.story("新增全部数据测试")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_add_success(self, login_to_item):
        # 输入框要修改的值
        text_str = "111"
        # 日期要修改的值
        date_str = "2025/07/17 00:00:00"
        self.item.click_add_button()  # 点击添加
        sleep(1)
        # ele = self.item.get_find_element_xpath(
        #     "//div[@id='ywz9q11i-sp3b']//input"
        # )
        # # 清空数字输入框
        # ele.send_keys(Keys.CONTROL, "a")
        # ele.send_keys(Keys.BACK_SPACE)
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
        input_values = self.item.batch_acquisition_input(self.all_input_edit_xpath_list2, text_str)
        # 批量获取日期的value
        date_values = self.item.batch_acquisition_input(self.all_date_edit_xpath_list2, date_str)
        sleep(1)
        self.item.click_button('(//button[@type="button"]/span[text()="取消"])[5]')
        assert (
                len(self.all_input_add_xpath_list) == len(input_values)
                and len(self.all_date_add_xpath_list) == len(date_values)
        )
        assert not self.item.has_fail_message()

    @allure.story("查询测试数据成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_selectcodesuccess(self, login_to_item):
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
        item.click_button('//div[text()="物料编号" and contains(@optid,"opt_")]')
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
    def test_MaterialCTB_selectnodatasuccess(self, login_to_item):

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
        self.item.click_button('//div[text()="物料编号" and contains(@optid,"opt_")]')
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
        # 点击刷新
        self.item.click_ref_button()
        assert len(itemcode) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，一个不选，显示正常")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_select2(self, login_to_item):
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        sleep(1)
        eles = self.item.get_find_element_xpath(
            '(//div[@class="vxe-pulldown--panel-wrapper"])//label/span').get_attribute(
            "class")
        if eles == "ivu-checkbox ivu-checkbox-checked":
            self.item.click_button('(//div[@class="vxe-pulldown--panel-wrapper"])//label/span')
            self.item.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//input')
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        self.item.right_refresh('物料CTB')
        assert len(eles) == 0
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置包含条件查询成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_select3(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('物料编号', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('物料CTB')
        assert all(first_char in text for text in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合开头查询成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_select4(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        first_char = name[:1] if name else ""
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合开头")
        sleep(1)
        self.item.select_input('物料编号', first_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('物料CTB')
        assert all(str(item).startswith(first_char) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("过滤条件查询，设置符合结尾查询成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_select5(self, login_to_item):

        name = self.item.get_find_element_xpath(
            '//div[@class="vxe-table--body-wrapper body--wrapper"]/table[@class="vxe-table--body"]//tr[2]//td[2]'
        ).get_attribute('innerText')
        last_char = name[-1:] if name else ""
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("符合结尾")
        sleep(1)
        self.item.select_input('物料编号', last_char)
        sleep(1)
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        sleep(1)
        list_ = [ele.text for ele in eles]
        self.item.right_refresh('物料CTB')
        assert all(str(item).endswith(last_char) for item in list_)
        assert not self.item.has_fail_message()

    @allure.story("清除筛选效果成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_clear(self, login_to_item):

        name = "3"
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("包含")
        sleep(1)
        self.item.select_input('物料编号', name)
        sleep(1)
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]')
        self.item.hover("清除所有筛选条件")
        sleep(1)
        ele = self.item.get_find_element_xpath(
            '//div[div[span[text()=" 物料编号"]]]//i[contains(@class,"suffixIcon")]').get_attribute(
            "class")
        self.item.right_refresh('物料CTB')
        assert ele == "vxe-icon-funnel suffixIcon"
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+i添加重复")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_ctrlIrepeat(self, login_to_item):

        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        ele1 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').get_attribute(
            "innerText")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = self.item.get_find_element_xpath('//div[text()=" 记录已存在,请检查！ "]').get_attribute("innerText")
        self.item.click_button('//div[@class="ivu-modal-footer"]//span[text()="关闭"]')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert message == '记录已存在,请检查！'
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_ctrlI(self, login_to_item):

        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据添加')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('物料编号', '1没有数据添加')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2 == '1没有数据添加'
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+m修改")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_ctrlM(self, login_to_item):

        self.item.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改')
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input').get_attribute(
            "value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('物料编号', '1没有数据修改')
        ele2 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele2
        assert not self.item.has_fail_message()

    @allure.story("模拟多选删除")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_shiftdel(self, login_to_item):
        self.item.right_refresh('物料CTB')
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        sleep(1)
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]//input', '1没有数据修改1')
        self.item.click_button('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]')
        self.item.enter_texts('(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input', '1没有数据修改12')
        sleep(1)
        ele1 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[1]/td[2])[2]').text
        ele2 = self.item.get_find_element_xpath(
            '(//table[@class="vxe-table--body"]//tr[2]/td[2])[2]//input').get_attribute("value")
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.item.get_find_message()
        self.item.select_input('物料编号', '1没有数据修改1')
        ele11 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[1]/td[2])[1]').get_attribute(
            "innerText")
        ele22 = self.item.get_find_element_xpath('(//table[@class="vxe-table--body"]//tr[2]/td[2])[1]').get_attribute(
            "innerText")
        assert ele1 == ele11 and ele2 == ele22
        assert not self.item.has_fail_message()
        self.item.select_input('物料编号', '1没有数据修改')
        before_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        before_count = int(re.search(r'\d+', before_data).group())
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[3]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[2])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        self.item.click_del_button()
        self.item.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = self.item.get_find_message()
        self.item.wait_for_loading_to_disappear()
        after_data = self.item.get_find_element_xpath('(//span[contains(text(),"条记录")])[1]').text
        after_count = int(re.search(r'\d+', after_data).group())
        assert message == "删除成功！"
        assert before_count - after_count == 3, f"删除失败: 删除前 {before_count}, 删除后 {after_count}"
        assert not self.item.has_fail_message()

    @allure.story("模拟ctrl+c复制可查询")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_ctrlC(self, login_to_item):
        self.item.right_refresh('物料CTB')
        self.item.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        before_data = self.item.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        self.item.click_button('//div[div[span[text()=" 物料编号"]]]//input')
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        eles = self.item.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr[2]//td[2]')
        eles = [ele.text for ele in eles]
        self.item.right_refresh('物料CTB')
        assert all(before_data in ele for ele in eles)
        assert not self.item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+i添加")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_shift(self, login_to_item):

        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('i').key_up(Keys.CONTROL).perform()
        num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert len(num) == 2
        assert not self.item.has_fail_message()

    @allure.story("模拟Shift+点击可多选ctrl+m编辑")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_ctrls(self, login_to_item):

        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        self.item.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = self.item.get_find_element_xpath(elements[1])
        ActionChains(self.driver).key_down(Keys.CONTROL).click(cell2).key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('m').key_up(Keys.CONTROL).perform()
        num = self.item.finds_elements(By.XPATH, '(//table[@class="vxe-table--body"])[last()]//tr')
        self.item.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        message = self.item.get_find_message()
        assert len(num) == 2 and message == "保存成功"
        assert not self.item.has_fail_message()

    @allure.story("删除数据成功")
    # @pytest.mark.run(order=1)
    def test_MaterialCTB_delsuccess3(self, login_to_item):
        layout_name = "测试布局A"
        sleep(4)
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
        layout = self.driver.find_elements(By.CLASS_NAME, "tabsDivItem")
        print('layout', len(layout))
        if len(layout) > 1:
            self.item.del_layout(layout_name)
        # 定位内容为‘111’的行
        itemdata = self.driver.find_elements(
            By.XPATH, '//tr[./td[2][.//span[text()="111"]]]/td[2]'
        )
        assert len(itemdata) == 0
        assert not self.item.has_fail_message()

    # @allure.story("测试")
    # # @pytest.mark.run(order=1)
    # def test_demo_delsuccess3(self, login_to_item):
    #     find_layout = self.driver.find_elements(By.XPATH, '//div[text()=" 测试布局A "]')
    #     print('layout', len(find_layout))
    #     input()
