from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage
from Pages.itemsPage.adds_page import AddsPages


class MaterialControlDefinition(BasePage):
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

    def select_input_mrq(self, name):
        """选择需求来源编码输入框."""
        self.wait_for_loading_to_disappear()
        xpath = '//div[p[text()="需求来源编码"]]/following-sibling::div//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        sleep(0.5)
        self.enter_texts(xpath, name)
        sleep(1)

    def select_input_mcd(self, name):
        """选择供应来源编码输入框."""
        self.wait_for_loading_to_disappear()
        xpath = '//div[p[text()="供应来源编码"]]/following-sibling::div//input'
        ele = self.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.DELETE)
        sleep(0.5)
        self.enter_texts(xpath, name)
        sleep(1)

    def double_click_th_dropdown_box(self, xpath_list=[]):
        """双击下拉框并点击下拉值，如果第一次点击不到则再次双击再点击"""
        for idx, d in enumerate(xpath_list, start=1):
            # 第一次双击
            ActionChains(self.driver).double_click(self.get_find_element_xpath(d['select'])).perform()
            sleep(0.5)
            for attempt in range(4):  # 最多尝试4次
                try:
                    self.click_button(d['value'])
                    break  # 成功就退出循环
                except Exception:
                    # 如果失败，先点击 select 再等待
                    self.click_button(d['select'])
                    sleep(0.5)
            else:
                # 如果三次都失败，可以在这里抛出异常或记录日志
                raise RuntimeError(f"无法点击 {d['value']} after 3 attempts")

            sleep(1)
            # 点击备注输入框
            self.click_button('//div[div[text()="备注:"]]//input')
            sleep(1)

    def add_data(self, value, num=1):
        """添加物控需求定义数据."""
        adds = AddsPages(self.driver)
        self.click_all_button("新增")
        sleep(1)
        self.click_button('//div[div[text()="标准需求设置-新增"]]//i[@title="最大化"]')
        input_list = [
            '//div[div[text()=" 需求来源编码: "]]//input',
            '//div[div[text()=" 需求来源名称: "]]//input',
        ]
        select_list = [
            {"select": '//div[div[text()=" 数据库名称: "]]//input[@class="ivu-select-input"]',
             "value": f'(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[1]/li[{num}]'},
            {"select": '//div[div[text()=" 表或视图名: "]]//input[@class="ivu-select-input"]',
             "value": '(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[2]/li[text()="APS_Order"]'},
        ]
        fields = [
            "DataSource",
            "OrderCode",
            "ItemCode",
            "PlanStartTime",
            "PlanQty",
            "BomVersion",
        ]

        table_list = []

        for i, field in enumerate(fields, start=2):  # 从2开始递增
            entry = {
                "select": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]',
                "value": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]//li[{i}]'
            }
            table_list.append(entry)

        self.click_button('//label[span[text()="制造"]]')
        adds.batch_modify_select_input(select_list)
        adds.batch_modify_input(input_list, value)
        self.double_click_th_dropdown_box(table_list)

        element = self.get_find_element_xpath('(//div[@class="d-flex"]//div[@class="vxe-table--body-wrapper body--wrapper"])[1]')
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
        # self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 100;", element)
        last_ = [{
            "select": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="ReleaseMat"]]/td[6]',
            "value": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="ReleaseMat"]]/td[6]//li[8]'
        }]
        self.double_click_th_dropdown_box(last_)
        self.click_confirm()

    def add_supply_data(self, value, num=1):
        """添加物控供应定义数据."""
        adds = AddsPages(self.driver)
        self.click_all_button("新增")
        sleep(1)
        self.click_button('//div[div[text()="标准供应设置-新增"]]//i[@title="最大化"]')
        input_list = [
            '//div[div[text()=" 供应来源编码: "]]//input',
            '//div[div[text()=" 供应来源名称: "]]//input',
            '//div[div[text()=" 供应来源顺序: "]]//input',
        ]
        select_list = [
            {"select": '//div[div[text()=" 数据库名称: "]]//input[@class="ivu-select-input"]',
             "value": f'(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[1]/li[{num}]'},
            {"select": '//div[div[text()=" 表或视图名: "]]//input[@class="ivu-select-input"]',
             "value": '(//div[@class="d-flex m-b-10"]//ul[@class="ivu-select-dropdown-list"])[2]/li[text()="APS_Order"]'},
        ]
        fields = [
            "Bussiness_No",
            "DataSource",
            "ItemCode",
            "SupplyCode",
            "SupplyDate",
            "SupplyName",
            "SupplyQty",
        ]

        table_list = []

        for i, field in enumerate(fields, start=2):  # 从2开始递增
            entry = {
                "select": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]',
                "value": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="{field}"]]/td[6]//li[{i}]'
            }
            table_list.append(entry)

        adds.batch_modify_select_input(select_list)
        adds.batch_modify_input(input_list, value)
        self.double_click_th_dropdown_box(table_list)

        # element = self.get_find_element_xpath('(//div[@class="d-flex"]//div[@class="vxe-table--body-wrapper body--wrapper"])[1]')
        # self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
        # last_ = [{
        #     "select": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="ReleaseMat"]]/td[6]',
        #     "value": f'//div[@class="d-flex"]//table[@class="vxe-table--body"]//tr[td[3]//span[text()="ReleaseMat"]]/td[6]//li[8]'
        # }]
        # self.double_click_th_dropdown_box(last_)
        self.click_confirm()

    def click_select_mcr(self, code="", data=""):
        """点击物控计算履历 查找."""
        if code:
            self.click_button('//div[span[text()="物控计算单号:"]]//input[@class="ivu-select-input"]')
            self.click_button(f'//div[span[text()="物控计算单号:"]]//ul[@class="ivu-select-dropdown-list"]/li[{code}]')
            sleep(0.5)
        if data:
            self.click_button('//div[span[text()="物控方案名称:"]]//input[@class="ivu-select-input"]')
            sleep(2)
            self.click_button(f'//div[span[text()="物控方案名称:"]]//ul[@class="ivu-select-dropdown-list"]/li[{data}]')
            sleep(0.5)
        self.click_button('//button[span[text()="查询"]]')
        self.wait_for_loading_to_disappear()

    def click_details(self, name):
        """点击物控计算履历 详情."""
        self.click_button(f'//button[span[text()="详情"]]')
        self.click_button(f'(//div[@class="ivu-tabs-nav"])[2]/div[text()=" {name} "]')
        self.click_button('(//button[span[text()="查询"]])[2]')
        self.wait_for_loading_to_disappear()

    def del_all(self, xpath, value=[]):
        for index, v in enumerate(value, start=1):
            try:
                sleep(1)
                self.enter_texts(xpath, v)
                sleep(0.5)
                self.click_button(f'//tr[./td[2][.//span[text()="{v}"]]]/td[2]')
                self.click_all_button("删除")  # 点击删除
                self.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
                sleep(1)
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
