from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class PsiPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)  # 调用基类构造函数

    def enter_texts(self, xpath, text):
        """输入文字."""
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        sleep(0.5)
        element.send_keys(text)

    def click_button(self, xpath):
        """点击按钮."""
        self.click(By.XPATH, xpath)

    def click_button_psi(self, name):
        """点击按钮."""
        sleep(1)
        self.click_button(f'//p[text()="{name}"]')

    def add_psi(self, name="", condition: bool = True, method: bool = True):
        """添加psi"""
        self.click_button_psi("新增")
        if name:
            self.enter_texts('//div[p[text()="PSI名称: "]]//input', name)
        if condition:
            self.click_button('(//div[p[text()="最上位行收集条件: "]]//i)[2]')
            self.click_button('//div[text()=" 标准登录 "]')
            ele = self.get_find_element_xpath('//span[text()="工作输入指令或工作输出指令"]')
            ActionChains(self.driver).double_click(ele).perform()
            self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        if method:
            self.click_button('(//div[p[text()="筛选方法: "]]//i)[2]')
            self.click_button('//div[text()=" 标准登录 "]')
            ele = self.get_find_element_xpath('//span[text()="分派结束"]')
            ActionChains(self.driver).double_click(ele).perform()
            self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

    def click_data(self, num="", name=""):
        if num == 1:
            self.click_button('//div[text()=" 透视数据表行 "]')
        if num == 2:
            self.click_button('//div[text()=" 透视数据表列 "]')
        if num == 3:
            self.click_button('//div[text()=" 透视数据内容 "]')
        self.click_button(f'(//i[@class="ivu-icon ivu-icon-md-add"])[{num}]')
        self.enter_texts(f'(//table[@class="vxe-table--body"]//tr/td[2]//input)[{num}]', name)
        self.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]//input)[{num}]')
        self.click_button(f'(//i[@class="ivu-icon ivu-icon-ios-build"])[{num}]')

    def enter_group_setting(self, name):
        self.click_button('//div[p[text()=" 标签: "]]//i')
        ele = self.get_find_element_xpath('//span[text()="该分类的名字"]')
        ActionChains(self.driver).double_click(ele).perform()
        self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')

        self.click_button('//div[p[text()=" 组化键: "]]//i')
        ele = self.get_find_element_xpath('//span[text()="按品目归结"]')
        ActionChains(self.driver).double_click(ele).perform()
        self.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')

        self.click_button('//div[p[text()=" 显示空数据: "]]//i')
        self.click_button('//li[text()="是"]')

        self.click_button('//div[@class="vxe-modal--box"]//i[@class="ivu-icon ivu-icon-md-add"]')
        self.enter_texts('//div[@class="vxe-modal--box"]//table[@class="vxe-table--body"]//tr/td[2]//input', name)
        self.click_button('//div[@class="vxe-modal--box"]//table[@class="vxe-table--body"]//tr/td[2]//input')
        self.click_button('//div[@class="vxe-modal--box"]//i[@class="ivu-icon ivu-icon-ios-build"]')

    def enter_group_update(self, name):
        self.enter_texts('//div[label[text()="标签"]]//input', name)
        self.enter_texts('//div[label[text()="显示内容"]]//input', name)
        self.enter_texts('//div[label[text()="初始值"]]//input', name)

        self.click_button('//div[label[text()="文字颜色表达式"]]//i')
        ele = self.get_find_element_xpath('//span[text()="第二个值比第一个值大的话就显示绿色，其它的话就显示红色"]')
        ActionChains(self.driver).double_click(ele).perform()
        self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')

        self.click_button('//div[label[text()="背景颜色表达式"]]//i')
        ele = self.get_find_element_xpath('//span[text()="第一个值为0以上的话就显示绿色，其他的话就显示灰色"]')
        ActionChains(self.driver).double_click(ele).perform()
        self.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')

        self.click_button('//div[label[text()="限制0的数值"]]//i')
        self.click_button('//div[label[text()="限制0的数值"]]//ul/li[text()="是"]')

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

    def right_refresh(self, name="PSI设置"):
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
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )
        sleep(1)

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

    def batch_modify_input(self, xpath_list=[], new_value=""):
        """批量修改输入框"""
        for xpath in xpath_list:
            try:
                self.enter_text(By.XPATH,xpath, new_value)
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

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

    def del_data(self, value=[]):
        """
        删除数据项

        该函数通过遍历提供的xpath列表，对每个数据项执行删除操作。
        主要流程包括：点击数据项、点击删除按钮、确认删除对话框。

        参数:
            value (list): 包含xpath表达式的列表，用于定位要删除的数据项

        返回值:
            无返回值
        """
        # 遍历xpath列表，对每个数据项执行删除操作
        for index, xpath in enumerate(value, start=1):
            try:
                # 点击数据项
                self.click_button(xpath)
                # 点击删除按钮
                self.click_button(f'(//table[@class="vxe-table--body"]//tr/td[2]//input)[1]')
                # 点击关闭图标
                self.click_button(f'(//i[@class="ivu-icon ivu-icon-md-close"])[{index}]')
                # 点击确认删除按钮
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            except NoSuchElementException:
                print(f"未找到元素: {xpath}")
            except Exception as e:
                print(f"操作 {xpath} 时出错: {str(e)}")

    def del_all(self, value=[], xpath=''):
        for index, v in enumerate(value, start=0):
            try:
                self.enter_texts(xpath, v)
                sleep(1)
                self.click_button(f'//table[@class="vxe-table--body"]//tr/td[2]//span[text()="{v}"]')
                self.click_button_psi("删除")  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
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