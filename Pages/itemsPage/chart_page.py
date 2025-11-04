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
        self.click_button('//a[@title="添加"]')

    def get_find_element_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

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
            lambda d: (
                d.find_element(By.CLASS_NAME, "el-loading-mask").value_of_css_property("display") == "none"
                if d.find_elements(By.CLASS_NAME, "el-loading-mask") else True
            )
        )
        sleep(1)

    def clicl_confirm_button(self):
        """点击确认按钮."""
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[3]')
        self.wait_for_loading_to_disappear()
