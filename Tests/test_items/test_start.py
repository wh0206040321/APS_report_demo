import logging
import random
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Pages.itemsPage.item_page import ItemPage
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.master_page import MasterPage
from Pages.itemsPage.order_page import OrderPage
from Pages.itemsPage.plan_page import PlanPage
from Utils.data_driven import DateDriver
from Utils.shared_data_util import SharedDataUtil
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@allure.feature("添加物品，添加工艺产能，添加制造订单测试用例")
@pytest.mark.run(order=21)
class TestStartPage:
    @allure.story("添加物品，添加工艺产能，添加制造订单进行排产")
    # @pytest.mark.run(order=1)
    def test_start(self):
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

        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        # 初始化登录页面
        page = LoginPage(driver)  # 初始化登录页面
        # 清空之前的共享数据
        SharedDataUtil.clear_data()
        item.go_item()

        # 检查并添加物品（如果不存在）
        item_names = ["1测试A", "1测试B", "1测试C"]
        for name in item_names:
            if not item.check_item_exists(name):
                item.add_item(name, name)
            else:
                print(f"物品 {name} 已存在，跳过添加")

        page.click_button('(//span[text()="工艺产能"])[1]')  # 点击工艺产能
        master = MasterPage(driver)  # 用 driver 初始化 MasterPage
        sleep(1)
        # 检查工艺产能是否存在
        if not master.check_master_exists("1测试C"):
            master.click_add_button()  # 检查点击添加
            # 放大页面
            master.click_button('(//div[text()="新增工艺产能"])[2]/parent::div//i[1]')

            master.go_item_dialog("1测试C")
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
            random_sel1 = random.randint(1, 4)
            sleep(1)
            # 输入工序代码
            master.click_button(
                f'(//div[@class="vxe-select-option--wrapper"])[1]/div[{random_sel1}]'
            )

            # 点击新增输入指令
            master.add_serial3()
            # 获取物料名称
            master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
            master.wait_for_loading_to_disappear()
            master.click_button(
                '(//table[.//span[@class="vxe-cell--label"]])[2]//tr[.//span[text()="1测试A"]]/td[2]//span[text()="1测试A"]'
            )
            master.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
            # 获取物料数量
            random_num1 = random.randint(1, 100)
            master.enter_texts(
                '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
                f"{random_num1}",
            )

            # 点击使用指令
            master.click_button(
                '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
            )

            # 使用指令 点击对话框按钮 获取资源名称
            master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i')
            random_int1 = random.randint(1, 8)
            master.click_button(
                f'//tr[{random_int1}]/td//span[@class="vxe-cell--checkbox"]'
            )

            # 点击对话框按钮
            master.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
            sleep(2)
            master_res1 = master.get_find_element_xpath(
                '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//input'
            ).get_attribute("value")

            # 获取资源能力
            random_n = random.randint(1, 10)
            master.enter_texts(
                '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[7]//input',
                f"{random_n}pm",
            )

            # 点击新增工序编号
            master.add_serial2()
            # 填写工序编号
            master.enter_texts(
                '//table[.//div[@class="vxe-input type--number size--mini"]]//tr[2]/td[2]//input',
                "2",
            )
            # 点击下拉框
            master.click_button(
                '//table[@class="vxe-table--body"]//tr[2]/td[3]//input[@placeholder="请选择"]'
            )
            random_sel2 = random.randint(1, 4)
            sleep(1)
            # 输入工序代码
            master.click_button(
                f'(//div[@class="vxe-select-option--wrapper"])[2]/div[{random_sel2}]'
            )

            # 点击新增输入指令
            master.click_button(
                '//div[.//div[text()=" 输入指令 "] and @class="ivu-tabs-nav"]//div[text()=" 输入指令 "]'
            )
            master.add_serial3()
            # 获取物料名称
            master.click_button('(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[2]//i')
            master.wait_for_loading_to_disappear()
            master.click_button(
                '(//table[.//span[@class="vxe-cell--label"]])[2]//tr[.//span[text()="1测试B"]]/td[2]//span[text()="1测试B"]'
            )
            try:
                master.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[3]/button[1]')
            except:
                master.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

            # 获取物料数量
            random_num2 = random.randint(1, 100)
            master.enter_texts(
                '(//table[.//div[@class="vxe-input type--number size--mini"]])[2]//tr[1]/td[3]//input',
                f"{random_num2}",
            )

            # 点击使用指令 放大按钮
            master.click_button(
                '//div[.//div[text()=" 使用指令 "] and @class="ivu-tabs-nav"]//div[text()=" 使用指令 "]'
            )
            master.add_serial4()

            # 使用指令 点击对话框按钮 获取资源名称
            master.click_button('(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//i')
            random_int2 = random.randint(1, 8)
            while random_int2 == random_int1:
                random_int2 = random.randint(1, 8)

            sleep(2)
            master.click_button(
                f'//tr[{random_int2}]/td//span[@class="vxe-cell--checkbox"]'
            )
            sleep(1)
            # 点击对话框按钮
            master.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
            sleep(2)
            master_res2 = master.get_find_element_xpath(
                '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[5]//input'
            ).get_attribute("value")

            SharedDataUtil.save_data(
                {"master_res1": master_res1, "master_res2": master_res2}
            )

            # 获取资源能力
            random_n2 = random.randint(1, 10)
            master.enter_texts(
                '(//table[.//div[@class="vxe-input type--text size--mini is--controls"]])[3]//tr[1]/td[7]//input',
                f"{random_n2}pm",
            )

            # 点击确定
            confirm_xpath = '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
            backup_xpath = '(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]'

            if master.is_clickable(confirm_xpath):
                master.click_button(confirm_xpath)
            elif master.is_clickable(backup_xpath):
                master.click_button(backup_xpath)
            else:
                raise Exception("主按钮和备用按钮都不可点击，请检查页面状态")

        else:
            eles = driver.find_elements(
                By.XPATH,
                '//tr[.//td[2]//span[text()="1测试C"] and .//td[9]//div[text()=" 使用指令 "]]//td[11]',
            )
            master_res1 = eles[0].text
            master_res2 = eles[1].text
            SharedDataUtil.save_data(
                {"master_res1": master_res1, "master_res2": master_res2}
            )
            print("工艺产能 1测试C 已存在，跳过创建")

        order = OrderPage(driver)  # 用 driver 初始化 OrderPage
        list_ = ["计划业务数据", "制造订单"]
        for v in list_:
            page.click_button(f'(//span[text()="{v}"])[1]')

        # 检查制造订单是否存在
        if not order.check_order_exists("1测试C订单"):
            order.add_order("1测试C订单", "1测试C")
        else:
            print("制造订单 1测试C订单 已存在，跳过创建")

        plan = PlanPage(driver)
        wait = WebDriverWait(driver, 60)
        list_ = ["计划运行", "计算工作台", "计划计算"]
        for v in list_:
            if v == "计划计算":
                ele = plan.get_find_element_xpath(f'//li[div/div/span[text()="{list_[1]}"]]').get_attribute('aria-expanded')
                if ele is None:
                    plan.click_button(f'//li[div/div/span[text()="{list_[1]}"]]')
            page.click_button(f'(//span[text()="{v}"])[1]')
            sleep(1)

        # 等待遮挡元素消失
        wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-spinner"))
        )
        # 额外加一个短暂等待，确保UI稳定
        sleep(1)
        ele = driver.find_elements(By.XPATH, '//div[@class="vue-treeselect__control-arrow-container"]')
        if len(ele) == 0:
            list_ = ["系统管理", "单元设置", "环境设置"]
            for v in list_:
                page.click_button(f'(//span[text()="{v}"])[1]')
            sleep(1)
            # 点击勾选框
            input_ele = page.get_find_element('//label[text()=" 服务器"]/span')
            if input_ele.get_attribute("class") == "ivu-radio":
                page.click_button('//label[text()=" 服务器"]/span')
                sleep(1)
            page.click_button('//p[text()="保存"]')  # 点击保存
            sleep(3)
            list_ = ["计划运行", "计划计算"]
            for v in list_:
                page.click_button(f'(//span[text()="{v}"])[1]')

        # 等待下拉框按钮可点击后点击展开
        dropdown_arrow = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="vue-treeselect__control-arrow-container"]')
            )
        )
        sleep(3)
        dropdown_arrow.click()

        # 等待第一个方案标签可点击后点击选择
        first_option = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@class="vue-treeselect__list"]/div[1]',
                )
            )
        )
        first_option.click()

        # 执行计划
        plan.click_plan()

        # 等待“完成”的文本出现
        success_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '(//div[@class="d-flex"])[3]/p[text()=" 完成 "]')
            )
        )

        assert success_element.text == "完成"
        assert not item.has_fail_message()
        safe_quit(driver)
