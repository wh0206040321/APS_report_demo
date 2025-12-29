# pages/login_page.py
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class PersonalPage(BasePage):
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
        self.click_button('//input[@placeholder="请选择计划单元"]')
        self.click_button(f'//li[text()="{planning_unit}"]')

    def click_login_button(self):
        self.click_button('//button[contains(@class, "ivu-btn-primary")]')

    def get_find_element(self, xpath):
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

    def edit_password(self, old_password, new_password, confirm_password):
        """
        修改用户密码。

        该方法通过模拟用户交互来修改密码，确保密码变更过程的安全性和准确性。

        参数:
        - old_password (str): 用户的当前密码。
        - new_password (str): 用户想要设置的新密码。
        - confirm_password (str): 新密码的再次确认，以防止输入错误。

        此方法无返回值。
        """
        # 打开密码修改界面
        self.click_button('//div[@class="flex-alignItems-center"]')
        self.click_button('//div[text()=" 修改密码 "]')

        # 输入原密码和新密码及其确认
        self.enter_text(By.XPATH, '//input[@placeholder="原密码"]', old_password)
        self.enter_text(By.XPATH, '//input[@placeholder="新密码"]', new_password)
        self.enter_text(By.XPATH, '//input[@placeholder="确认密码"]', confirm_password)

        # 确认密码修改
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

    def wait_for_el_loading_mask(self, timeout=10):
        sleep(1)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )

    def go_setting_page(self):
        """
        进入个人设置页面。

        该方法通过模拟用户点击操作，导航到个人设置页面。首先点击的是包含灵活对齐中心的div，
        接着点击文本为"个人设置"的div，以确保用户到达正确的设置页面。
        """

        # 点击灵活对齐中心的div，通常是导航或菜单项。
        self.click_button('//div[@class="flex-alignItems-center"]')

        # 点击文本为"个人设置"的div，进入个人设置页面。
        self.click_button('//i[@class="el-icon-setting"]')
        self.wait_for_el_loading_mask()

    def switch_language(self, language):
        """
        切换系统语言。
        参数:
        - language (str): 要设置的系统语言。

        返回:
        - str: 切换语言后页面上的某个特定元素的文本，用于确认语言切换是否成功。
        """
        # 打开个人设置菜单
        self.go_setting_page()

        # 点击系统语言设置图标，准备选择新的语言
        self.click_button('//div[@class="ivu-tabs-tabpane"]/div[.//li[text()="简体中文"]]/div')

        # 选择目标语言
        self.click_button(f'//li[text()="{language}"]')

        # 确认
        self.click_button('//div[@class="demo-drawer-footer"]/button[2]')
        sleep(3)
        # 获取并返回特定元素的文本，用于验证语言是否已成功切换
        ele = self.get_find_element('//div[@class="vxe-pulldown--content"]//input').get_attribute("placeholder")
        return ele

    def go_engine_page(self, name=''):
        """
        根据不同的名称参数，进入不同的引擎页面配置，并进行相应的设置。

        参数:
        - name: 指定需要配置的引擎页面类型，支持 'web', 'ip', 'system_webip', 'system_ip', 'system_web'。

        步骤:
        1. 点击系统管理、单元设置、环境设置，进入环境配置页面。
        2. 根据传入的name参数，选择相应的服务器类型和配置。
        3. 保存配置。
        4. 依次点击计划运行、计算工作台、计划计算，进入计划计算页面。
        """
        self.click_button('(//span[text()="系统管理"])[1]')  # 点击系统管理
        self.click_button('(//span[text()="单元设置"])[1]')  # 点击单元设置
        self.click_button('(//span[text()="环境设置"])[1]')  # 点击环境设置
        sleep(2)
        radio = self.get_find_element('//label[text()=" 服务器"]/span')
        sleep(1)
        if name == 'web' or name == 'ip':
            # 选择服务器类型并保存
            if 'ivu-radio-checked' in radio.get_attribute('class'):
                sleep(1)
                self.click_button('//label[text()=" 本地"]/span')
                sleep(1)
            self.click_button('//p[text()="保存"]')
        elif name == 'system_webip':
            # 选择本地并设置web服务，然后保存
            if radio.get_attribute('class') != 'ivu-radio':
                sleep(2)
                self.click_button('//label[text()=" 本地"]/span')
            self.click_button('//input[@placeholder="请选择"]')
            self.click_button('//span[text()="web服务"]')
            self.click_button('//p[text()="保存"]')
        elif name == 'system_ip':
            # 选择本地并设置IP，然后保存
            if radio.get_attribute('class') != 'ivu-radio':
                sleep(2)
                self.click_button('//label[text()=" 本地"]/span')
            self.click_button('//input[@placeholder="请选择"]')
            self.click_button('//span[text()="IP"]')
            self.click_button('//p[text()="保存"]')
        elif name == 'system_web':
            # 直接保存当前配置，适用于web服务配置
            if radio.get_attribute('class') == 'ivu-radio':
                sleep(2)
                radio.click()
            self.click_button('//p[text()="保存"]')
        self.get_find_message()
        # 进入计划计算页面
        self.click_button('(//span[text()="计划运行"])[1]')  # 点击计划运行
        self.click_button('(//span[text()="计算工作台"])[1]')  # 点击计算工作台
        self.click_button('(//span[text()="计划计算"])[1]')  # 点击计划计算
        sleep(3)

    def go_exit(self, num=""):
        """
        设置自动退出时间。

        如果提供了num参数，則會到個人設置菜單設置自動退出時間。

        参数:
        num (str): 自动退出前等待的时间（秒）。如果未提供，则不进行设置。
        """
        if num:
            # 打开个人设置菜单
            self.go_setting_page()
            # 找到并操作自动退出时间的输入框
            input_ = self.get_find_element('//div[./p[text()=" 不操作自动退出(秒): "]]//input')
            # 清空输入框
            input_.send_keys(Keys.CONTROL, "a")
            input_.send_keys(Keys.DELETE)
            # 输入新的自动退出时间
            input_.send_keys(num)
            # 点击确定按钮保存设置
            self.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
            self.get_find_message()

    def go_characters_display(self, name=""):
        # 打开个人设置菜单
        self.go_setting_page()
        radio = self.get_find_element('//label[text()="悬浮"]/span')
        if radio.get_attribute('class') == "ivu-radio":
            self.click_button('//label[text()="悬浮"]')
        display = self.get_find_element(f'//div[./p[text()=" 组件菜单文字: "]]/div/label[text()="{name}"]/span')
        if name == "显示":
            if display.get_attribute('class') == "ivu-radio":
                self.click_button(f'//div[./p[text()=" 组件菜单文字: "]]/div/label[text()="{name}"]')
        else:
            if display.get_attribute('class') != "ivu-radio-input":
                self.click_button(f'//div[./p[text()=" 组件菜单文字: "]]/div/label[text()="{name}"]')
        # 点击确定按钮保存设置
        self.click_button('//div[@class="demo-drawer-footer"]//span[text()="确定"]')
        self.get_find_message()
        sleep(3)
        style = self.get_find_element('//div[@class="menuTitle"]').get_attribute("style")
        return style