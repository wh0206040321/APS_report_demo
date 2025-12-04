from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class ImpPage(BasePage):
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

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def click_confirm(self):
        """点击确定"""
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

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

    def select_input(self, name):
        """选择输入框."""
        xpath = '//div[p[text()="接口名称"]]/following-sibling::div//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL + "a")
        ele.send_keys(Keys.DELETE)
        self.enter_texts('//div[p[text()="接口名称"]]/following-sibling::div//input', name)

    def right_refresh(self, name="导入设置"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    # 等待加载遮罩消失
    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )
        sleep(1)

    def click_impall_button(self, name):
        """点击导入页面各种按钮"""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def hover(self, name=""):
        # 悬停模版容器触发图标显示
        container = self.get_find_element_xpath(
            f'//span[@class="position-absolute font12 right10"]'
        )
        ActionChains(self.driver).move_to_element(container).perform()

        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//ul/li[contains(text(),"{name}")]'
            ))
        )

        # 3️⃣ 再点击图标
        delete_icon.click()

    def del_all(self, value=[]):
        """批量删除"""
        for v in value:
            self.click_button('//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//input[@class="ivu-select-input"]')
            self.click_button(f'(//li[text()="{v}"])[1]')
            self.click_impall_button("删除")
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            self.get_find_message()

        self.click_impall_button("保存")

    def add_imp(self, name):
        """添加导入方案"""
        self.click_impall_button("新增")
        self.enter_texts('//div[label[text()="名称"]]//input', name)
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

    def copy_(self, name='', copy_name=''):
        """复制导入方案"""
        self.click_impall_button("复制")
        if name != '':
            self.click_button('//div[label[text()="源方案"]]//input[@type="text"]')
            self.click_button(f'(//ul/li[text()="{name}"])[2]')
        if copy_name != '':
            self.enter_texts('//div[label[text()="目的方案"]]//input[@type="text"]', copy_name)
        self.click_button('(//div[@class="ivu-modal-footer"]//span[text()="确定"])[2]')

    def mover_right(self):
        """右移"""
        element = self.get_find_element_xpath('(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]')
        # 滚动到最右边
        self.driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", element)
        sleep(1)
