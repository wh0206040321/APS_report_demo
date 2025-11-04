from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from Pages.base_page import BasePage


class SchedPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def click_add_schedbutton(self):
        """点击添加方案按钮."""
        self.click(By.XPATH, '//span[text()="新增方案"]')

    def click_del_schedbutton(self):
        """点击删除方案按钮."""
        self.click(By.XPATH, '//span[text()="删除方案"]')

    def click_add_commandbutton(self):
        """点击添加命令按钮."""
        self.click(By.XPATH, '//i[@class="ivu-icon ivu-icon-md-add"]')

    def click_del_commandbutton(self):
        """点击删除命令按钮."""
        self.click(By.XPATH, '//i[@class="ivu-icon ivu-icon-md-close"]')

    def click_up_commandbutton(self):
        """点击向上移动命令按钮."""
        self.click(By.XPATH, '//i[@class="ivu-icon ivu-icon-md-arrow-up"]')

    def click_down_commandbutton(self):
        """点击向下移动命令按钮."""
        self.click(By.XPATH, '//i[@class="ivu-icon ivu-icon-md-arrow-down"]')

    def click_attribute_button(self):
        """点击属性设置按钮."""
        self.click(By.XPATH, '//span[text()="属性设置"]')

    def click_sched_button(self):
        """点击均衡排产按钮."""
        self.click(By.XPATH, '//div[text()=" 分派属性 "]')

    def click_time_sched(self):
        """点击时间属性"""
        self.click(By.XPATH, '//div[text()=" 时间属性 "]')

    def click_ok_schedbutton(self):
        """点击确定按钮."""
        self.click(By.XPATH, '(//button[@class="ivu-btn ivu-btn-primary"])[2]')

    def click_ok_button(self):
        """点击确定按钮."""
        self.click(By.XPATH, '(//button[@class="ivu-btn ivu-btn-primary"])[3]')

    def click_save_button(self):
        """点击保存按钮."""
        self.click(By.XPATH, '//button[./span[text()="保存设置"]]')

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

    def get_error_message(self, xpath):
        """获取错误消息元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def get_find_message(self):
        """获取错误信息"""
        message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="ivu-message"]//span')
            )
        )
        return message

    def set_input_value(self, xpath, value):
        input_element = self.find_element_by_xpath(xpath)
        input_element.clear()  # 清空input元素的内容
        input_element.send_keys(value)  # 设置input元素的新值

    def get_after_value(self, name):
        """获取保存之后的值"""
        self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"]//span[text()="确定"])[1]')
        self.click_save_button()
        sleep(1)
        self.driver.refresh()
        sleep(1)
        self.click_button(f'//ul[@visible="visible"]//ul//span[text()="{name}"]')
        self.click_attribute_button()

    def batch_modify_input_number(self, xpath_list=[], value_list=[]):
        for index, xpath in enumerate(xpath_list, 1):
            try:
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.BACK_SPACE)
                sleep(1)
                self.enter_texts(xpath, value_list[index-1]
                )

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )

    def batch_modify_input(self, xpath_list=[], new_value=""):
        """批量修改输入框"""
        for xpath in xpath_list:
            try:
                self.enter_texts(xpath, new_value)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_acquisition_input(self, xpath_list=[], val_list=[]):
        """批量获取输入框"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                # 显式等待元素可见（最多等待10秒）
                element = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(("xpath", xpath))
                )

                # 获取输入框的值
                value = element.get_attribute("value")
                print("value", value)
                print("index", index-1)
                if value == val_list[index-1]:
                    values.append(value)

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )

        return values

    def batch_acquisition_text(self, xpath_list=[], val_list=[]):
        """批量获取文本"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                # 显式等待元素可见（最多等待10秒）
                value = self.get_find_element_xpath(xpath).text
                # 获取输入框的值
                print("text", value)
                print("index", index-1)
                if value == val_list[index-1]:
                    values.append(value)

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )

        return values

    def expression_click(self, xpath_list):
        for index, xpath in enumerate(xpath_list, 1):
            try:
                # 显式等待元素可见（最多等待10秒）
                # element = WebDriverWait(self.driver, 10).until(
                #     EC.visibility_of_element_located(("xpath", xpath))
                # )
                self.click_button(xpath)
                element = self.get_find_element_xpath('//tr[./td[2][.//span[text()="Abs"]]]/td[2]')
                actions = ActionChains(self.driver)
                # 双击命令
                actions.double_click(element).perform()
                self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
                sleep(1)
            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )

    def batch_selection_dropdown(self, xpath_list, value_list):
        """批量选择下拉"""
        for index, xpath in enumerate(xpath_list, 1):
            try:
                # 显式等待元素可见（最多等待10秒）
                # element = WebDriverWait(self.driver, 10).until(
                #     EC.visibility_of_element_located(("xpath", xpath))
                # )
                self.click_button(xpath)
                text_str = value_list[index - 1]
                print("text_str", text_str)
                sleep(1)
                # self.click_button('//div[contains(text(),"方案是否循环执行")]/following-sibling::div//li[contains(text(),"是")]')
                self.click_button(f'{xpath}//li[contains(text(),"{text_str}")]')
                # 获取输入框的值
                # value = element.get_attribute("value")
                # if value == val_list[index - 1]:
                #     values.append(value)

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )

