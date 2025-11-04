import random
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Pages.base_page import BasePage


class Calendar(BasePage):
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

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def get_find_message(self):
        """获取正确信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--error"]/p')
            )
        )
        return message.text

    def click_confirm_button(self):
        """点击确定按钮."""
        self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]/button[1]')
        self.wait_for_loading_to_disappear()

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

    def add_input_all(self, num):
        """输入框全部输入保存"""
        if num != "":
            # 点击资源
            self.click_button(
                '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
            )
            # 勾选框
            random_int = random.randint(1, 5)
            sleep(1)
            self.click_button(f'//table[@class="vxe-table--body"]//tr[{random_int}]/td[2]/div/span/span')

            self.click_button(
                '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
            )
            sleep(1)
            resource = self.get_find_element_xpath('//label[text()="资源"][1]/parent::div//input').get_attribute("value")

            # 点击班次
            self.click_button(
                '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[2]'
            )
            # 勾选框
            random_int1 = random.randint(1, 2)
            sleep(1)
            self.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]//span[@class="vxe-cell--checkbox"])[{random_int1}]')
            self.click_button(
                '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
            )
            sleep(1)
            shift = self.get_find_element_xpath('//label[text()="班次"][1]/parent::div//input').get_attribute("value")

            name = ["优先级", "资源量", "备注"]
            for index, value in enumerate(name, start=1):
                ele = self.get_find_element_xpath(f'//label[text()="{value}"][1]/parent::div//input')
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
                ele.send_keys(num)

            self.click_button('(//div[text()=" 星期 "])[1]')
            self.click_button(
                '//div[@class="d-flex"]/label/span'
            )
            self.click_button(
                '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]/button[1]'
            )
            return resource, shift

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

        try:
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
            )
        except TimeoutException:
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
            )
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
            )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        self.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

