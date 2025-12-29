from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Pages.base_page import BasePage


class SchedPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def click_add_schedbutton(self):
        """点击添加方案按钮."""
        self.click_button('//span[text()="新增方案"]')
        sleep(1)

    def click_del_schedbutton(self):
        """点击删除方案按钮."""
        self.click_button('//span[text()="删除方案"]')

    def click_add_commandbutton(self):
        """点击添加命令按钮."""
        self.click_button('//i[@class="ivu-icon ivu-icon-md-add"]')

    def click_del_commandbutton(self):
        """点击删除命令按钮."""
        self.click_button('//i[@class="ivu-icon ivu-icon-md-close"]')

    def click_up_commandbutton(self):
        """点击向上移动命令按钮."""
        self.click_button('//i[@class="ivu-icon ivu-icon-md-arrow-up"]')

    def click_down_commandbutton(self):
        """点击向下移动命令按钮."""
        self.click_button('//i[@class="ivu-icon ivu-icon-md-arrow-down"]')

    def click_attribute_button(self):
        """点击属性设置按钮."""
        sleep(1)
        self.click_button('//span[text()="属性设置"]')

    def click_sched_button(self):
        """点击均衡排产按钮."""
        self.click_button('//div[text()=" 分派属性 "]')

    def click_time_sched(self):
        """点击时间属性"""
        self.click_button('//div[text()=" 时间属性 "]')

    def click_name_ok(self):
        """点击确定按钮."""
        sleep(1)
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)

    def click_ok_schedbutton(self):
        """点击确定按钮."""
        sleep(1)
        self.click_button('//div[@class="ivu-modal-confirm"]//span[text()="确定"]')
        sleep(1)

    def click_ok_button(self):
        """点击确定按钮."""
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[3]')

    def click_save_button(self):
        """点击保存按钮."""
        self.click_button('//button[./span[text()="保存设置"]]')
        self.get_find_message()
        sleep(1)

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

    def get_find_elements_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        self.finds_elements(By.XPATH, xpath)

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def right_refresh(self, name):
        """右键刷新."""
        self.click_button('(//div[@class="vxe-modal--footer"]//span[text()="取消"])[1]')
        sleep(0.5)
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_el_loading_mask()
        sleep(1)

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

    def wait_for_el_loading_mask(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def get_after_value(self, name):
        """获取保存之后的值"""
        self.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[1]')
        self.click_save_button()
        self.driver.refresh()
        sleep(1)
        self.click_button(f'//ul[@visible="visible"]//ul//span[text()="{name}"]')
        self.click_attribute_button()

    def add_copy_sched(self, name=[]):
        """添加复制方案"""
        for v in name:
            self.click_add_schedbutton()
            self.enter_texts('//label[text()="名称"]/following-sibling::div//input', v)
            self.click_button(
                '//label[text()="选择复制的方案"]/following-sibling::div/div'
            )  # 点击下拉框
            self.click_button('//li[text()="排产方案(订单级)"]')
            self.click_name_ok()  # 点击确定
            self.click_save_button()  # 点击保存

    def add_copy_materialsched(self, name=[]):
        """添加复制方案"""
        ele = self.get_find_element_xpath(
            '//div[@class="h-69 background-ffffff"]//label[1]'
        ).text
        for v in name:
            self.click_add_schedbutton()
            self.enter_texts('//label[text()="名称"]/following-sibling::div//input', v)
            self.click_button(
                '//label[text()="选择复制的方案"]/following-sibling::div/div'
            )  # 点击下拉框
            self.click_button(f'//li[text()="{ele}"]')
            self.click_name_ok()  # 点击确定
            self.click_save_button()  # 点击保存

    def del_all_sched(self, name=[]):
        """删除所有方案"""
        for v in name:
            self.click_button(f'//label[text()="{v}"]')
            self.click_del_schedbutton()  # 点击删除
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            # 点击保存
            self.click_save_button()

    def batch_sched_dialog_box(self, xpath_list=[], new_value=""):
        """选择对话框选择表格"""
        for index, xpath in enumerate(xpath_list, start=1):
            try:
                self.click_button(xpath)
                sleep(3)
                ele = self.get_find_element_xpath(f'(//table[@class="vxe-table--body"]//tr[1]/td[2]/div/span)[1]').get_attribute('class')
                if 'is--checked'not in ele:
                    self.click_button(f'(//table[@class="vxe-table--body"]//tr[1]/td[2]/div/span)[1]')
                self.click_button(f'(//button[@class="ivu-btn ivu-btn-primary"])[3]')
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")
