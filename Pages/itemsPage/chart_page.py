from time import sleep

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from Pages.base_page import BasePage


class ChartPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def enter_texts(self, xpath, text):
        """输入文字."""
        self.enter_text(By.XPATH, xpath, text)

    def click_button(self, xpath):
        """点击按钮."""
        self.click(By.XPATH, xpath)

    def click_add_button(self):
        """点击添加按钮."""
        self.wait_for_el_loading_mask()
        self.click_button('//a[@title="添加"]')

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

    def wait_for_el_loading_mask(self, timeout=30):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        sleep(2)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def click_resource_confirm_button(self):
        """点击确认按钮."""
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[3]')
        self.wait_for_el_loading_mask()

    def click_order_confirm_button(self):
        """点击确认按钮."""
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[2]')
        self.wait_for_el_loading_mask()

    def click_close_page(self, before_name, name):
        """点击关闭页面."""
        self.click_button(f'//div[text()=" {before_name} "]')
        self.click_button(f'//div[div[text()=" {before_name} "]]/span')
        self.click_button(f'(//span[text()="{name }"])[1]')
        self.wait_for_el_loading_mask()
        sleep(2)
