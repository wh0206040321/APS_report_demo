# pages/login_page.py
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def enter_username(self, username):
        """输入用户名."""
        self.enter_text(By.XPATH, '//input[@placeholder="请输入账户"]', username)

    def enter_password(self, password):
        """输入密码."""
        self.enter_text(By.XPATH, '//input[@placeholder="请输入密码"]', password)

    def click_button(self, xpath):
        """点击按钮."""
        self.click(By.XPATH, xpath)

    def select_planning_unit(self, planning_unit):
        self.click_button('//div[@class="ivu-select-head-flex"]/input')
        self.click_button(f'//li[text()="{planning_unit}"]')

    def login(self, username, password, planning_unit, timeout=60):
        """完整的登录流程"""
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="loadingbox"]')
            )
        )
        self.enter_username(username)
        self.enter_password(password)
        self.select_planning_unit(planning_unit)
        sleep(0.2)
        self.click_login_button()
        sleep(1)

    def wait_for_loadingbox(self, timeout=30):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="loadingbox"]')
            )
        )

    def click_login_button(self):
        self.click_button('//button[contains(@class, "ivu-btn-primary")]')

    def get_find_element(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def get_error_message(self, xpath):
        """获取错误消息元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def wait_for_el_loading_mask(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)
