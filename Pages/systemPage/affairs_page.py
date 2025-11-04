from time import sleep
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.base_page import BasePage


class AffairsPage(BasePage):
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

    def right_refresh(self, name="事务管理"):
        """右键刷新."""
        but = self.get_find_element_xpath(f'//div[@class="scroll-body"]/div[.//div[text()=" {name} "]]')
        but.click()
        # 右键点击
        ActionChains(self.driver).context_click(but).perform()
        self.click_button('//li[text()=" 刷新"]')
        self.wait_for_loading_to_disappear()

    def click_confirm_button(self):
        """点击确认按钮."""
        self.click_button('(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')
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
            lambda d: (
                d.find_element(By.CLASS_NAME, "el-loading-mask").value_of_css_property("display") == "none"
                if d.find_elements(By.CLASS_NAME, "el-loading-mask") else True
            )
        )
        sleep(1)

    def del_cycle(self, name="", edi="删除"):
        """循环删除指定名称的模板

        Args:
            name (str): 模板名称（默认空）
            edi (str): 操作类型，如"删除"（默认空）
        """
        deleted_count = 0  # 记录成功删除的数量
        for i in range(1, 8):  # 循环7次，对应name1到name7
            current_name = f"{name}{i}"  # 拼接当前要删除的模板名

            try:
                print(f"正在尝试删除模板: {current_name}")

                # 1. 悬停并点击删除按钮
                self.hover(current_name, edi)

                # 2. 处理删除确认弹窗
                try:
                    confirm = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//div[@class="el-message-box__btns"]//button/span[contains(text(),"确定")]')
                        )
                    )
                    confirm.click()
                    print(f"成功删除模板: {current_name}")
                    deleted_count += 1

                    # 等待删除操作完成
                    sleep(1)  # 根据实际需要调整等待时间

                except TimeoutException:
                    print(f"未找到删除确认弹窗，可能已经删除或无需确认: {current_name}")
                    continue

            except NoSuchElementException:
                print(f"模板 {current_name} 不存在，跳过")
                continue
            except Exception as e:
                print(f"删除模板 {current_name} 时发生异常: {str(e)}")
                continue

    def del_process(self, name, edi="删除"):
        """
        删除指定名称的流程记录

        :param name: 要删除的流程记录名称
        :param edi: 删除按钮的文本内容，默认为"删除"
        :return: 无返回值
        """
        while True:
            # 查找当前页面中符合条件的删除按钮
            eles = self.finds_elements(By.XPATH,
                                       f'//table[@class="el-table__body"]//tr[td[2][div[contains(text(),"{name}")]]]/td[last()]//span[text()="{edi}"]')

            if not eles:
                print("所有目标项已删除完毕")
                break  # 没有匹配项，退出循环

            # 删除第一个匹配项
            ele = eles[0]
            sleep(2)
            ele.click()
            sleep(1)
            self.click_button('//div[@class="el-message-box__btns"]/button[2]')

    def hover(self, name="", edi=""):
        # 悬停模版容器触发图标显示
        container = self.get_find_element_xpath(
            f'//div[@class="template-card__title"]/div[text()="{name}"]'
        )
        ActionChains(self.driver).move_to_element(container).perform()

        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//div[@class="template-card__title"]/div[text()="{name}"]/ancestor::div[3]//button/span[text()="{edi}"]'
            ))
        )

        # 3️⃣ 再点击图标
        delete_icon.click()

    def input_text(self, text):
        """输入文字."""
        self.enter_texts('//input[@placeholder="搜索相关事务名称或描述关键词"]', text)

    def click_process(self):
        """点击流程"""
        self.click_button('//div[@id="tab-flow"]')

    def click_process_log(self):
        """点击流程日志"""
        self.click_button('//div[@id="tab-log"]')

    def click_process_update(self, name):
        """点击编辑流程"""
        self.click_button(f'//table[@class="el-table__body"]//tr[td[2][div[text()="{name}"]]]/td[last()]//span[text()="编辑"]')

    def add_process_affairs(self, add: bool = True, name="", sel=""):
        """点击添加流程"""
        self.click_button('//div[text()="添加下一个事务 "]/i')
        if add:
            self.click_button('//div[@class="layout" and button[span[text()="新建事务"]]]/button')
            self.enter_texts('//div[label[text()="事务名称"]]//input', name)
            self.click_button(f'//div[label[text()="事务类型"]]//i')
            self.click_button(f'//span[text()="服务"]')
            self.click_button('//div[label[text()="配置参数"]]//i[@class="ivu-icon ivu-icon-md-albums paramIcon"]')
            self.click_button('//div[text()=" 自定义 "]')
            self.enter_texts('//div[p[text()="自定义服务:"]]//input', "http12ssc")
            self.click_button(
                '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[2]//span[text()="确定"]')
            self.click_button(
                '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]//span[text()="确定"]')
            self.click_button(f'//div[@class="application__name"]/div[@class="name" and contains(text(),"{name}")]')
        elif sel:
            self.enter_texts('//input[@placeholder="请输入关键词"]', sel)
            sleep(1)
            self.click_button(f'//div[@class="application__name"]/div[@class="name" and contains(text(),"{sel}")]')
        sleep(1)
        num = len(self.finds_elements(By.XPATH, '//div[@class="application__name"]/div[@class="name"]'))
        value = self.get_find_element_xpath('//div[@class="application__item activated"]/div[@class="application__name"]/div[@class="name"]').text
        self.click_button('//div[@class="el-dialog__footer"]//span[text()="确定"]')
        return num, value

    def click_add_affairs(self, name="", type="", button: bool = True):
        """点击新增事务"""
        self.click_button('//div[@id="pane-air"]//span[text()="新建事务"]')
        if name:
            self.enter_texts('//div[label[text()="事务名称"]]//input', name)
        if type:
            self.click_button(f'//div[label[text()="事务类型"]]//i')
            self.click_button(f'//span[text()="{type}"]')
            self.click_button('//div[label[text()="配置参数"]]//i[@class="ivu-icon ivu-icon-md-albums paramIcon"]')
        if button:
            self.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')

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

    def click_next(self):
        """点击下一步"""
        self.click_button('//div[@class="footer"]//span[text()="下一步"]')

    def click_save(self):
        """点击保存"""
        self.click_button('//div[@class="footer"]//span[text()="保存"]')

    def add_process(self, name="", type="", frequency="", time=""):
        """新增流程"""
        self.click_button('//button[span[text()="新建流程"]]')
        if name:
            self.enter_texts('//div[label[text()="名称"]]/div//input', name)
        if type:
            self.enter_texts('//div[label[text()="分类"]]/div//input', type)
        if frequency:
            self.click_button('//div[label[text()="频率"]]/div//i')
            sleep(1)
            if frequency == "一次":
                self.click_button(f'//li[span[text()="{frequency}"]]')
                if time:
                    self.click_button('//div[label[text()="执行时间"]]/div//input')
                    self.click_button('//td[@class="available today"]//span')
                    self.click_button('//div[@class="el-picker-panel__footer"]/button[2]')
            elif frequency == "每天":
                self.click_button(f'//li[span[text()="{frequency}"]]')
                self.click_button('//div[label[text()="执行设置"]]/div//i')
                sleep(1)
                if time == "1":
                    self.click_button('//li[span[text()="每天执行一次"]]')
                    self.click_button('(//input[@placeholder="开始日期"])[2]')
                    self.click_button('//td[@class="available today"]')
                    self.click_button('(//span[normalize-space(text())="26"])[2]')
                else:
                    self.click_button('//li[span[text()="间隔执行"]]')
                    self.click_button('(//input[@placeholder="开始日期"])[2]')
                    self.click_button('//td[@class="available today"]')
                    self.click_button('(//span[normalize-space(text())="26"])[2]')
                    self.click_button('//div[@class="el-picker-panel__footer"]/button[2]')

            elif frequency == "周":
                self.click_button(f'//li[span[text()="{frequency}"]]')
                sleep(1)
                if time:
                    self.click_button('//div[label[text()="按周"]]/div//i[@class="el-select__caret el-input__icon el-icon-arrow-up"]')
                    self.click_button('//li[span[text()="星期三"]]')
                    self.click_button('//div[label[text()="按周"]]/div//i[@class="el-select__caret el-input__icon el-icon-arrow-up is-reverse"]')
            elif frequency == "月":
                self.click_button(f'//li[span[text()="{frequency}"]]')
                if time:
                    self.click_button('//div[label[text()="按月"]]/div//i[@class="el-select__caret el-input__icon el-icon-arrow-up"]')
                    self.click_button('//li[span[text()="3"]]')
                    self.click_button('//div[label[text()="按月"]]/div//i[@class="el-select__caret el-input__icon el-icon-arrow-up is-reverse"]')

    def select_all(self, affairs="", enable="", process="", button: bool = True):
        """查询所有."""
        if affairs:
            self.click_button('//div[label[text()="流程事务:"]]//input')
            self.click_button(f'//li[@class="el-select-dropdown__item"]//span[text()="{affairs}"]')
        if enable:
            self.click_button('//div[label[text()="是否启用:"]]//input')
            if enable == "全部":
                self.click_button(f'(//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{enable}"])[2]')
            else:
                self.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{enable}"]')
        if process:
            self.enter_texts('//div[label[text()="流程名称:"]]//input[not(@placeholder="请输入流程名称")]', process)
        sleep(1)
        if button:
            self.click_button(f'(//button[span[text()="筛选"]])[1]')
        else:
            self.click_button(f'(//button[span[text()="重置筛选条件"]])[1]')

    def click_paging(self, num):
        """点击分页."""
        self.click_button('//div[@class="el-select el-select--mini"]//input')
        self.click_button(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]//span[text()="{num}条/页"]')

    def get_log_time(self):
        """获取日志时间."""
        time1 = self.get_find_element_xpath('(//table[@class="el-table__body"])[2]//tr[2]/td[5]').text
        time2 = self.get_find_element_xpath('(//table[@class="el-table__body"])[2]//tr[4]/td[5]').text
        # 解析原始字符串
        dt1 = datetime.strptime(time1, "%Y/%m/%d %H:%M:%S")
        dt2 = datetime.strptime(time2, "%Y/%m/%d %H:%M:%S")
        # 格式化为新字符串
        formatted_date1 = dt1.strftime("%Y-%m-%d")
        formatted_date2 = dt2.strftime("%Y-%m-%d")
        return formatted_date1, formatted_date2

    def sel_log_all(self, time1="", time2="", ptype="", pid="", pname="", affairs_name="", button: bool = True):
        """查询所有."""
        if time1:
            if len(time1) > 10:
                self.click_button('(//input[@placeholder="开始日期"])[1]')
                self.enter_texts('(//input[@placeholder="开始日期"])[2]', time1)
                self.enter_texts('//input[@placeholder="开始时间"]', time2)
                self.enter_texts('(//input[@placeholder="结束日期"])[2]', time1)
                self.enter_texts('//input[@placeholder="结束时间"]', time2)
                self.click_button('//div[@class="el-picker-panel__footer"]/button[2]')
            else:
                self.click_button('(//input[@placeholder="开始日期"])[1]')
                self.enter_texts('(//input[@placeholder="开始日期"])[2]', time2)
                self.enter_texts('//input[@placeholder="开始时间"]', "00:00:00")
                self.enter_texts('(//input[@placeholder="结束日期"])[2]', time1)
                self.enter_texts('//input[@placeholder="结束时间"]', "00:00:00")
                self.click_button('//div[@class="el-picker-panel__footer"]/button[2]')
        if ptype:
            self.click_button('//div[label[text()="执行状态:"]]//input')
            self.click_button(f'//li[span[text()="{ptype}"]]')
        if pid:
            self.enter_texts('//input[@placeholder="请输入流程ID"]', pid)
        if pname:
            self.enter_texts('//input[@placeholder="请输入流程名称"]', pname)
        if affairs_name:
            self.click_button('//div[label[text()="事务:"]]//input')
            self.click_button(f'//li[div/span[text()="{affairs_name}"]]')
        if button:
            self.click_button(f'(//button[span[text()="筛选"]])[2]')
        else:
            self.click_button(f'(//button[span[text()="重置筛选条件"]])[2]')
        sleep(3)