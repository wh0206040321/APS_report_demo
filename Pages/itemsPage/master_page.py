import random
from time import sleep

from selenium.common import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class MasterPage(BasePage):
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

    def add_serial1(self):
        """序号添加按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[1]')

    def del_serial1(self):
        """序号删除按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[2]')

    def add_serial2(self):
        """序号添加按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[3]')

    def del_serial2(self):
        """序号删除按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[4]')

    def add_serial3(self):
        """序号添加按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[5]')

    def del_serial3(self):
        """序号删除按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[6]')

    def add_serial4(self):
        """序号添加按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[7]')

    def del_serial4(self):
        """序号删除按钮."""
        self.click(By.XPATH, '(//button[@class="m-b-10 ivu-btn ivu-btn-default"])[8]')

    def wait_for_loading_to_disappear(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def add_ok_button(self):
        """点击添加确定按钮"""
        self.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]/button[1]'
        )
        self.wait_for_loading_to_disappear()

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

    def get_message(self):
        """获取信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--success"]/p')
            )
        )
        return message.text

    def get_find_element_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def get_find_elements_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        self.finds_elements(By.XPATH, xpath)

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def go_item_dialog(self, test_item):
        """选择物料代码"""
        # 填写订物料代码
        self.click_button('//span[text()=" 物料代码： "]/parent::div//i')
        self.wait_for_loading_to_disappear()
        self.click_button(
            f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{test_item}"]'
        )
        sleep(1)
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')

    def delete_material(self, test_item):
        """删除工艺产能"""
        wait = WebDriverWait(self.driver, 3)
        # 循环删除元素直到不存在
        while True:
            self.wait_for_loading_to_disappear()
            eles = self.driver.find_elements(
                By.XPATH,
                f'//tr[.//span[text()="{test_item}"]]/td[2]//span[text()="{test_item}"]',
            )
            if not eles:
                break  # 没有找到元素时退出循环
                # 存在元素，点击删除按钮
            eles[0].click()
            self.click_del_button()
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            # 等待元素消失
            try:
                wait.until_not(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            f'//tr[.//span[text()="{test_item}"]]/td[2]//span[text()="{test_item}"]',
                        )
                    )
                )
            except TimeoutException:
                print("警告：元素未在预期时间内消失")
                continue  # 继续下一轮尝试
            else:
                # 不再找到元素，退出循环
                break

    def check_master_exists(self, item_name):
        try:
            self.get_find_element_xpath(
                f'//tr[.//span[text()="{item_name}"]]/td[2]//span[text()="{item_name}"]'
            )
            return True
        except:
            return False

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

    def add_layout(self, layout):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')
        self.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
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
        sleep(2)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
