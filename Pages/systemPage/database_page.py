from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages


class DateBasePage(BasePage):
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

    def right_refresh(self, name="数据库维护"):
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
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[1]")
            )
        )
        sleep(1)

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def select_input_database(self, field_name, name):
        """选择输入框."""
        xpath = f'//div[div[p[text()="{field_name}"]]]//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        sleep(0.5)
        self.enter_texts(xpath, name)
        sleep(0.5)

    def click_synchronize_button(self, name):
        """点击同步按钮."""
        if name == "同步单表":
            self.click_all_button(name)
            self.click_button('//div[p[text()="表名："]]//i[contains(@class,"ivu-icon")]')
            self.click_button('//li[text()="APS_Item"]')
            self.click_confirm()
        if name == "同步所有":
            self.click_all_button(name)
            self.click_button('//div[@class="el-message-box__btns"]//span[contains(text(),"确定")]')

    def loop_judgment(self, xpath):
        """循环判断"""
        eles = self.finds_elements(By.XPATH, xpath)
        code = [ele.text for ele in eles]
        return code

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

    def click_confirm(self):
        """点击确定"""
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

    def click_field_button(self, name):
        """点击字段按钮"""
        self.click_button(f'//button/span[text()="{name}"]')

    def click_select_button(self):
        """点击查询按钮"""
        self.click_button('//div[text()=" 查询 "]')

    def add_table_code(self, button_name='', code='', field_code='', fieldbutton_name=''):
        """添加表"""
        add = AddsPages(self.driver)
        xpath_list = [
            '//div[label[text()="字段代码"]]//input',
            '//div[label[text()="字段名称"]]//input',
            '//div[label[text()="类型"]]//i',
            '//li[text()="字符"]',
            '//div[label[text()="长度"]]//input',
        ]
        if button_name == '新增':
            self.click_all_button("新增")
            self.enter_texts('//div[label[text()="表代码"]]//input', code)
        if button_name == '编辑':
            self.select_input_database("表代码", code)
            sleep(2)
            self.click_button(f'(//table[@class="vxe-table--body"])[1]//tr[1]/td[2]//span[text()="{code}"]')
            self.click_all_button("编辑")
        sleep(2)

        if fieldbutton_name == '添加':
            self.click_field_button(fieldbutton_name)
            add.batch_modify_input(xpath_list[:2], field_code)
            self.click_button(xpath_list[2])
            self.click_button(xpath_list[3])
            self.enter_texts(xpath_list[4], '100')
            self.click_confirm()
            sleep(1)
            self.click_all_button("保存")
        if fieldbutton_name == '编辑':
            self.select_input_database("字段代码", field_code)
            sleep(1)
            self.click_button(f'(//table[@class="vxe-table--body"])[3]//tr[1]/td[2]//span[text()="{field_code}"]')
            self.click_field_button(fieldbutton_name)
        if fieldbutton_name == '删除':
            self.select_input_database("字段代码", field_code)
            sleep(1)
            self.click_button(f'(//table[@class="vxe-table--body"])[3]//tr[1]/td[2]//span[text()="{field_code}"]')
            self.click_field_button(fieldbutton_name)
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            sleep(1)
            self.click_all_button("保存")
