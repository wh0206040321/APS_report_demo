from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages


class UserRolePage(BasePage):
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
        message = WebDriverWait(self.driver, 60).until(
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

    def right_refresh(self, name="用户权限管理"):
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

    def wait_for_el_loading_mask(self, timeout=60):
        sleep(2)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )

    def wait_for_loadingbox(self, timeout=30):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="loadingbox"]')
            )
        )

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def add_user(self, name, password, role):
        """添加用户权限管理."""
        add = AddsPages(self.driver)
        self.click_all_button("新增")
        xpath_value_map = {
            '//div[label[text()="用户代码"]]//input': name,
            '//div[label[text()="用户名称"]]//input': name,
            '//div[label[text()="密码"]]//input': password,
            '//div[label[text()="确认密码"]]//input': password,
        }
        sleep(0.5)
        add.batch_modify_inputs(xpath_value_map)
        self.click_button('//div[label[text()="用户有效日期"]]//input')
        self.click_button(
            '//div[@class="ivu-date-picker-cells"]/span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"]/following-sibling::span')
        self.enter_texts('//div[div[p[text()="角色代码"]]]//input', role)
        sleep(1)
        self.click_button('(//table[@class="vxe-table--body"]//tr[1]/td[2]/div/span)[2]')

    def update_user(self, before_name, after_name):
        """修改用户管理."""
        add = AddsPages(self.driver)
        self.select_input(before_name)
        sleep(0.5)
        self.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{before_name}"]')
        sleep(1)
        self.click_all_button("编辑")
        xpath_value_map = {
            '//div[label[text()="用户名称"]]//input': after_name,
        }
        sleep(0.5)
        add.batch_modify_inputs(xpath_value_map)

    def select_input(self, name):
        """选择输入框."""
        ele = self.get_find_element_xpath('//div[div[p[text()="用户代码"]]]//input')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        self.enter_texts('//div[div[p[text()="用户代码"]]]//input', name)
        sleep(1)

    def click_sel_button(self):
        """点击查询按钮."""
        self.click(By.XPATH, '//p[text()="查询"]')

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

    def get_verify_text(self, text):
        """获取输入框错误提示"""
        verify = self.get_find_element_xpath(
            f'//div[label[text()="{text}"]]//div[@class="ivu-form-item-error-tip"]')
        return verify.text

    def del_(self, value=[]):
        """删除"""
        for index, v in enumerate(value, start=1):
            try:
                xpath = '//p[text()="用户代码"]/ancestor::div[2]//input'
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
                self.enter_texts(xpath, v)
                self.click_button(f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
                self.click_all_button("删除")  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                self.get_find_message()
            except NoSuchElementException:
                print(f"未找到元素: {v}")
            except Exception as e:
                print(f"操作 {v} 时出错: {str(e)}")