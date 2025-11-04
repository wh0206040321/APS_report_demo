from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Utils.data_driven import DateDriver


class SynchronizePage(BasePage):
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

    def right_refresh(self, name="配置同步"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    # 等待加载遮罩消失
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

    def click_synchronize_button(self):
        """点击同步按钮."""
        self.click_button('//p[text()="同步"]')

    def switch_plane(self, name, num, js=True):
        """切换计划方案。"""
        if js:
            plan = DateDriver()
            self.click_button(f'//div[contains(text(),"{plan.planning}")]')

        self.click_button(f'//ul/li[text()="{name}"]')
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//div[@class="loadingbox"]')
            )
        )
        sleep(1)
        menu_paths = {
            1: ["系统管理", "单元设置", "PSI设置"],
            2: ["计划运行", "方案管理", "计划方案管理"],
            3: ["计划运行", "方案管理", "物控方案管理"],
            4: ["数据接口底座", "DBLinK", "导入设置"]
        }

        for menu in menu_paths.get(num, []):
            self.click_button(f'(//span[text()="{menu}"])[1]')

    # def click_checkbox_value(self, name1=[], name2=[], num=""):
    #     """批量勾选复选框"""
    #     if num == "1":
    #         self.click_button('//div[text()=" PSI设置 "]')
    #         for index, value in enumerate(name1, start=1):
    #             try:
    #                 ele = self.get_find_element_xpath('//div[p[text()="PSI名称"]]/following-sibling::div//input')
    #                 ele.send_keys(Keys.CONTROL, 'a')
    #                 ele.send_keys(Keys.DELETE)
    #                 self.enter_texts('//div[p[text()="PSI名称"]]/following-sibling::div//input', value)
    #                 self.click_button(f'(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span')
    #             except NoSuchElementException:
    #                 print(f"未找到元素: {value}")
    #             except Exception as e:
    #                 print(f"操作 {value} 时出错: {str(e)}")
    #     elif num == "2":
    #         self.click_button('//div[text()=" 计划方案 "]')
    #         for index, value in enumerate(name1, start=1):
    #             try:
    #                 ele = self.get_find_element_xpath('//div[p[text()="计划方案名称"]]/following-sibling::div//input')
    #                 ele.send_keys(Keys.CONTROL, 'a')
    #                 ele.send_keys(Keys.DELETE)
    #                 self.enter_texts('//div[p[text()="计划方案名称"]]/following-sibling::div//input', value)
    #                 self.click_button(f'(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span')
    #             except NoSuchElementException:
    #                 print(f"未找到元素: {value}")
    #             except Exception as e:
    #                 print(f"操作 {value} 时出错: {str(e)}")
    #     elif num == "3":
    #         self.click_button('//div[text()=" 数据导入 "]')
    #         for index, value in enumerate(name1, start=1):
    #             try:
    #                 ele = self.get_find_element_xpath('//div[p[text()="数据导入方案名称"]]/following-sibling::div//input')
    #                 ele.send_keys(Keys.CONTROL, 'a')
    #                 ele.send_keys(Keys.DELETE)
    #                 self.enter_texts('//div[p[text()="数据导入方案名称"]]/following-sibling::div//input', value)
    #                 self.click_button(f'(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span')
    #             except NoSuchElementException:
    #                 print(f"未找到元素: {value}")
    #             except Exception as e:
    #                 print(f"操作 {value} 时出错: {str(e)}")
    #
    #     for index, value in enumerate(name2, start=1):
    #         try:
    #             ele = self.get_find_element_xpath(f'(//div[p[text()="计划单元"]]/following-sibling::div//input)[{num}]')
    #             ele.send_keys(Keys.CONTROL, 'a')
    #             ele.send_keys(Keys.DELETE)
    #             self.enter_texts(f'(//div[p[text()="计划单元"]]/following-sibling::div//input)[{num}]', value)
    #             self.click_button(f'(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span')
    #         except NoSuchElementException:
    #             print(f"未找到元素: {value}")
    #         except Exception as e:
    #             print(f"操作 {value} 时出错: {str(e)}")

    def handle_checkbox_interaction(self, input_xpath, value, click_xpath):
        try:
            ele = self.get_find_element_xpath(input_xpath)
            ele.send_keys(Keys.CONTROL, 'a')
            ele.send_keys(Keys.DELETE)
            self.enter_texts(input_xpath, value)
            sleep(1)
            self.click_button(click_xpath)
        except NoSuchElementException:
            print(f"未找到元素: {value}")
        except Exception as e:
            print(f"操作 {value} 时出错: {str(e)}")

    def click_checkbox_value(self, name1=[], name2=[], num=""):
        """批量勾选复选框"""

        config = {
            "1": {
                "section_xpath": '//div[text()=" PSI设置 "]',
                "input_xpath": '//div[p[text()="PSI名称"]]/following-sibling::div//input',
                "click_xpath_template": '(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span'
            },
            "2": {
                "section_xpath": '//div[text()=" 计划方案 "]',
                "input_xpath": '//div[p[text()="计划方案名称"]]/following-sibling::div//input',
                "click_xpath_template": '(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span'
            },
            "3": {
                "section_xpath": '//div[text()=" 物控方案 "]',
                "input_xpath": '//div[p[text()="物控方案"]]/following-sibling::div//input',
                "click_xpath_template": '(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span'
            },
            "4": {
                "section_xpath": '//div[text()=" 数据导入 "]',
                "input_xpath": '//div[p[text()="数据导入方案名称"]]/following-sibling::div//input',
                "click_xpath_template": '(//tr[td[3]//span[text()="{value}"]])[1]/td[2]/div/span'
            }
        }

        if num in config:
            section = config[num]
            self.click_button(section["section_xpath"])
            for value in name1:
                self.handle_checkbox_interaction(
                    input_xpath=section["input_xpath"],
                    value=value,
                    click_xpath=section["click_xpath_template"].format(value=value)
                )

        # 处理计划单元部分
        for value in name2:
            input_xpath = f'(//div[p[text()="计划单元"]]/following-sibling::div//input)[{num}]'
            click_xpath = f'//tr[td[3]//span[text()="{value}"]]/td[2]/div/span'
            self.handle_checkbox_interaction(input_xpath, value, click_xpath)

    def click_synchronize_pop(self, button: bool = True):
        """点击同步弹窗确定按钮."""
        if button:
            self.click_button('//div[div[text()="将同步数据到目的计划单元, 是否继续?"]]/following-sibling::div//span[text()="确定"]')
        else:
            self.click_button('//div[div[text()="将同步数据到目的计划单元, 是否继续?"]]/following-sibling::div//span[text()="取消"]')
