from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class FunctionPage(BasePage):
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

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def go_navigation(self, name1="", name2="", name3=""):
        """前往导航栏"""
        self.click_button('(//span[text()="计划管理"])[1]')  # 点击计划管理
        self.click_button('(//span[text()="计划基础数据"])[1]')  # 点击计划基础数据
        if name1 != '':
            self.click_button(f'(//span[text()="{name1}"])[1]')
            sleep(1)
        if name2 != '':
            self.click_button(f'(//span[text()="{name2}"])[1]')
            sleep(1)
        if name3 != '':
            self.click_button(f'(//span[text()="{name3}"])[1]')
            sleep(1)

    def get_find_message(self):
        """获取错误信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--success"]/p')
            )
        )
        return message.text