from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class AddsPages(BasePage):
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

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def wait_for_el_loading_mask(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )

    def batch_modify_input(self, xpath_list=[], new_value=""):
        """批量修改输入框"""
        for xpath in xpath_list:
            try:
                sleep(0.3)
                self.enter_texts(xpath, new_value)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_modify_dialog_box(self, xpath_list=[], new_value=""):
        """批量修改对话框"""
        for xpath in xpath_list:
            try:
                self.click_button(xpath)
                self.wait_for_loading_to_disappear()
                self.click_button(new_value)
                sleep(0.2)
                self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_modify_code_box(self, xpath_list=[], new_value=""):
        """批量修改代码对话框双击"""
        for xpath in xpath_list:
            try:
                self.click_button(xpath)
                ActionChains(self.driver).double_click(self.get_find_element_xpath(new_value)).perform()
                sleep(0.5)
                self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[last()]//span[text()="确定"]')
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def batch_modify_select_input(self, xpath_list=[]):
        """批量修改下拉框"""
        for idx, d in enumerate(xpath_list, start=1):
            self.click_button(d['select'])
            self.click_button(d['value'])

    def batch_modify_time_input(self, xpath_list=[]):
        """批量修改时间"""
        for index, xpath in enumerate(xpath_list, start=1):
            try:
                self.click_button(xpath)
                self.click_button(f'(//span[@class="ivu-date-picker-cells-cell ivu-date-picker-cells-cell-today ivu-date-picker-cells-focused"])[1]')
                self.click_button(f'(//div[@class="ivu-picker-confirm"])[{index}]/button[3]')
                sleep(0.5)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

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

    def batch_modify_inputs(self, xpath_value_map: dict):
        """通过字典批量修改输入框（键为XPath，值为输入内容）"""
        for xpath, value in xpath_value_map.items():
            self.enter_texts(xpath, value)

    def add_layout(self, layout):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')
        self.wait_for_el_loading_mask()
        sleep(2)
        self.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        checkbox1 = self.get_find_element_xpath(
            '//div[text()="是否默认启动:"]/following-sibling::label/span'
        )

        # 检查复选框是否未被选中
        if checkbox1.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            self.click_button(
                '//div[text()="是否默认启动:"]/following-sibling::label/span'
            )
        sleep(1)

        self.click_button('(//div[text()=" 显示设置 "])[1]')
        sleep(1)
        # 获取是否可见选项的复选框元素
        checkbox2 = self.get_find_element_xpath(
            '(//div[./div[text()="是否可见:"]])[1]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox2.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            self.click_button('(//div[./div[text()="是否可见:"]])[1]/label/span')
            # 点击确定按钮保存设置
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

    def go_settings_page(self):
        """
        进入设置页面
        """
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[3]//i')
        self.wait_for_el_loading_mask()
        sleep(1)
        self.click_button('//div[text()=" 显示设置 "]')
        sleep(5)
        ele = self.get_find_element_xpath('(//div[@class="vxe-table--body-wrapper body--wrapper"])[4]')
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", ele)
        sleep(1)
        ele = self.finds_elements(By.XPATH, '(//div[@class="vxe-table--fixed-left-wrapper"])[3]//table[@class="vxe-table--body"]//tr[last()]//div')
        num1 = ele[0].text
        if num1:
            num = self.get_find_element_xpath('(//div[@class="vxe-table--fixed-left-wrapper"])[3]//table[@class="vxe-table--body"]//tr[last()]//div').text
        else:
            num = self.get_find_element_xpath(
                '(//div[@class="vxe-table--fixed-left-wrapper"])[2]//table[@class="vxe-table--body"]//tr[last()]//div').text
        sleep(0.5)
        try:
            self.click_button('(//div[@class="demo-drawer-footer"])[2]//span[text()="确定"]')
        except Exception:
            # 如果第一个点不了，就点另一个
            self.click_button('(//div[@class="demo-drawer-footer"])[3]//span[text()="确定"]')

        self.wait_for_loading_to_disappear()
        return num

    def batch_order_time_input(self, xpath_list=[]):
        """订单页：按累积策略查找“今天”按钮，每次点击成功后索引递增"""
        start_today_index = 1  # 初始查找索引

        for input_index, xpath in enumerate(xpath_list, start=1):
            try:
                self.click_button(xpath)
                sleep(0.5)  # 等待日期控件弹出

                max_today_index = 50  # 可根据页面总数设定更大的范围
                clicked = False

                for today_index in range(start_today_index, max_today_index + 1):
                    today_xpath = f'(//span[contains(@class, "ivu-date-picker-cells-cell-today")])[{today_index}]'
                    try:
                        WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, today_xpath))
                        )
                        self.click_button(today_xpath)

                        # 确认按钮与 today_index 一致（如页面结构不稳定可改为 input_index）
                        confirm_xpath = f'(//div[@class="ivu-picker-confirm"])[{today_index}]/button[3]'
                        WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, confirm_xpath))
                        )
                        self.click_button(confirm_xpath)

                        print(f"✅ 第 {input_index} 项: 点击了第 {today_index} 个“今天”按钮")
                        start_today_index = today_index + 1  # 下次从下一个开始
                        clicked = True
                        break
                    except (TimeoutException, ElementClickInterceptedException):
                        continue

                if not clicked:
                    print(f"❌ 第 {input_index} 项: 没有可点击的“今天”按钮")

            except Exception as e:
                print(f"🛑 第 {input_index} 项执行出错: {str(e)}")



