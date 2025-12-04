import random
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Pages.base_page import BasePage


class Coverage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def click_add_button(self):
        """点击添加按钮."""
        self.click(By.XPATH, '//p[text()="新增"]')

    def click_edi_button(self):
        """点击修改按钮."""
        self.click(By.XPATH, '//p[text()="编辑"]')

    def click_del_button(self):
        """点击删除按钮."""
        self.click(By.XPATH, '//p[text()="删除"]')

    def click_sel_button(self):
        """点击查询按钮."""
        self.click(By.XPATH, '//p[text()="查询"]')

    def click_ref_button(self):
        """点击刷新按钮."""
        self.click(By.XPATH, '//p[text()="刷新"]')

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

    def get_find_element_class(self, classname):
        """获取用户头像元素，返回该元素。如果元素未找到，返回None。"""
        try:
            return self.find_element(By.CLASS_NAME, classname)
        except NoSuchElementException:
            return None

    def get_find_message(self):
        """获取正确信息"""
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

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def click_select_button(self):
        """点击查询确定按钮."""
        self.click_button('(//div[@class="demo-drawer-footer"]//span[text()="确定"])[2]')
        sleep(0.5)
        self.wait_for_loading_to_disappear()

    def batch_modify_inputs(self, xpath_value_map: dict):
        """通过字典批量修改输入框（键为XPath，值为输入内容）"""
        for xpath, value in xpath_value_map.items():
            self.enter_texts(xpath, value)

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

        num = self.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="更新时间"]]]/td[7]//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.DELETE)
        num.send_keys("8")
        # 点击确定按钮保存设置
        try:
            self.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        except:
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

    def add_input_all(self, num):
        """输入框全部输入保存"""
        start = "2027/08/21 00:00:00"
        end = "2028/07/21 00:00:00"
        if num != "":
            # 点击资源
            self.click_button(
                '(//i[@class="ivu-icon ivu-icon-md-albums ivu-input-icon ivu-input-icon-normal"])[1]'
            )
            # 勾选框
            random_int = random.randint(2, 10)
            sleep(1)
            self.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
            sleep(1)
            self.click_button(
                '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
            )
            sleep(1)
            # 获取勾选的资源代码
            resource = self.get_find_element_xpath(
                '//div[@id="2ssy7pog-1nb7"]//input'
            ).get_attribute("value")

            # 时序
            self.enter_texts(
                '//div[@id="tg89jocr-6to2"]//input', f"{start};{end}"
            )

            # 点击下拉框
            self.click_button('//span[text()="请选择"]/following-sibling::i')
            self.click_button('//span[text()="RGB(100,255,178)"]')

            self.enter_texts('//div[@id="9la8xi09-07ws"]//input', num)
            self.enter_texts('//div[@id="k0z05daz-8tok"]//input', num)
            self.enter_texts('//div[@id="luvfyssv-uxe2"]//input', num)
            self.enter_texts('//div[@id="6ofb26y9-tous"]//input', num)

            sel = self.get_find_element_xpath('//div[@class="checkBoxComp position-absolute"]/label/span')
            if sel.get_attribute("class") == "ivu-checkbox":
                self.click_button(
                    '//div[@class="checkBoxComp position-absolute"]/label'
                )
            selClass = self.get_find_element_xpath('//div[@class="checkBoxComp position-absolute"]/label/span').get_attribute("class")

            self.click_button(
                '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
            )
            return resource, selClass, start, end
