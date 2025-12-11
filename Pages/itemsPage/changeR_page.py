from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class ChangeR(BasePage):
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

    def del_data(self):
        self.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        self.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        # 定位第一行
        self.click_button(
            '//table[@class="vxe-table--body"]//tr[1]/td[2]'
        )
        self.click_del_button()  # 点击删除
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def click_flagdata(self):
        self.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )
        sleep(1)
        self.click_button(
            '//div[p[text()="更新时间"]]/div[1]'
        )

    def right_refresh(self, name):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    def wait_for_loading_to_disappear(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.XPATH,
                 "(//div[contains(@class, 'vxe-loading') and contains(@class, 'vxe-table--loading') and contains(@class, 'is--visible')])[2]")
            )
        )

    def click_select_button(self):
        """点击查询确定按钮."""
        self.click_button('(//div[@class="demo-drawer-footer"]//span[text()="确定"])[3]')
        sleep(0.5)
        self.wait_for_loading_to_disappear()

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

    def add_layout(self, layout):
        """添加布局."""
        self.click_button('//div[@class="toolTabsDiv"]/div[2]/div[2]//i')
        self.click_button('//li[text()="添加新布局"]')
        self.wait_for_el_loading_mask()
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
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            self.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

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
        self.wait_for_loading_to_disappear()

    def click_changespec_num(self, num):
        """点击指定生产特征数字"""
        try:
            self.click_button(f'(//span[text()="生产特征{num}切换"])[1]')
        except Exception as e:
            self.click_button('(//span[text()="计划管理"])[1]')
            self.click_button('(//span[text()="计划切换定义"])[1]')
            self.click_button(f'(//span[text()="生产特征{num}切换"])[1]')
        self.wait_for_loading_to_disappear()

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(
            f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

    def add_changespec_data(self, name):
        """添加数据."""
        self.click_add_button()  # 检查点击添加
        # 输入代码
        self.enter_texts('(//label[text()="资源"])[1]/parent::div//input', name)
        self.enter_texts('(//label[text()="前生产特征"])[1]/parent::div//input', name)
        self.enter_texts('(//label[text()="后生产特征"])[1]/parent::div//input', name)
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def edit_changespec_data(self, before_name, after_name):
        """编辑数据."""
        self.click_button(f'//tr[./td[2][.//span[text()="{before_name}"]]]/td[2]')
        self.click_edi_button()  # 检查点击编辑
        # 输入代码
        self.enter_texts('(//label[text()="资源"])[1]/parent::div//input', after_name)
        self.enter_texts('(//label[text()="前生产特征"])[1]/parent::div//input', after_name)
        self.enter_texts('(//label[text()="后生产特征"])[1]/parent::div//input', after_name)
        self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def del_changespec_data(self, name):
        """删除数据."""
        self.click_button(f'//tr[./td[2][.//span[text()="{name}"]]]/td[2]')
        self.click_del_button()  # 检查点击删除
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()

    def select_changespec_data(self, name):
        """查询数据."""
        self.click_sel_button()
        sleep(1)
        # 定位名称输入框
        element_to_double_click = self.driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(self.driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        sleep(1)
        # 点击物料代码
        self.click_button('//div[text()="资源" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        self.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        self.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        self.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            name,
        )
        sleep(1)

        # 点击确认
        self.click_select_button()
