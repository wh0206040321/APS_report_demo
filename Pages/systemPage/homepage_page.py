from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class HomePage(BasePage):
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

    def right_refresh(self, name="主页设置"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    # 等待加载遮罩消失
    def wait_for_loading_to_disappear(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, 30).until(
            lambda d: (
                d.find_element(By.CLASS_NAME, "el-loading-mask").value_of_css_property("display") == "none"
                if d.find_elements(By.CLASS_NAME, "el-loading-mask") else True
            )
        )
        sleep(1)

    def click_save_button(self):
        """点击保存按钮."""
        self.click_button('(//div[@class="d-flex m-b-7 toolBar"]//button)[1]')

    def click_template(self):
        self.click_button('//div[text()=" 模板 "]')

    def click_save_template_button(self, name="", button=""):
        """点击保存模版按钮."""
        self.click_button('(//div[@class="d-flex m-b-7 toolBar"]//button)[2]')
        if name == "":
            self.click_button(
                f'//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="{button}"]')
            message = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="el-message el-message--error"]//p')
                )
            )
            return message.text
        else:
            self.enter_texts('//div[text()=" 名称 "]/following-sibling::div//input', name)
            self.click_button(
                f'//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="{button}"]')
            self.click_template()
            eles = self.finds_elements(By.XPATH,
                                       f'//div[@class="flex-column flex-align-items-center overflow-auto b-r-s-dcdee2 flex-1"]//div[@class="flex-j-c-between"]/span[1][text()=" {name} "]')
            return len(eles)

    def clear_all_button(self, span_text):
        """点击清除所有按钮."""
        self.wait_for_loading_to_disappear()
        self.click_button('(//div[@class="d-flex m-b-7 toolBar"]//button)[3]')
        self.click_button(
            f'//div[./div[text()="确定要删除所有的组件吗？"]]/following-sibling::div//span[text()="{span_text}"]')

    def clear_button(self, span_text):
        """点击清除按钮."""
        self.click_button('(//div[@class="d-flex m-b-7 toolBar"]//button)[4]')
        self.click_button(f'//div[./div[text()="你确定要删除这个组件吗"]]/following-sibling::div//span[text()="{span_text}"]')

    def count_div_elements(self):
        """
        返回 id 为 homeCanvasBox 的容器下的直接子 div 元素个数（排除后两个元素）。

        注意：减2是由于后两个子元素为布局占位符，非实际内容项。
        """
        try:
            eles = self.finds_elements(By.XPATH, '//div[@id="homeCanvasBox"]/div')
            count = (len(eles) - 2)
            return count
        except Exception as e:
            # 可根据实际日志系统记录错误
            print(f"元素查找或处理失败: {e}")

    def delete_template(self, name=""):
        """
        删除指定名称的模板

        参数:
            name (str): 要删除的模板名称，默认为空字符串

        返回值:
            int: 删除操作后仍存在的同名模板数量，正常情况下应为0
        """
        self.click_template()
        self.wait_for_loading_to_disappear()

        # 1️⃣ 悬停模版容器触发图标显示
        container = self.get_find_element_xpath(
            f'//span[text()=" {name} "]/ancestor::div[2]'
        )
        ActionChains(self.driver).move_to_element(container).perform()

        # 2️⃣ 等待删除图标可见
        delete_icon = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//span[text()=" {name} "]/ancestor::div[2]//i[contains(@class, "el-icon-delete-solid")]'
            ))
        )

        # 3️⃣ 点击删除图标并确认删除操作
        delete_icon.click()
        self.click_button('(//div[@class="ivu-modal-confirm-footer"])[2]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()
        self.click_save_button()
        self.wait_for_loading_to_disappear()
        self.get_find_message()
        self.right_refresh()
        self.click_template()
        # 检查删除后的模板数量并返回
        ele = self.driver.find_elements(By.XPATH, f'//div[./span[text()=" {name} "]]')
        return len(ele)

    def drag_component(self, name="", index=""):
        """
        拖拽组件到画布区域。

        参数:
            name (str): 组件名称，如果指定该参数，则只拖拽对应名称的组件。
            index (str or int): 指定拖拽组件的数量。可以是数字字符串或整数，
                                表示从组件列表中按顺序拖拽前 index 个组件。

        返回:
            int: 成功拖拽的组件总数。若指定了 name，则返回 1；
                 否则返回第一组和第二组组件数量之和。
        """

        input_element = self.get_find_element_xpath('//div[@id="homeCanvasBox"]')
        canvas_size = input_element.size
        max_x = int(canvas_size['width'] * 0.25) - 10  # 考虑 zoom 后的大小

        offset_step = 30
        current_offset_x = 5
        current_offset_y = 5

        # 情况一：指定名称拖一个组件
        if name:
            sleep(1)
            text_element = self.get_find_element_xpath(
                f'(//div[@class="menuList"])[1]/div[.//span[text()="{name}"]]'
            )
            ActionChains(self.driver).drag_and_drop(text_element, input_element).perform()
            return 1

        # 情况二和三：准备组件 XPath 列表
        index1 = len(self.finds_elements(By.XPATH, '(//div[@class="menuList"])[1]/div'))
        index2 = len(self.finds_elements(By.XPATH, '(//div[@class="menuList"])[2]/div'))
        xpath_list = [
            f'(//div[@class="menuList"])[{group}]/div[{i}]'
            for group, count in [(1, index1), (2, index2)]
            for i in range(1, count + 1)
        ]

        # 情况二：如果传入数字 index，只拖对应数量的组件
        if isinstance(index, int) or (isinstance(index, str) and index.isdigit()):
            count_limit = int(index)
            xpath_list = xpath_list[:count_limit]

        col = 0
        row = 0

        # 遍历组件列表并依次拖拽到画布上，按行列排列
        for xpath in xpath_list:
            text_element = self.get_find_element_xpath(xpath)
            offset_x = current_offset_x + (col * offset_step)
            offset_y = current_offset_y + (row * offset_step)

            # 防止越界
            if offset_x > max_x:
                col = 0
                row += 1
                offset_x = current_offset_x
                offset_y = current_offset_y + (row * offset_step)

            ActionChains(self.driver) \
                .click_and_hold(text_element) \
                .move_to_element_with_offset(input_element, offset_x, offset_y) \
                .release() \
                .perform()
            col += 1

        return index1 + index2

