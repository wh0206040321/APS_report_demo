from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages


class MaterialSubstitutionPage(BasePage):
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
        sleep(1)

    # 等待加载遮罩消失
    def wait_for_el_loading_mask(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        sleep(1)

    def click_all_button(self, name):
        """点击按钮."""
        self.click_button(f'//div[@class="flex-alignItems-center background-ffffff h-36px w-b-100 m-l-12 toolbar-container"]//p[text()="{name}"]')

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

    def select_input_substitution(self, name):
        """选择替代场景输入框."""
        self.wait_for_loading_to_disappear()
        xpath = '//div[div[span[text()=" 替代场景"]]]//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        sleep(0.5)
        self.enter_texts(xpath, name)
        sleep(1)

    def click_select_button(self):
        """点击选择按钮."""
        self.click_button('//div[@id="8quvzg1r-ahmn"]//button')
        self.wait_for_loading_to_disappear()

    def loop_click(self, count):
        """
        循环点击方法
        :param driver: Selenium WebDriver
        :param count: 循环次数（即 my-list-item 下标最大值）
        """
        for i in range(1, count + 1):
            # 第一步：点击输入框
            self.click_button('//div[@id="d6hm28lu-jl64"]//input')
            sleep(1)
            # 第二步：点击 my-list-item[i]
            list_item_xpath = f'(//div[@class="el-scrollbar"])[last()]//div[@class="my-list-item"][{i}]'
            self.click_button(list_item_xpath)
            sleep(1)
            # 第三步：点击确认按钮
            self.click_button('//div[@id="d9i00fi8-vwtd"]/i')
            sleep(1)

            print(f"第 {i} 次循环完成")

    def add_material_substitution(self, num, name=""):
        """添加物料替代"""
        adds = AddsPages(self.driver)
        select_list1 = [{"select": '//div[@id="h0590xfj-jemd"]//input',
                        "value": f'(//div[@class="el-scrollbar"])[last()]//div[@class="my-list-item"][{num}]'},
                       {"select": '//div[@id="gid148zp-0f98"]//input',
                        "value": '(//div[@class="el-scrollbar"]//span[text()="*"])[last()]'}]
        select_list2 = [{"select": '//div[@id="ho29oiq5-qhal"]//input',
                         "value": f'(//div[@class="el-scrollbar"])[last()]//div[@class="my-list-item"][{num}]'},
                        {"select": '//div[@id="db2x9abu-154j"]//input',
                         "value": '(//div[@class="el-scrollbar"])[last()]//div[@class="my-list-item"][1]'}]
        self.click_all_button("新增")
        if name:
            self.wait_for_loading_to_disappear()
            sleep(1)
            self.click_button('//div[@id="88tcogwz-ptbs"]//label[text()=" 成组替代"]')
            sleep(3)
            adds.batch_modify_select_input(select_list1)
            self.click_button('//div[@id="sj42kd3w-8l59"]/i')
            sleep(2)
            # 定位目标区域
            target = self.driver.find_element(By.XPATH, '(//div[@class="vxe-table--body-wrapper body--wrapper"])[7]//table')

            # 循环拖拽两个源元素
            sources = [
                self.driver.find_element(By.XPATH, '(//table[@class="vxe-table--body"]//tr[1]/td[1])[3]'),
                self.driver.find_element(By.XPATH, '(//table[@class="vxe-table--body"]//tr[2]/td[1])[3]')
            ]

            for source in sources:
                actions = ActionChains(self.driver)
                actions.click_and_hold(source).pause(0.5).move_to_element(target).pause(0.5).release().perform()
                sleep(1)  # 给前端一点反应时间

            self.loop_click(num)

        else:
            adds.batch_modify_select_input(select_list1)
            self.click_button('//div[@id="sj42kd3w-8l59"]/i')
            adds.batch_modify_select_input(select_list2)

        self.click_button('(//div[@class="vxe-modal--footer"]//span[text()="确定"])[2]')

    def click_flagdata(self):
        """点击更新时间."""
        self.wait_for_loading_to_disappear()
        self.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(2)
        self.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(2)

    def click_update(self):
        self.click_flagdata()
        self.click_button('//table[@class="vxe-table--body"]//tr[1]/td[2]')
        sleep(1)
        self.click_all_button("编辑")
        self.wait_for_loading_to_disappear()

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

        num = self.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="更新时间"]]]/td[7]//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.DELETE)
        num.send_keys("10")

        try:
            self.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        except:
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

        self.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        self.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        self.wait_for_loading_to_disappear()
