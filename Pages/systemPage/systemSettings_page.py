from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Utils.data_driven import DateDriver


class SystemSettingsPage(BasePage):
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

    def get_message(self):
        """获取信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--success"]/p')
            )
        )
        return message.text

    def right_refresh(self, name="系统表示设置"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_el_loading_mask()

    # 等待加载遮罩消失
    def wait_for_el_loading_mask(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def log_out (self, timeout=10):
        """退出登录"""
        self.click_button('//div[@class="flex-alignItems-center"]')
        self.click_button('//ul/li/div[text()=" 注销 "]')
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="loadingbox"]')
            )
        )

    def click_save_button(self):
        """点击保存按钮."""
        sleep(0.5)
        self.click_button(' //button[span[text()="保存"]]')

    def upload_file(self, file_path, num):
        if num == 1:
            upload_input = self.get_find_element_xpath('(//input[@type="file"])[1]')
            upload_input.send_keys(file_path)
        else:
            upload_input = self.get_find_element_xpath('(//input[@type="file"])[2]')
            upload_input.send_keys(file_path)

    def del_icon(self, name):
        # 1️⃣ 悬停模版容器触发图标显示
        container = self.get_find_element_xpath(
            f'//div[p[text()=" {name}: "]]//div[@class="demo-upload-list"]'
        )
        ActionChains(self.driver).move_to_element(container).perform()

        # 2️⃣ 等待删除图标可见
        delete_icon = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//i[@class="ivu-icon ivu-icon-ios-trash-outline"]'
            ))
        )

        # 3️⃣ 点击删除图标并确认删除操作
        delete_icon.click()
        self.click_button('(//div[@class="ivu-modal-confirm-footer"])[1]//span[text()="确定"]')
        self.wait_for_el_loading_mask()
