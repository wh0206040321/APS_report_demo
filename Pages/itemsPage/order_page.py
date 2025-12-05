import random
from time import sleep
from datetime import date, datetime
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from Pages.base_page import BasePage
import time

class OrderPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def click_add_button(self):
        """点击添加按钮."""
        self.click(By.XPATH, '//p[text()="新增"]')

    def click_edi_button(self):
        """点击修改按钮."""
        self.click(By.XPATH, '//p[text()="编辑"]')

    def click_del_button(self):
        """点击删除按钮."""
        self.click(By.XPATH, '//p[text()="删除"]')

    def click_sel_button(self):
        """点击查询按钮."""
        self.click(By.XPATH, '//p[text()="查询"]')

    def click_ref_button(self):
        """点击刷新按钮."""
        self.click(By.XPATH, '//p[text()="刷新"]')

    def enter_texts(self, xpath, text):
        """输入文字."""
        self.enter_text(By.XPATH, xpath, text)

    def click_button(self, xpath):
        """点击按钮."""
        self.click(By.XPATH, xpath)

    def get_find_element_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def loop_judgment(self, xpath):
        """循环判断"""
        eles = self.finds_elements(By.XPATH, xpath)
        code = [ele.text for ele in eles]
        return code

    def click_confirm_button(self):
        """点击确定按钮."""
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        self.wait_for_loading_to_disappear()

    def click_select_button(self):
        """点击查询确定按钮."""
        self.click_button('(//div[@class="demo-drawer-footer"]//span[text()="确定"])[3]')
        sleep(0.5)
        self.wait_for_loading_to_disappear()

    def wait_for_loading_to_disappear(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'vxe-loading'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def add_order(self, code, order_item):
        self.click_add_button()
        # 填写订单代码
        self.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', code)
        # 物料
        self.click_button('//label[text()="物料"]/parent::div/div//i')
        try:
            self.click_button(
                f'(//div[@class="vxe-table--body-wrapper body--wrapper"]//table//tr/td[3]//span[text()="{order_item}"])[1]')
        except:
            self.click_button(
                f'(//div[@class="vxe-table--body-wrapper body--wrapper"]//table//tr/td[3]//span[text()="{order_item}"])[2]')
        self.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]/button[1]'
        )

        # 填写交货期
        self.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        self.click_button(
            '//div[@class="ivu-select-dropdown ivu-date-picker-transfer setZindex"]//div[@class="ivu-date-picker-header"]//span[@class="ivu-picker-panel-icon-btn ivu-date-picker-next-btn ivu-date-picker-next-btn-arrow"]/i'
        )
        self.click_button(
            '//div[@class="ivu-select-dropdown ivu-date-picker-transfer setZindex"]//div[@class="ivu-date-picker-cells"]//em[text()="20"]'
        )
        self.click_button(
            '//div[@class="ivu-select-dropdown ivu-date-picker-transfer setZindex"]//div[@class="ivu-picker-confirm"]//button[3]'
        )

        # 计划数量
        num = self.get_find_element_xpath(
            '(//label[text()="计划数量"])[1]/parent::div//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.BACK_SPACE)
        self.enter_texts('(//label[text()="计划数量"])[1]/parent::div//input', "200")
        confirm_xpath = '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[5]/button[1]'
        backup_xpath = '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[4]/button[1]'
        backup2_xpath = '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]/button[1]'
        if self.is_clickable(confirm_xpath):
            self.click_button(confirm_xpath)
        elif self.is_clickable(backup_xpath):
            self.click_button(backup_xpath)
        elif self.click_button(backup2_xpath):
            self.click_button(backup2_xpath)

    def delete_order(self, code):
        # 判断是否存在该订单
        elements = self.driver.find_elements(
            By.XPATH, f'(//span[text()="{code}"])[1]/ancestor::tr[1]/td[2]'
        )
        if not elements:
            print(f"订单 {code} 不存在，跳过删除。")
            return  # 跳过删除操作

        self.click_button(f'(//span[text()="{code}"])[1]/ancestor::tr[1]/td[2]')
        self.click_del_button()  # 点击删除按钮

        # 查找确认框并点击“确定”
        parent = self.get_find_element_class("ivu-modal-confirm-footer")
        if parent is None:
            print("未找到确认框，可能弹窗未出现或页面加载失败。")
            return

        all_buttons = parent.find_elements(By.TAG_NAME, "button")
        if len(all_buttons) > 1:
            all_buttons[1].click()  # 点击第二个按钮（确定）
        else:
            print("确认按钮数量不足，无法点击。")

    def check_order_exists(self, order_name):
        try:
            self.get_find_element_xpath(f'//span[text()="{order_name}"]')
            return True
        except:
            return False

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def get_find_message(self):
        """获取错误信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--success"]/p')
            )
        )
        return message.text

    def get_error_message(self):
        """获取错误信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--error"]/p')
            )
        )
        return message.text

    def is_clickable(self, xpath, timeout=5):
        """
        判断指定的元素是否可点击。
        :param xpath: 要检查的 XPath
        :param timeout: 等待超时时间（秒）
        :return: True/False
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            return True
        except TimeoutException:
            return False

    def click_setting_button(self):
        """点击设置按钮."""
        self.click_button('(//i[@style="cursor: pointer;"])[2]')

    def add_layout(self, layout):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')
        self.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        sleep(0.5)
        checkbox1 = self.get_find_element_xpath(
            '//div[text()="是否默认启动:"]/following-sibling::label/span'
        )

        # 检查复选框是否未被选中
        if checkbox1.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            self.click_button(
                '//div[text()="是否默认启动:"]/following-sibling::label/span'
            )
        sleep(1)

        self.click_button('(//div[text()=" 显示设置 "])[1]')
        # 获取是否可见选项的复选框元素
        checkbox2 = self.get_find_element_xpath(
            '(//div[./div[text()="是否可见:"]])[1]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox2.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            self.click_button('(//div[./div[text()="是否可见:"]])[1]/label/span')
            # 点击确定按钮保存设置
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

    def del_all(self, value=[], xpath=''):
        for index, v in enumerate(value, start=1):
            try:
                self.enter_texts(xpath, v)
                sleep(0.5)
                self.click_button(f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
                self.click_del_button()  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                self.wait_for_loading_to_disappear()
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)

    def del_layout(self, layout):
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = self.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = self.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）

        self.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        self.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(1)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def click_order_page(self, name):
        """点击不同订单页"""
        self.click_button(f'(//span[text()="{name}"])[1]')

    def add_order_data(self, name):
        """添加数据."""

        self.click_add_button()  # 检查点击添加
        # 输入代码
        self.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', name)
        self.enter_texts('(//label[text()="物料"])[1]/parent::div//input', name)
        self.click_button('(//label[text()="交货期"])[1]/parent::div//input')
        self.click_button('(//div[@class="ivu-date-picker-cells"])[3]/span[19]')
        self.click_button(
            '(//button[@class="ivu-btn ivu-btn-primary ivu-btn-small"])[3]'
        )
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def edit_order_data(self, before_name, after_name):
        """编辑数据."""
        self.click_button(f'//tr[./td[2][.//span[text()="{before_name}"]]]/td[2]')
        self.click_edi_button()  # 检查点击编辑
        # 输入代码
        self.enter_texts('(//label[text()="订单代码"])[1]/parent::div//input', after_name)
        self.enter_texts('(//label[text()="物料"])[1]/parent::div//input', after_name)
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def del_order_data(self, name):
        """删除数据."""
        eles = self.finds_elements(By.XPATH, f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        if len(eles) == 1:
            self.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
            self.click_del_button()  # 检查点击删除
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            self.wait_for_loading_to_disappear()

    def select_order_data(self, name):
        """查询数据."""
        self.click_sel_button()
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
        # 点击物料代码
        self.click_button('//div[text()="订单代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        self.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        self.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        self.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        self.click_select_button()
