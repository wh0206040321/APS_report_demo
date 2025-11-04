from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class EnvironmentPage(BasePage):
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

    def click_save_button(self):
        """点击保存按钮"""
        self.click_button('//p[text()="保存"]')

    def click_cycle(self):
        """点击周期"""
        self.click_button('//div[text()=" 周期 "]')

    def click_plan(self):
        """点击排程"""
        self.click_button('//div[text()=" 排程 "]')

    def click_trademark(self):
        """点击排程"""
        self.click_button('//div[text()=" 标识 "]')

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

    def right_refresh(self, name="环境设置"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    def wait_for_loading_to_disappear(self, timeout=10):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[contains(@class, "el-loading-mask") and not(contains(@style, "display: none"))]')
            )
        )
        sleep(1)

    def update_checkbox(self, xpath_list=[], new_value: bool = True):
        """
        改变复选框状态

        参数:
            xpath_list (list): 包含复选框元素XPath路径的列表，默认为空列表
            new_value (str): 目标状态值，"true"表示选中，"false"表示取消选中，默认为空字符串

        返回值:
            无返回值
        """
        # 遍历XPath列表，逐个处理复选框元素
        for index, xpath in enumerate(xpath_list, start=1):
            sleep(0.5)
            try:
                # 获取复选框元素
                checkbox = self.get_find_element_xpath(xpath)
                modified_xpath = xpath.replace("//input", "/label/span")
                # 根据目标状态值处理复选框选中状态
                if new_value:
                    # 如果目标状态为选中且当前未选中，则点击复选框
                    if not checkbox.is_selected():
                        self.click_button(modified_xpath)
                        sleep(0.5)
                elif not new_value:
                    # 如果目标状态为未选中且当前已选中，则点击复选框
                    if checkbox.is_selected():
                        self.click_button(modified_xpath)
                        sleep(0.5)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_modify_input(self, xpath_list=[], new_value=""):
        """批量修改输入框"""
        for xpath in xpath_list:
            try:
                ele = self.get_find_element_xpath(xpath)
                ele.send_keys(Keys.CONTROL, 'a')
                ele.send_keys(Keys.DELETE)
                self.enter_texts(xpath, new_value)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_modify_inputs(self, xpath_value_map: dict):
        """通过字典批量修改输入框（键为XPath，值为输入内容）"""
        for xpath, value in xpath_value_map.items():
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.DELETE)
            element.send_keys(value)

    def batch_acquisition_input(self, xpath_list=[], text_value=""):
        """批量获取输入框"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                value = self.get_find_element_xpath(xpath).get_attribute("value")
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

    def get_border_color(self, xpath_list=[], text_value=""):
        """获取边框颜色"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                value = self.get_find_element_xpath(xpath).value_of_css_property("border-color")
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

    def batch_acquisition_text(self, xpath_list=[], text_value=""):
        """批量获取输入框"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                value = self.get_find_element_xpath(xpath).text
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

    def get_checkbox_value(self, xpath_list=[]):
        """获取复选框值"""
        values = []
        for index, xpath in enumerate(xpath_list, 1):
            try:
                value = self.get_find_element_xpath(xpath)
                is_checked = value.is_selected()
                values.append(is_checked)

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )
        return values

    def batch_modify_select_input(self, xpath_list=[]):
        """批量修改下拉框"""
        for idx, d in enumerate(xpath_list, start=1):
            self.click_button(d['select'])
            self.click_button(d['value'])
