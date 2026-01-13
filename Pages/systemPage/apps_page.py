from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages


class AppsPage(BasePage):
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
        message = WebDriverWait(self.driver, 30).until(
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

    def right_refresh(self):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" 应用管理 "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    # 等待加载遮罩消失
    def wait_for_el_loading_mask(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def select_input(self, name):
        """选择输入框."""
        xpath = '//div[div[p[text()="应用代码"]]]//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        sleep(0.5)
        self.enter_texts(xpath, name)
        sleep(0.5)

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

    def click_confirm(self):
        """点击确定"""
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

    def click_save_button(self):
        """点击保存按钮."""
        self.click_button('//div[@class="d-flex background-color-fff"]/div[1]')

    def click_apps_button(self):
        """点击应用管理"""
        self.click_button('//div[@class="scroll-outer"]//div[text()=" 应用管理 "]')
        self.right_refresh()

    def click_save_template_button(self, name, button: bool = True):
        """点击保存模版按钮."""
        self.click_button('//div[@class="d-flex background-color-fff"]/div[2]')
        self.enter_texts('//div[label[text()="名称"]]//input[@placeholder="请输入"]', name)
        if button:
            self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        try:
            self.get_find_message()
        except TimeoutException:
            pass

    def go_template(self):
        """
        进入模版管理页面
        """
        self.click_button('(//div[@class="ivu-tabs"])[1]/div[1]//div[text()=" 模板 "]')
        # ele = self.finds_elements(By.XPATH, f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[contains(text(),"{name}")]]')

    def get_template_num(self, name):
        """
        获取实际模版数量
        """
        ele = self.finds_elements(By.XPATH, f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[contains(text(),"{name}")]]')
        return len(ele)

    def delete_template(self, list_xpath=[]):
        """
        删除模版
        """
        for value in list_xpath:
            self.click_button(
                f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[contains(text(),"{value}")]]/span')
            self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
            self.get_find_message()

    def drag_component(self, name=""):
        """
        拖拽组件到画布区域。
        """
        # 定位拖拽源和目标元素
        source = self.get_find_element_xpath(f'(//div[@class="ivu-tabs"])[1]/div[2]//div[div/span[text()="{name}"]]')  # 拖拽起点元素
        target = self.get_find_element_xpath('//div[@id="canvasBox"]')  # 拖拽目标元素

        # 执行拖拽操作
        sleep(2)
        ActionChains(self.driver).drag_and_drop(source, target).perform()

    def del_all(self, xpath, value=[]):
        for index, v in enumerate(value, start=1):
            try:
                sleep(1)
                self.enter_texts(xpath, v)
                sleep(1)
                self.click_button(f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
                self.click_all_button("删除")  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                sleep(1)
                self.wait_for_loading_to_disappear()
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

        try:
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        except:
            self.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')

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

        self.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        self.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def click_close_button(self):
        """点击关闭按钮"""
        self.click_button('//div[div[text()=" 应用设计 "]]/span')
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="无需保存"]')
        sleep(1)
