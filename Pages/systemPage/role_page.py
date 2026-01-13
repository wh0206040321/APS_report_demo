from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages
from selenium.webdriver import Keys

class RolePage(BasePage):
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
        message = WebDriverWait(self.driver, 100).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--success"]/p')
            )
        )
        return message.text

    def get_error_message(self):
        """获取错误信息"""
        message = WebDriverWait(self.driver, 100).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="el-message el-message--error"]/p')
            )
        )
        return message.text

    def right_refresh(self, name="角色管理"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_el_loading_mask()

    # 等待加载遮罩消失
    def wait_for_el_loading_mask(self, timeout=60):
        sleep(1)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def wait_for_loading_to_disappear(self, timeout=30):
        sleep(1)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[1]")
            )
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

    def add_role(self, name, module):
        """添加角色管理."""
        add = AddsPages(self.driver)
        self.click_all_button("新增")
        list_ = [
            '//div[label[text()="角色代码"]]//input',
            '//div[label[text()="角色名称"]]//input',
        ]
        add.batch_modify_input(list_, name)

        list_sel = [
            {"select": '//div[label[text()="计划单元名称"]]//div[@class="ivu-select-selection"]',
             "value": f'//div[label[text()="计划单元名称"]]//li[text()="{module}"]'},
        ]
        add.batch_modify_select_input(list_sel)

    def update_role(self, before_name, after_name, module):
        """修改角色管理."""
        add = AddsPages(self.driver)
        self.select_input(before_name)
        sleep(2)
        self.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{before_name}"]')
        self.click_all_button("编辑")
        sleep(1)
        list_ = [
            '//div[label[text()="角色名称"]]//input',
        ]
        add.batch_modify_input(list_, after_name)
        sleep(1)
        list_sel = [
            {"select": '//div[label[text()="计划单元名称"]]//div[@class="ivu-select-selection"]',
             "value": f'//ul[@class="ivu-select-dropdown-list"]/li[text()="{module}"]'},
        ]
        add.batch_modify_select_input(list_sel)

    def select_input(self, name):
        """选择输入框."""
        xpath = '//div[div[p[text()="角色代码"]]]//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL + "a")
        ele.send_keys(Keys.DELETE)
        self.enter_texts('//div[div[p[text()="角色代码"]]]//input', name)
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

    def del_all(self, value=[], xpath=''):
        for index, v in enumerate(value, start=1):
            try:
                self.enter_texts(xpath, v)
                sleep(0.5)
                self.click_button(f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
                self.click_all_button("删除")  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                self.wait_for_el_loading_mask()
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
            except NoSuchElementException:
                print(f"未找到元素: {v}")
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
            except Exception as e:
                print(f"操作 {v} 时出错: {str(e)}")
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
