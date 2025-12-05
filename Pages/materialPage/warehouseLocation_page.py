import random
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class WarehouseLocationPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def click_add_button(self):
        """点击添加按钮."""
        self.click(By.XPATH, '//p[text()="新增"]')

    def click_edi_button(self):
        """点击修改按钮."""
        self.click(By.XPATH, '//p[text()="编辑"]')

    def clear_input(self, xpath):
        input_element = self.get_find_element_xpath(xpath)
        print('input_element', input_element)
        input_element.clear()  # 清空input元素的内容

    def filter_method(self, click_xpath):
        """过滤公共方法"""
        sleep(2)
        self.click_button(click_xpath)
        sleep(2)
        self.click_button('//div[@class="filterInput"]//following-sibling::label')
        sleep(1)
        self.click_button('//div[@class="filter-btn-bar"]/button')
        sleep(1)
        item_code = self.driver.find_elements(
            By.XPATH,
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        )
        # sleep(1)
        # self.click_button('//div[@class="filterInput"]//preceding-sibling::div[1]')
        #
        # item_code2 = self.driver.find_elements(
        #     By.XPATH,
        #     '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]',
        # )
        sleep(1)
        self.click_ref_button()
        return len(item_code) == 0
        #and len(item_code2) > 0

    def add_layout(self, layout):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')
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
        # 获取是否可见选项的复选框元素
        checkbox2 = self.get_find_element_xpath(
            '(//div[./div[text()="是否可见:"]])[1]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox2.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            self.click_button('(//div[./div[text()="是否可见:"]])[1]/label/span')
            # 点击确定按钮保存设置
            self.click_button('//div[@class="h-100 setTableTwo"]/following-sibling::div/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            self.click_button('//div[@class="h-100 setTableTwo"]/following-sibling::div/button[2]')

    def del_layout(self, layout):
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = self.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = self.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）

        try:
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
            )
        except TimeoutException:
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
            )
            self.click_button(
                f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
            )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        self.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

    def wait_for_el_loading_mask(self, timeout=15):
        """
        显式等待加载遮罩元素消失。

        参数:
        - timeout (int): 超时时间，默认为10秒。

        该方法通过WebDriverWait配合EC.invisibility_of_element_located方法，
        检查页面上是否存在class中包含'el-loading-mask'且style中不包含'display: none'的div元素，
        以此判断加载遮罩是否消失。
        """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def click_del_button(self):
        """点击删除按钮."""
        self.click(By.XPATH, '//p[text()="删除"]')

    def click_sel_button(self):
        """点击查询按钮."""
        self.click(By.XPATH, '//p[text()="查询"]')
        self.wait_for_el_loading_mask()

    def click_ref_button(self):
        """点击刷新按钮."""
        self.click(By.XPATH, '//p[text()="刷新"]')

    def enter_texts(self, xpath, text):
        """输入文字."""
        self.enter_text(By.XPATH, xpath, text)

    def click_button(self, xpath):
        """点击按钮."""
        self.click(By.XPATH, xpath)

    def batch_modify_input(self, xpath_list=[], new_value=""):
        """批量修改输入框"""
        for xpath in xpath_list:
            try:
                print('new_value',new_value,xpath)
                self.enter_texts(xpath, new_value)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def get_demo_num1(self):
        num = 0
        sleep(1)
        num = 1
        return num

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

    def batch_acquisition_input_list(self, xpath_list=[], val_list=[]):
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
                print("index", index - 1)
                if value == val_list[index - 1]:
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

    def batch_acquisition_input(self, xpath_list=[], text_value=""):
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
                if value == text_value:
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

    def acquisition_input(self, xpath):
        """获取输入框值"""
        # 显式等待元素可见（最多等待10秒）
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(("xpath", xpath))
        )
        # 获取输入框的值
        value = element.get_attribute("value")
        return value

    def go_item(self):
        """前往物料页面"""
        self.click_button('(//span[text()="物控管理"])[1]')  # 点击物控管理
        self.click_button('(//span[text()="物控基础数据"])[1]')  # 点击物控基础数据
        self.click_button('(//span[text()="仓库库位"])[1]')  # 点击仓库库位

    def add_item(self, material_code, material_name):
        """添加物料信息."""
        self.click_add_button()
        self.enter_texts(
            '(//label[text()="物料代码"])[1]/parent::div//input', material_code
        )
        self.enter_texts(
            '(//label[text()="物料名称"])[1]/parent::div//input', material_name
        )
        self.click_button('(//button[@type="button"]/span[text()="确定"])[4]')

    def delete_item(self, material_code):
        """删除物料信息."""
        # 定位内容为‘1测试A’的行
        self.click_button(
            f'(//span[text()="{material_code}"])[1]/ancestor::tr[1]/td[2]'
        )
        self.click_del_button()  # 点击删除
        # 点击确定
        # 找到共同的父元素
        parent = self.get_find_element_class("ivu-modal-confirm-footer")

        # 获取所有button子元素
        all_buttons = parent.find_elements(By.TAG_NAME, "button")

        # 选择需要的button 第二个确定按钮
        second_button = all_buttons[1]
        second_button.click()

    def check_item_exists(self, item_name):
        """检查物料是否存在."""
        try:
            self.get_find_element_xpath(f'//span[text()="{item_name}"]')
            return True
        except:
            return False

    def get_find_element_xpath(self, xpath):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
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

    def add_none(self, xpath_list=[], color_value=""):
        """新增弹窗(有必填项)不填写信息，不允许提交公共方法."""
        for index, xpath in enumerate(xpath_list, 1):
            try:
                element = self.get_find_element_xpath(xpath)
                this_color = element.value_of_css_property("border-color")
                # 获取输入框的值
                if color_value != this_color:
                    raise NoSuchElementException(
                        f"边框颜色不对{this_color}（XPath列表第{index}个）: {xpath}"
                    )
                    return False

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )
        return True

    def add_one(self, xpath_list=[], color_value=""):
        """新增弹窗(有必填项)多项必填只填写一项不允许提交方法，不允许提交公共方法."""
        for index, xpath in enumerate(xpath_list, 1):
            try:
                element = self.get_find_element_xpath(xpath)
                # 获取输入框的值
                if color_value != element.value_of_css_property("border-color"):
                    raise NoSuchElementException(
                        f"边框颜色不对（XPath列表第{index}个）: {xpath}"
                    )
                    return False

            except TimeoutException:
                raise NoSuchElementException(
                    f"元素未找到（XPath列表第{index}个）: {xpath}"
                )
            except Exception as e:
                raise Exception(
                    f"获取输入框值时发生错误（XPath列表第{index}个）: {str(e)}"
                )
        return True

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def click_select_button(self):
        """点击查询确定按钮."""
        self.click_button('(//button[@class="ivu-btn ivu-btn-primary"]/span[text()="确定"])[2]')
        sleep(1)
        self.wait_for_loading_to_disappear()