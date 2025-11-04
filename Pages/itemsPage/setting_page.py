from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class SettingPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

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

    def add_layout(self):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')

    def wait_for_loading_to_disappear(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'vxe-loading'的div元素，
        以此判断加载遮罩是否消失。
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(
                    (By.XPATH,
                     "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
                )
            )
        except TimeoutException:
            print("等待超时：第二个加载动画未消失，但继续执行后续操作")
        except NoSuchElementException:
            print("找不到目标元素，但继续执行后续操作")
        sleep(1)

    def wait_for_el_loading_mask(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: (
                d.find_element(By.CLASS_NAME, "el-loading-mask").value_of_css_property("display") == "none"
                if d.find_elements(By.CLASS_NAME, "el-loading-mask") else True
            )
        )
        sleep(1)

    def click_confirm_button(self):
        """点击确认按钮."""
        self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        self.wait_for_loading_to_disappear()

    def add_layout_ok(self, layout):
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
        sleep(1)

    def add_pivot_table(self):
        """添加透视表."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加透视表"]')

    def click_setting_button(self):
        """点击设置按钮."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[3]//i')

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

    def click_ref_button(self):
        """点击刷新按钮."""
        self.click(By.XPATH, '//p[text()="刷新"]')

    def add_statistics(self, num='', data="", name="", code1='', code2='', code3=''):
        """添加统计."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        self.click_button('//div[./span[text()=" 统计 "]]//i')
        self.click_button(f'//h2[text()="图表"]/following-sibling::div/div[{num}]')
        if data:  # 如果 data 不为空，则输入
            self.click_button('//h2[text()="数据源"]/following-sibling::div[1]//i')
            sleep(1)
            self.click_button(f'//li[text()="{data}" and @class="ivu-select-item"]')
        if name:  # 如果 name 不为空，则输入
            self.enter_texts('//span[text()="图表名"]/following-sibling::div[1]//input', f"{name}")
        if code1 != '' and code2 != '':
            # 定义文本元素和目标输入框的 XPath
            text_elements = [
                f'//span[text()="{code1}"]',
                f'//span[text()="{code2}"]',
            ]

            input_elements = [
                '//h3[text()="X轴(维度)"]/following-sibling::div[1]',
                '//h3[text()="Y轴(数值)"]/following-sibling::div[1]',
            ]

            # 使用循环进行拖放操作
            for text_xpath, input_xpath in zip(text_elements, input_elements):
                sleep(1)
                text_element = self.get_find_element_xpath(text_xpath)
                input_element = self.get_find_element_xpath(input_xpath)
                ActionChains(self.driver).drag_and_drop(text_element, input_element).perform()

            sleep(1)
        elif code2 != '' and code3 != '':
            # 定义文本元素和目标输入框的 XPath
            text_elements = [
                f'//span[text()="{code2}"]',
                f'//span[text()="{code3}"]',
            ]

            input_elements = [
                '//h3[text()="Y轴(数值)"]/following-sibling::div[1]',
                '//h3[text()="分组"]/following-sibling::div[1]',
            ]

            # 使用循环进行拖放操作
            for text_xpath, input_xpath in zip(text_elements, input_elements):
                text_element = self.get_find_element_xpath(text_xpath)
                input_element = self.get_find_element_xpath(input_xpath)
                ActionChains(self.driver).drag_and_drop(text_element, input_element).perform()

    def add_lable(self, name=''):
        """添加标签."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        self.click_button('(//i[@class="el-tooltip ivu-icon ivu-icon-md-add"])[2]')
        if name:
            self.enter_texts('//div[text()="标签名："]/following-sibling::div/input', f"{name}")

    def hover(self, name=""):
        # 悬停模版容器触发图标显示
        container = self.get_find_element_xpath(
            f'//div[@id="container"]//span[text()="{name}"]'
        )
        sleep(3)
        ActionChains(self.driver).move_to_element(container).perform()
        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//div[@id="container"]//span[text()="{name}"]/ancestor::div[1]/div'
            ))
        )
        # 3️⃣ 再点击图标
        delete_icon.click()
