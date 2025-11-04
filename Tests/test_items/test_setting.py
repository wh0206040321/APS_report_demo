import logging
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.setting_page import SettingPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_setting():
    driver = None
    try:
        """初始化并返回 driver"""
        date_driver = DateDriver()
        # 初始化 driver
        driver = create_driver(date_driver.driver_path)
        driver.implicitly_wait(3)

        # 初始化登录页面
        page = LoginPage(driver)  # 初始化登录页面
        url = date_driver.url
        print(f"[INFO] 正在导航到 URL: {url}")
        # 尝试访问 URL，捕获连接错误
        for attempt in range(2):
            try:
                page.navigate_to(url)
                break
            except WebDriverException as e:
                capture_screenshot(driver, f"login_fail_{attempt + 1}")
                logging.warning(f"第 {attempt + 1} 次连接失败: {e}")
                driver.refresh()
                sleep(date_driver.URL_RETRY_WAIT)
        else:
            logging.error("连接失败多次，测试中止")
            safe_quit(driver)
            raise RuntimeError("无法连接到登录页面")

        page.login(date_driver.username, date_driver.password, date_driver.planning)
        page.click_button('(//span[text()="计划管理"])[1]')  # 点击计划管理
        page.click_button('(//span[text()="计划基础数据"])[1]')  # 点击计划基础数据
        page.click_button('(//span[text()="物品"])[1]')  # 点击物品
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("标准应用设置测试用例")
@pytest.mark.run(order=25)
class TestSettingPage:
    @allure.story("不填写布局名称，添加失败")
    # @pytest.mark.run(order=1)
    def test_setting_addfail1(self, login_to_setting):
        driver = login_to_setting
        setting = SettingPage(driver)

        # 调用 add_layout 方法，用于添加布局
        setting.add_layout()

        # 点击特定的按钮，这里的 XPath 表达式用于定位页面上的按钮
        setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

        # 获取页面上的提示信息，用于后续的断言验证
        message = setting.get_error_message()

        # 断言提示信息是否与预期相符，以验证功能的正确性
        assert message == "请输入布局名称"
        assert not setting.has_fail_message()

    @allure.story("填写布局名称，不勾选可见字段，添加失败")
    # @pytest.mark.run(order=1)
    def test_setting_addfail2(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.add_layout()
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', "测试布局A"
        )
        setting.click_button('//div[text()=" 显示设置 "]')
        # 获取是否可见选项的复选框元素
        checkbox = setting.get_find_element_xpath(
            '//div[./div[text()="是否可见:"]]/label/span'
        )

        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，直接点击确认按钮，进行下一步操作
            setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        else:
            # 如果已选中，先取消选择，再点击确认按钮
            setting.click_button('//div[./div[text()="是否可见:"]]/label/span/span')
            setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

        # 获取操作后的提示信息元素
        message = setting.get_error_message()

        # 断言提示信息是否符合预期，以验证操作是否成功
        assert message == "请勾选可见字段"
        assert not setting.has_fail_message()

    @allure.story("添加布局成功")
    # @pytest.mark.run(order=1)
    def test_setting_addsuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.add_layout_ok(layout)

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        # 断言布局名称与预期相符
        assert name == layout
        assert not setting.has_fail_message()

    @allure.story("添加测试布局重复，添加失败")
    # @pytest.mark.run(order=1)
    def test_setting_addrepeat(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.add_layout_ok(layout)

        # 获取设置后的提示信息
        message = setting.get_error_message()
        # 断言提示信息是否符合预期，以验证设置是否生效
        assert message == "布局名称已存在，请重新输入"
        assert not setting.has_fail_message()

    @allure.story("删除布局成功")
    # @pytest.mark.run(order=1)
    def test_setting_deletelayout(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.del_layout(layout)

        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        # 断言目标 div 已经被成功删除
        assert len(after_layout) == 0
        assert not setting.has_fail_message()

    @allure.story("添加透视表布局-不添加名称 添加失败")
    # @pytest.mark.run(order=1)
    def test_setting_addtablefail1(self, login_to_setting):
        driver = login_to_setting
        setting = SettingPage(driver)

        # 调用 add_pivot_table 方法，用于添加布局
        setting.add_pivot_table()

        # 点击特定的按钮，这里的 XPath 表达式用于定位页面上的按钮
        setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')

        # 获取页面上的提示信息，用于后续的断言验证
        message = setting.get_error_message()

        # 断言提示信息是否与预期相符，以验证功能的正确性
        assert message == "请输入布局名称"
        assert not setting.has_fail_message()

    @allure.story("添加透视表布局-添加名称点击确定 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_addtable1(self, login_to_setting):
        driver = login_to_setting
        setting = SettingPage(driver)
        layout = "测试透视表A"
        # 调用 add_pivot_table 方法，用于添加布局
        setting.add_pivot_table()

        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        # 点击特定的按钮，这里的 XPath 表达式用于定位页面上的按钮
        setting.click_confirm_button()

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        # 断言布局名称与预期相符
        assert name == layout
        assert not setting.has_fail_message()

    @allure.story("添加透视表布局-添加名称添加显示设置 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_addtable2(self, login_to_setting):
        driver = login_to_setting
        setting = SettingPage(driver)
        layout = "测试透视表B"
        # 调用 add_pivot_table 方法，用于添加布局
        setting.add_pivot_table()
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )

        setting.click_button('//div[text()=" 显示设置 "]')
        # 定义文本元素和目标输入框的 XPath
        text_elements = [
            '//div[span[text()=" code(物料代码) "]]',
            '//div[span[text()=" name(物料名称) "]]',
            '//div[span[text()=" type(物料种类) "]]',
        ]

        input_elements = [
            '(//div[@class="axis"])[1]',
            '(//div[@class="axis"])[2]',
            '(//div[@class="axis"])[3]',
        ]

        # 使用循环进行拖放操作
        for text_xpath, input_xpath in zip(text_elements, input_elements):
            text_element = setting.get_find_element_xpath(text_xpath)
            input_element = setting.get_find_element_xpath(input_xpath)
            ActionChains(driver).drag_and_drop(text_element, input_element).perform()

        sleep(2)
        setting.click_confirm_button()

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        table = setting.get_find_element_xpath(
            '//tr[@class="vxe-header--row" and .//span[text()="物料代码"]]/th[2]//span'
        ).text
        # 断言布局名称与预期相符
        assert name == layout and table == "物料代码"
        assert not setting.has_fail_message()

    @allure.story("删除透视表布局成功")
    # @pytest.mark.run(order=1)
    def test_setting_deletetable(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试透视表A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.del_layout(layout)

        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        # 断言目标 div 已经被成功删除
        assert len(after_layout) == 0
        assert not setting.has_fail_message()

    @allure.story("添加测试布局成功")
    # @pytest.mark.run(order=1)
    def test_setting_addsuccess1(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.add_layout()
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        setting.click_button('//div[text()=" 显示设置 "]')
        # 获取是否可见选项的复选框元素
        checkbox = setting.get_find_element_xpath(
            '//div[./div[text()="是否可见:"]]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button('//div[./div[text()="是否可见:"]]/label/span/span')
            # 点击确定按钮保存设置
            setting.click_confirm_button()
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_confirm_button()

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        # 断言布局名称与预期相符
        assert name == layout
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置为不显示布局")
    # @pytest.mark.run(order=1)
    def test_setting_notdisplay(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_setting_button()
        checkbox = setting.get_find_element_xpath(
            '//div[text()="是否显示布局:"]/following-sibling::label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 点击确定按钮保存设置
            setting.click_confirm_button()
        else:
            # 如果已选中，点击取消选中
            setting.click_button(
                '//div[text()="是否显示布局:"]/following-sibling::label/span'
            )
            sleep(1)
            setting.click_confirm_button()

        setting.click_ref_button()
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert name.get_attribute("style") == "display: none;"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-布局列表设置为显示布局")
    # @pytest.mark.run(order=1)
    def test_setting_display(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        sleep(1)

        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)

        setting.click_button(f'(//span[text()=" 在导航中显示布局 "])[{index + 1}]')
        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        setting.get_find_message()
        setting.wait_for_loading_to_disappear()
        sleep(1)
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert name.text == layout
        assert not setting.has_fail_message()

    @allure.story("设置表格布局默认启动-成功")
    # @pytest.mark.run(order=1)
    def test_setting_default_start_success(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_setting_button()
        checkbox = setting.get_find_element_xpath(
            '//div[text()="是否默认启动:"]/following-sibling::label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button(
                '//div[text()="是否默认启动:"]/following-sibling::label/span'
            )
            sleep(1)
            # 点击确定按钮保存设置
            setting.click_confirm_button()
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_confirm_button()

        sleep(1)
        safe_quit(driver)
        # 重新打开浏览器
        driver_path = DateDriver().driver_path
        driver = create_driver(driver_path)
        driver.implicitly_wait(3)

        # 重新登录并进入目标页面
        page = LoginPage(driver)
        page.navigate_to(DateDriver().url)
        page.login(DateDriver().username, DateDriver().password, DateDriver().planning)
        # 用新 driver 初始化 SettingPage
        setting = SettingPage(driver)
        layout = "测试布局A"
        page.click_button('(//span[text()="计划管理"])[1]')
        page.click_button('(//span[text()="计划基础数据"])[1]')
        page.click_button('(//span[text()="物品"])[1]')

        sleep(2)
        div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).get_attribute("class")
        assert div == "tabsDivItem tabsDivActive"
        assert not setting.has_fail_message()
        safe_quit(driver)

    @allure.story("设置表格布局-表尾内容设置为合计")
    # @pytest.mark.run(order=1)
    def test_setting_total(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_setting_button()
        setting.click_button('//div[text()="表尾内容:"]/following-sibling::div//i')
        setting.click_button('//div[text()="合计"]')
        setting.click_confirm_button()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        name = setting.get_find_element_xpath('(//span[text()="合计"])[2]').text
        assert name == "合计"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-表尾内容设置为平均")
    # @pytest.mark.run(order=1)
    def test_setting_average(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_setting_button()
        setting.click_button('//div[text()="表尾内容:"]/following-sibling::div//i')
        setting.click_button('//div[text()="平均"]')
        setting.click_confirm_button()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        name = setting.get_find_element_xpath('(//span[text()="平均"])[2]').text
        assert name == "平均"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置一页显示数据为5")
    # @pytest.mark.run(order=1)
    def test_setting_displaynum1(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_setting_button()
        num = 5
        inupt_number = setting.get_find_element_xpath(
            '//div[text()="一页显示条数:"]/following-sibling::div//input'
        )
        inupt_number.send_keys(Keys.CONTROL, "a")
        inupt_number.send_keys(Keys.DELETE)
        inupt_number.send_keys(f"{num}")
        setting.click_confirm_button()
        sleep(1)
        tr_text = driver.find_elements(
            By.XPATH,
            f'//div[@class="vxe-table--body-wrapper body--wrapper" and @xid="2"]/table//tr[{num}]',
        )
        tr_none = driver.find_elements(
            By.XPATH,
            f'//div[@class="vxe-table--body-wrapper body--wrapper" and @xid="2"]/table//tr[{num+1}]',
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        nums = setting.get_find_element_xpath(
            '//span[@class="vxe-pager--btn-wrapper"]/button[last()]'
        ).text
        total_records = setting.get_find_element_xpath(
            "//span[contains(text(),'共') and contains(text(),'条记录')]"
        ).text
        total_number = int(
            total_records.replace("共", "").replace("条记录", "").strip()
        )
        if int(total_number) % num != 0:  # 如果有余数
            result = (int(total_number) // num) + 1  # 商加一（向上取整）
        else:  # 如果刚好整除
            result = int(total_number) // num  # 直接使用商

        if num <= total_number:
            assert len(tr_text) == 1 and len(tr_none) == 0 and result == int(nums)
        else:
            assert len(tr_text) == 0 and len(tr_none) == 0 and result == int(nums)
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置一页显示数据为50000")
    # @pytest.mark.run(order=1)
    def test_setting_displaynum2(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        # 设置每页显示的记录数为50000条
        num = 50000
        # 点击布局选项卡
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        # 点击设置按钮
        setting.click_setting_button()
        # 找到输入每页显示条数的输入框
        inupt_number = setting.get_find_element_xpath(
            '//div[text()="一页显示条数:"]/following-sibling::div//input'
        )
        # 选中输入框中的文本
        inupt_number.send_keys(Keys.CONTROL, "a")
        # 删除输入框中的文本
        inupt_number.send_keys(Keys.DELETE)
        # 输入新的每页显示条数
        inupt_number.send_keys(f"{num}")
        # 点击确定按钮保存设置
        setting.click_confirm_button()
        # 滚动到页面底部以加载所有元素
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 等待1秒以确保页面滚动完成
        sleep(1.5)
        # 获取分页数字
        nums = setting.get_find_element_xpath(
            '//span[@class="vxe-pager--btn-wrapper"]/button[last()]'
        ).text
        # 获取总记录数的文本
        total_records = setting.get_find_element_xpath(
            "//span[contains(text(),'共') and contains(text(),'条记录')]"
        ).text
        # 提取总记录数并转换为整数
        total_number = int(
            total_records.replace("共", "").replace("条记录", "").strip()
        )
        # 计算总页数，如果总记录数除以每页记录数有余数，则总页数为商加一，否则总页数为商
        if int(total_number) % num != 0:  # 如果有余数
            result = (int(total_number) // num) + 1  # 商加一（向上取整）
        else:  # 如果刚好整除
            result = int(total_number) // num  # 直接使用商

        # 断言计算的总页数与页面显示的最后一页数字一致
        assert result == int(nums)
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置物料名称为不可见")
    # @pytest.mark.run(order=1)
    def test_setting_display1(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        after_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[3]//p'
        ).text
        setting.click_setting_button()
        # 点击显示设置按钮以展开设置选项
        setting.click_button('//div[text()=" 显示设置 "]')

        # 定位到物料名称对应的复选框
        checkbox = setting.get_find_element_xpath(
            '//tr[./td[3] and ./td[.//span[text()="物料名称"]]]/td[6]//span[1]'
        )
        sleep(2)
        # 检查复选框是否已被选中
        if checkbox.get_attribute("class") == "ivu-checkbox ivu-checkbox-checked":
            # 如果复选框选中，则点击取消选中，并保存设置
            checkbox.click()
            setting.click_confirm_button()
        else:
            # 如果复选框未选中，则直接保存设置
            setting.click_confirm_button()
        sleep(1)
        # 获取设置更改后的物料代码列文本
        before_text = driver.find_elements(
            By.XPATH, '//table[.//th[.//p[text()="物料代码"]]]//th//p'
        )
        before_texts = [elem.text.strip() for elem in before_text]
        # 断言设置更改后，after_text 不再存在于 before_text 中
        assert after_text not in before_texts and after_text == "物料名称"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置物料名称为可见")
    # @pytest.mark.run(order=1)
    def test_setting_display2(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        sleep(1)
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        # 查找包含物料代码的表格，并获取相关文本
        after_text = driver.find_elements(
            By.XPATH, '//table[.//th[.//p[text()="物料代码"]]]//th//p'
        )
        after_texts = [elem.text.strip() for elem in after_text]
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        ele = setting.get_find_element_xpath('(//div[@class="vxe-table--body-wrapper body--wrapper"])[4]')
        setting.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", ele)
        # 定位到物料名称对应的复选框
        checkbox = setting.get_find_element_xpath(
            '//tr[./td[3] and ./td[.//span[text()="物料名称"]]]/td[6]//span[1]'
        )
        xpath = '//tr[./td[3] and ./td[.//span[text()="物料名称"]]]/td[7]//input'
        ele = setting.get_find_element_xpath(xpath)
        # 检查复选框是否已被选中
        if checkbox.get_attribute("class") == "ivu-checkbox ivu-checkbox-checked":
            # 如果已选中，直接点击确认按钮
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.DELETE)
            setting.enter_texts(xpath, '2')
            setting.click_confirm_button()
        else:
            # 如果未选中，点击复选框并确认
            checkbox.click()
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.DELETE)
            setting.enter_texts(xpath, '2')
            setting.click_confirm_button()
        sleep(1)
        # 获取设置更改后的物料代码相关文本
        before_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[3]//p'
        ).text
        # 断言更改后的设置在之前获取的文本中存在
        assert before_text not in after_texts and before_text == "物料名称"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置物料组代码自定义显示为测试物料组代码")
    # @pytest.mark.run(order=1)
    def test_setting_display3(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        # 查找包含物料代码的表格，并获取相关文本
        after_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[4]//p'
        ).text
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        input_text = setting.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="物料组代码"]]]/td[4]//input'
        )
        input_text.send_keys(Keys.CONTROL, "a")
        input_text.send_keys(Keys.DELETE)
        input_text.send_keys("测试物料组代码")

        setting.click_confirm_button()
        before_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[4]//p'
        ).text
        assert before_text != after_text and before_text == "测试物料组代码"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置物料组代码自定义显示改为之前的值")
    # @pytest.mark.run(order=1)
    def test_setting_display4(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        # 查找包含物料代码的表格，并获取相关文本
        after_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[4]//p'
        ).text
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        input_text = setting.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="物料组代码"]]]/td[4]//input'
        )
        input_text.send_keys(Keys.CONTROL, "a")
        input_text.send_keys(Keys.DELETE)

        setting.click_confirm_button()
        before_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[4]//p'
        ).text
        assert before_text != after_text and before_text == "物料组代码"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-设置物料优先度表尾内容为求和")
    # @pytest.mark.run(order=1)
    def test_setting_display5(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()="表尾内容:"]/following-sibling::div//i')
        setting.click_button('//div[text()="列设置"]')
        setting.click_button('//div[text()=" 显示设置 "]')
        setting.click_button('//tr[./td[3][.//span[text()="物料优先度"]]]/td[5]//input')
        setting.click_button('//div[text()="求和"]')
        setting.click_confirm_button()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        text1 = setting.get_find_element_xpath(
            '(//tr[.//span[text()="合计"]])[2]/td[1]//span'
        ).text
        text2 = setting.get_find_element_xpath(
            '//tr[.//span[text()="合计"]]/td[6]//span'
        ).text
        assert text1 == "合计" and text2 != "-"
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-改变关联条件列的顺序")
    # @pytest.mark.run(order=1)
    def test_setting_display6(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        after_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[10]//p'
        ).text
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        num = setting.get_find_element_xpath(
            '//tr[./td[3][.//span[text()="关联条件"]]]/td[7]//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.DELETE)
        num.send_keys("8")
        setting.click_confirm_button()
        sleep(1)
        before_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[9]//p'
        ).text
        assert before_text == after_text
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-把顺序修改回来")
    # @pytest.mark.run(order=1)
    def test_setting_display7(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        after_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[10]//p'
        ).text
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        num = setting.get_find_element_xpath(
            f'//tr[./td[3][.//span[text()="{after_text}"]]]/td[7]//input'
        )
        num.send_keys(Keys.CONTROL, "a")
        num.send_keys(Keys.DELETE)
        num.send_keys("8")
        setting.click_confirm_button()
        sleep(1)
        before_text = setting.get_find_element_xpath(
            '//table[.//th[.//p[text()="物料代码"]]]//th[9]//p'
        ).text
        assert before_text == after_text
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-物料代码快速查询-输入框")
    # @pytest.mark.run(order=1)
    def test_setting_select_input(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        code = "物料代码"
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        # 点击快速查询按钮以开始搜索
        setting.click_button('//div[text()=" 快速查询 "]')

        # 根据提供的code点击对应的行按钮，以展开详细信息
        setting.click_button(
            f'//tr[./td[3][.//span[text()="{code}"]]]/td[4]//input[@placeholder="请选择"]'
        )

        # 点击输入框，准备输入数据
        setting.click_button('//div[text()="输入框"]')

        # 确认输入框点击，进入下一步
        setting.click_confirm_button()

        # 获取表格中特定位置的数据，用于后续的验证
        data = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[2]'
        ).text

        # 等待界面更新，确保数据被正确处理
        sleep(1)

        # 在界面上输入之前获取的数据，以进行验证
        setting.enter_texts(
            f'//div[text()="{code}"]/following-sibling::div//input', f"{data}"
        )

        # 点击查询按钮，提交输入的数据
        setting.click_button('//div[@class="queryBtn"]/button[1]')

        # 等待查询结果出现
        sleep(1)

        # 获取查询结果中的第一条数据，用于验证
        text1 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[1]/td[2]'
        ).text

        # 再次等待，确保所有数据都已加载
        sleep(1)

        # 获取查询结果中的第二条数据，用于进一步验证
        text2 = driver.find_elements(
            By.XPATH,
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[2]',
        )

        # 断言查询结果与之前获取的数据一致，且没有其他不相关数据
        assert text1 == data and text2 == []
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-物料优先度快速查询-数字输入框")
    # @pytest.mark.run(order=1)
    def test_setting_select_numinput(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        code = "物料优先度"
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        # 点击快速查询按钮，以展开查询选项
        setting.click_button('//div[text()=" 快速查询 "]')

        # 根据特定代码点击相应的行按钮，以选择特定的查询条件
        setting.click_button(
            f'//tr[./td[3][.//span[text()="{code}"]]]/td[4]//input[@placeholder="请选择"]'
        )

        # 点击数字输入框按钮，准备输入数值
        setting.click_button('//div[text()="数字输入框"]')

        # 确认数字输入框的弹窗，以应用所选条件
        setting.click_confirm_button()

        # 在指定的输入框中输入特殊字符，以测试系统的稳定性和正确性
        setting.enter_texts(
            f'//div[text()="{code}"]/following-sibling::div//input', "q的 /?=-+0]>"
        )

        # 等待系统处理输入，确保数据被正确应用
        sleep(1)

        # 点击查询按钮，启动查询过程
        setting.click_button('//div[@class="queryBtn"]/button[1]')

        # 等待查询结果加载，确保数据展示正确
        sleep(1)

        # 获取查询结果中第一行的特定数据
        num1 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[1]/td[6]'
        ).text

        # 获取查询结果中第二行的特定数据
        num2 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[6]'
        ).text

        # 获取查询结果中第三行的特定数据
        num3 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[3]/td[6]'
        ).text

        # 断言查询结果中的数据均为0，以验证查询功能的准确性
        assert num1 == num2 == num3 and num1 == "0"
        assert not setting.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_setting_select_textverify(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        num = "111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.enter_texts(
            f'//div[text()="物料优先度"]/following-sibling::div//input', num
        )
        setting.enter_texts(
            f'//div[text()="物料代码"]/following-sibling::div//input', num
        )
        # 点击查询按钮，启动查询过程
        setting.click_button('//div[@class="queryBtn"]/button[1]')
        ele = setting.finds_elements(By.XPATH, '//div[@class="ivu-modal-body"]//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        assert len(ele) == 0
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-物料种类快速查询-下拉框")
    # @pytest.mark.run(order=1)
    def test_setting_select_seleinput(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        code = "物料种类"
        # 点击设置按钮，进入显示设置界面
        setting.click_setting_button()
        # 点击快速查询按钮
        setting.click_button('//div[text()=" 快速查询 "]')

        # 点击特定代码的行以选择
        setting.click_button(
            f'//tr[./td[3][.//span[text()="{code}"]]]/td[4]//input[@placeholder="请选择"]'
        )

        # 打开下拉框
        setting.click_button('//div[text()="下拉框"]')

        # 点击物料种类图标以展开选项
        setting.click_button(
            '//tr[./td[3][.//span[text()="物料种类"]]]/td[4]//i[@class="ivu-icon ivu-icon-md-albums"]'
        )

        # 选择表/视图选项
        setting.click_button('//div[text()="表/视图"]')

        # 输入并选择APS_Item
        setting.enter_texts(
            '//div[text()=" 表/视图 "]/following-sibling::div//input[@placeholder="请选择"]',
            "APS_Item",
        )
        setting.click_button('//li[text()="APS_Item "]')

        # 等待加载
        sleep(1)

        # 输入并选择Type
        setting.enter_texts(
            '//div[text()=" key "]/following-sibling::div//input[@placeholder="请选择"]',
            "Type",
        )
        setting.click_button('(//li[text()="Type"])[1]')

        # 等待加载
        sleep(1)

        # 再次输入并选择Type
        setting.enter_texts(
            '//div[text()=" name "]/following-sibling::div//input[@placeholder="请选择"]',
            "Type",
        )
        setting.click_button('(//li[text()="Type"])[2]')

        # 等待加载
        sleep(1)

        # 点击确定按钮
        setting.click_button(
            '(//div[@class="h-40px flex-justify-end flex-align-items-end b-t-s-d9e3f3"])[1]/button[1]'
        )

        # 点击确认按钮
        setting.click_confirm_button()

        # 为特定代码选择P选项
        setting.click_button(
            f'//div[text()="{code}"]/following-sibling::div//input[@placeholder="请选择"]'
        )
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="P"]')

        # 等待加载
        sleep(1)

        # 展开物料种类下拉框
        setting.click_button(
            '//div[text()="物料种类"]/following-sibling::div//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]'
        )

        # 点击查询按钮
        setting.click_button('//div[@class="queryBtn"]/button[1]')

        # 等待加载
        sleep(1)

        # 获取并记录P选项的结果
        Ptext1 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[1]/td[5]'
        ).text

        # 等待加载
        sleep(1)

        Ptext2 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[5]'
        ).text

        # 点击重置按钮
        setting.click_button('//div[@class="queryBtn"]/button[2]')

        # 为特定代码选择I选项
        setting.click_button(
            f'//div[text()="{code}"]/following-sibling::div//input[@placeholder="请选择"]'
        )
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="I"]')

        # 等待加载
        sleep(1)

        # 展开物料种类下拉框
        setting.click_button(
            '//div[text()="物料种类"]/following-sibling::div//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]'
        )

        # 点击查询按钮
        setting.click_button('//div[@class="queryBtn"]/button[1]')

        # 等待加载
        sleep(1)

        # 获取并记录I选项的结果
        Itext1 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[1]/td[5]'
        ).text

        # 等待加载
        sleep(1)

        Itext2 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[5]'
        ).text

        # 点击重置按钮
        setting.click_button('//div[@class="queryBtn"]/button[2]')

        # 为特定代码选择M选项
        setting.click_button(
            f'//div[text()="{code}"]/following-sibling::div//input[@placeholder="请选择"]'
        )
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="M"]')

        # 等待加载
        sleep(1)

        # 展开物料种类下拉框
        setting.click_button(
            '//div[text()="物料种类"]/following-sibling::div//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]'
        )

        # 点击查询按钮
        setting.click_button('//div[@class="queryBtn"]/button[1]')

        # 等待加载
        sleep(1)

        # 获取并记录M选项的结果
        Mtext1 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[1]/td[5]'
        ).text

        # 等待加载
        sleep(1)

        Mtext2 = setting.get_find_element_xpath(
            '(//div[@class="vxe-table--body-wrapper body--wrapper"])[2]/table//tr[2]/td[5]'
        ).text

        # 断言所有结果一致且符合预期
        assert (
            Ptext1 == Ptext2
            and Itext1 == Itext2
            and Mtext1 == Mtext2
            and Ptext1 == "完成品"
            and Itext1 == "中间品"
            and Mtext1 == "原材料"
        )
        assert not setting.has_fail_message()

    @allure.story("快速查询两个条件显示正确")
    # @pytest.mark.run(order=1)
    def test_setting_select_success(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.enter_texts(
            '//div[text()="物料优先度"]/following-sibling::div//input', "0"
        )
        # 为特定代码选择I选项
        setting.click_button(
            f'//div[text()="物料种类"]/following-sibling::div//input[@placeholder="请选择"]'
        )
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="I"]')
        sleep(1)
        # 展开物料种类下拉框
        setting.click_button(
            '//div[text()="物料种类"]/following-sibling::div//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]'
        )
        # 点击查询按钮
        setting.click_button('//div[@class="queryBtn"]/button[1]')
        sleep(2)

        # 获取所有行
        rows = driver.find_elements(By.XPATH, '(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr')
        row_count = len(rows)
        print(f"共找到 {row_count} 行")

        for i in range(row_count):
            try:
                td5_xpath = f'(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr[{i + 1}]/td[5]'
                td6_xpath = f'(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr[{i + 1}]/td[6]'

                td5 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, td5_xpath)))
                td6 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, td6_xpath)))

                value5 = td5.text.strip()
                value6 = td6.text.strip()

                assert value5 == "中间品", f"❌ 第 {i + 1} 行第5列不是中间品，而是：{value5}"
                assert value6 == "0", f"❌ 第 {i + 1} 行第6列不是0，而是：{value6}"

            except Exception as e:
                print(f"⚠️ 第 {i + 1} 行检查异常：{e}")
        assert not setting.has_fail_message()

    @allure.story("快速查询下拉框多选为或者关系")
    # @pytest.mark.run(order=1)
    def test_setting_select_selsuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.enter_texts(
            '//div[text()="物料优先度"]/following-sibling::div//input', "1"
        )
        # 为特定代码选择I选项
        setting.click_button(
            f'//div[text()="物料种类"]/following-sibling::div//input[@placeholder="请选择"]'
        )
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="I"]')
        sleep(1)
        setting.click_button('//ul[@class="ivu-select-dropdown-list"]/li[text()="M"]')
        sleep(1)
        # 展开物料种类下拉框
        setting.click_button(
            '//div[text()="物料种类"]/following-sibling::div//i[@class="ivu-icon ivu-icon-ios-arrow-down ivu-select-arrow"]'
        )
        # 点击查询按钮
        setting.click_button('//div[@class="queryBtn"]/button[1]')
        sleep(2)

        # 获取表格中所有行的元素，以便后续遍历
        rows = driver.find_elements(By.XPATH, '(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr')
        # 计算行数
        row_count = len(rows)

        # 遍历每一行
        for i in range(row_count):
            try:
                # 构建当前行第5列的XPath，并获取其文本内容
                td5_xpath = f'(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr[{i + 1}]/td[5]'
                value5 = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, td5_xpath))
                ).text.strip()

                # 如果第5列的值为“中间品”或“原材料”
                if value5 in ["中间品", "原材料"]:
                    # 构建当前行第6列的XPath，并获取其文本内容
                    td6_xpath = f'(//table[@xid="2" and contains(@class,"vxe-table--body")])[1]//tr[{i + 1}]/td[6]'
                    value6 = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, td6_xpath))
                    ).text.strip()

                    # 断言第6列的值应为“1”
                    assert value6 == "1"

                else:
                    # 如果第5列的值不是“中间品”或“原材料”，则跳过当前行
                    print(f"🟡 第 {i + 1} 行跳过：第5列值为「{value5}」")

            except Exception as e:
                # 如果在检查当前行时发生异常，使用pytest的fail方法记录错误
                pytest.fail(f"⚠️ 第 {i + 1} 行检查异常：{e}")
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-制造订单交货期查询-日期")
    # @pytest.mark.run(order=1)
    def test_setting_select_timeinput(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('(//span[text()="计划业务数据"])[1]')
        setting.click_button('(//span[text()="制造订单"])[1]')
        layout = "测试布局A"
        code = "交货期"
        sleep(1)
        setting.add_layout()
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        setting.click_button('(//div[text()=" 显示设置 "])[2]')
        # 获取是否可见选项的复选框元素
        checkbox = setting.get_find_element_xpath(
            '(//div[./div[text()="是否可见:"]])[2]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button('(//div[./div[text()="是否可见:"]])[2]/label/span')
            # 点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[5]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[5]/button[2]')

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text

        setting.click_setting_button()
        # 点击快速查询按钮
        setting.click_button('(//div[text()=" 快速查询 "])[2]')
        # 点击特定代码的行以选择
        setting.click_button(
            f'//tr[./td[3][.//span[text()="{code}"]]]/td[4]//input[@placeholder="请选择"]'
        )
        # 打开下拉框
        setting.click_button('//div[text()="日期"]')
        setting.click_button('(//div[@class="demo-drawer-footer"])[5]/button[2]')
        # 断言布局名称与预期相符
        time = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[2]/td[9]'
        ).text
        setting.enter_texts('//div[@class="ivu-date-picker-rel"]//input', time)
        setting.click_button('//div[@class="queryBtn"]/button[1]')
        sleep(1)
        after_time = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[1]/td[9]'
        ).text

        assert name == layout and time == after_time
        assert not setting.has_fail_message()

    @allure.story("设置表格布局-制造订单交货期查询-日期范围")
    # @pytest.mark.run(order=1)
    def test_setting_select_dateinput(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('(//span[text()="计划业务数据"])[1]')
        setting.click_button('(//span[text()="制造订单"])[1]')
        layout = "测试布局A"
        code = "交货期"
        sleep(1)
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_setting_button()
        # 点击快速查询按钮
        setting.click_button('(//div[text()=" 快速查询 "])[2]')
        # 点击特定代码的行以选择
        setting.click_button(
            f'//tr[./td[3][.//span[text()="{code}"]]]/td[4]//input[@placeholder="请选择"]'
        )
        # 打开下拉框
        setting.click_button('//div[text()="日期范围"]')
        setting.click_button('(//div[@class="demo-drawer-footer"])[5]/button[2]')
        time1 = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[2]/td[9]'
        ).text
        sleep(1)
        setting.click_button('//p[text()="交货期"]/following-sibling::div[1]')
        time2 = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[2]/td[9]'
        ).text
        if time1 > time2:
            time = time2 + " - " + time1
        else:
            time = time1 + " - " + time2
        print(time)
        setting.enter_texts('//div[@class="ivu-date-picker-rel"]//input', time)
        setting.click_button('//div[@class="queryBtn"]/button[1]')
        sleep(1)
        after_time1 = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[1]/td[9]'
        ).text
        after_time2 = setting.get_find_element_xpath(
            '//div[@class="single-page"]//table[@class="vxe-table--body" and .//tr[@class="vxe-body--row"]]//tr[2]/td[9]'
        ).text

        # 删除导航栏物品页面
        setting.click_button(
            '//div[@class="scroll-body" and .//div[text()=" 物品 "]]//div[./div[text()=" 物品 "]]'
        )
        setting.click_button(
            '//div[@class="scroll-body" and .//div[text()=" 物品 "]]//div[./div[text()=" 物品 "]]/span'
        )
        sleep(1)
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）

        setting.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        # 等待一段时间，确保删除操作完成
        sleep(1)

        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 确保时间顺序的正确性和布局状态的正确性
        assert (
            time1 >= after_time1 >= time2
            and time1 >= after_time2 >= time2
            and len(after_layout) == 0
        )
        assert not setting.has_fail_message()

    @allure.story("设置透视表格布局-设置为不显示布局")
    # @pytest.mark.run(order=1)
    def test_setting_perspective_notdisplay(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试透视表B"
        sleep(1)
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_setting_button()
        checkbox = setting.get_find_element_xpath(
            '//div[text()="是否显示布局:"]/following-sibling::label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 点击确定按钮保存设置
            setting.click_confirm_button()
            sleep(1)
        else:
            # 如果已选中，点击取消选中
            setting.click_button(
                '//div[text()="是否显示布局:"]/following-sibling::label/span'
            )
            sleep(1)
            setting.click_confirm_button()
        sleep(2)
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert name.get_attribute("style") == "display: none;"
        assert not setting.has_fail_message()

    @allure.story("设置透视表格布局-布局列表设置为显示布局")
    # @pytest.mark.run(order=1)
    def test_setting_perspective_display(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试透视表B"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')

        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        xpath = f'(//i[@class="el-icon-more layoutListDropdown"])[{index + 1}]'
        setting.hover(layout)

        setting.click_button(f'(//span[text()=" 在导航中显示布局 "])[{index + 1}]')
        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert name.text == layout
        assert not setting.has_fail_message()

    @allure.story("设置透视表格布局默认启动-成功")
    # @pytest.mark.run(order=1)
    def test_setting_perspective_start_success(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试透视表B"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_setting_button()
        checkbox = setting.get_find_element_xpath(
            '//div[text()="是否默认启动:"]/following-sibling::label/span'
        )

        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button(
                '//div[text()="是否默认启动:"]/following-sibling::label/span'
            )
            sleep(1)
            # 点击确定按钮保存设置
            setting.click_confirm_button()
            sleep(1)
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_confirm_button()

        sleep(2)
        safe_quit(driver)
        # 重新打开浏览器
        driver_path = DateDriver().driver_path
        driver = create_driver(driver_path)
        driver.implicitly_wait(3)

        # 重新登录并进入目标页面
        page = LoginPage(driver)
        page.navigate_to(DateDriver().url)
        page.login(DateDriver().username, DateDriver().password, DateDriver().planning)
        # 用新 driver 初始化 SettingPage
        setting = SettingPage(driver)
        layout = "测试透视表B"
        page.click_button('(//span[text()="计划管理"])[1]')
        page.click_button('(//span[text()="计划基础数据"])[1]')
        page.click_button('(//span[text()="物品"])[1]')

        div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).get_attribute("class")
        assert div == "tabsDivItem tabsDivActive"
        assert not setting.has_fail_message()
        safe_quit(driver)

    @allure.story("删除透视表布局成功")
    # @pytest.mark.run(order=1)
    def test_setting_deleteperspective(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试透视表B"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）

        sleep(2)
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        # 等待一段时间，确保删除操作完成
        sleep(1)

        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        # 断言目标 div 已经被成功删除
        assert len(after_layout) == 0
        assert not setting.has_fail_message()

    @allure.story("添加统计图 不输入图表名 点击确认 不允许添加")
    # @pytest.mark.run(order=1)
    def test_setting_statisticsfail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=1)
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        message = setting.get_error_message()
        assert message == "请输入图表名称"
        assert not setting.has_fail_message()

    @allure.story("添加统计图 输入图表名 点击确认 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success1(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图1"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=1, name=statistics)
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath('//div[@class="statisticalListItemTitle"]/span').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("在测试布局A添加的统计图，显示在布局A，也显示在其他布局中")
    # @pytest.mark.run(order=1)
    def test_setting_statistics(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局B"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" 测试布局A "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        ele = setting.get_find_element_xpath('//div[@class="statisticalListItemTitle"]/span').text
        # 刷新当前页面
        driver.refresh()
        sleep(1)
        setting.add_layout()
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        setting.click_button('//div[text()=" 显示设置 "]')
        # 获取是否可见选项的复选框元素
        checkbox = setting.get_find_element_xpath(
            '//div[./div[text()="是否可见:"]]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button('//div[./div[text()="是否可见:"]]/label/span/span')
            # 点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')

        # 获取布局名称的文本元素
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        sleep(1)
        eles = driver.find_elements(By.XPATH, '//div[.//span[text()="统计图1 "] and @class="statisticalListItemTitle"]')
        assert len(eles) == 1 and ele == "统计图1 (数据源:测试布局A)" and name == layout
        assert not setting.has_fail_message()

    @allure.story("添加柱状统计图 输入图表名 输入XY轴 点击确认 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success2(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图2"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=1, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加柱状统计图 输入图表名 输入Y轴 分组 点击确认 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success3(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图3"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=1, name=statistics, code2="物料优先度 (itemPriority)", code3="物料种类 (type)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        ele = setting.get_find_element_xpath(f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]')
        setting.driver.execute_script("arguments[0].scrollIntoView();", ele)
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加柱状统计图 切换数据源 点击确认 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success4(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局B"
        statistics = "统计图4"
        setting.click_button('//div[@class="tabsDivItemCon"]/div[text()=" 测试布局A "]')
        setting.add_statistics(num=1, data=layout, name=statistics, code2="物料优先度 (itemPriority)", code3="物料种类 (type)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加柱状统计图 输入重复的表名 点击确认 添加失败")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_fail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图4"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=1, name=statistics, code2="物料优先度 (itemPriority)", code3="物料种类 (type)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        message = setting.get_error_message()
        assert message == "记录已存在,请检查！"
        assert not setting.has_fail_message()

    @allure.story("添加折线统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success5(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图5"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=2, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加饼状统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success6(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图6"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=3, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加散点统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success7(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图7"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=4, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加仪表盘统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success8(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图8"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=5, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加双轴统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success9(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图9"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=6, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加面积统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success10(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图10"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=7, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加漏斗统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success11(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图11"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=8, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("添加雷达统计图 添加成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_success12(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图12"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_statistics(num=9, name=statistics, code1="物料种类 (type)", code2="物料优先度 (itemPriority)")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("修改统计图名称重复，修改失败")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_updaterepeat(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        setting.wait_for_el_loading_mask()

        element = driver.find_element(By.XPATH, '//span[text()="统计图1 "]/following-sibling::div')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        sleep(1)
        # 点击三个点
        setting.click_button('//span[text()="统计图1 "]/following-sibling::div')
        # 点击设置
        setting.click_button('//span[text()="统计图1 "]/following-sibling::div//div[text()="设置"]')
        ele = setting.get_find_element_xpath('(//input[@placeholder="请输入" and @class="ivu-input ivu-input-default"])[1]')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        setting.enter_texts('(//input[@placeholder="请输入" and @class="ivu-input ivu-input-default"])[1]', "统计图2")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        message = setting.get_error_message()
        assert message == "记录已存在,请检查！"
        assert not setting.has_fail_message()

    @allure.story("修改统计图名称成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_updatesuceess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        statistics = "统计图13"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        setting.wait_for_el_loading_mask()
        element = driver.find_element(By.XPATH, '//span[text()="统计图1 "]/following-sibling::div')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        sleep(1)
        # 点击三个点
        setting.click_button('//span[text()="统计图1 "]/following-sibling::div')
        # 点击设置
        setting.click_button('//span[text()="统计图1 "]/following-sibling::div//div[text()="设置"]')
        ele = setting.get_find_element_xpath(
            '(//input[@placeholder="请输入" and @class="ivu-input ivu-input-default"])[1]')
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        setting.enter_texts('(//input[@placeholder="请输入" and @class="ivu-input ivu-input-default"])[1]', f"{statistics}")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        name = setting.get_find_element_xpath(
            f'//div[@class="statisticalListItemTitle"]/span[contains(text(),"{statistics}")]').text
        assert name == f"{statistics} "f"(数据源:{layout})"
        assert not setting.has_fail_message()

    @allure.story("循环删除统计数据成功")
    # @pytest.mark.run(order=1)
    def test_setting_statistics_deletesuceess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        i = 1
        while i <= 13:
            try:
                element = driver.find_element(By.XPATH, f'//span[text()="统计图{i} "]/following-sibling::div')
                driver.execute_script("arguments[0].scrollIntoView();", element)

                # 点击三个点
                setting.click_button(f'//span[text()="统计图{i} "]/following-sibling::div')
                # 点击刪除
                setting.click_button(f'//span[text()="统计图{i} "]/following-sibling::div//li[text()="删除"]')
                # 确认删除
                setting.click_button(
                    '//div[@class="ivu-modal-confirm-footer"]/button[@class="ivu-btn ivu-btn-primary"]')
                sleep(3)
            except NoSuchElementException:
                print(f"统计图{i} 不存在，跳过")
            finally:
                i += 1

        sleep(3)
        driver.refresh()
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[4]//i')
        ele = driver.find_elements(By.XPATH, '//div[@class="statisticalListItemTitle"]/span[contains(text(),"统计图")]')
        assert len(ele) == 0
        assert not setting.has_fail_message()

    @allure.story("标签列表不添加名称不允许添加")
    # @pytest.mark.run(order=1)
    def test_setting_label_fail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_lable()
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        message = setting.get_error_message()
        assert message == "标签名不能为空"
        assert not setting.has_fail_message()

    @allure.story("标签列表添加名称成功")
    # @pytest.mark.run(order=1)
    def test_setting_label_addsuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_lable("标签1")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        ele = driver.find_elements(By.XPATH, '//div[@class="labelItem"]')
        sleep(1)
        assert any("标签1" in element.text for element in ele), "没有找到包含'标签1'的标签项"
        assert not setting.has_fail_message()

    @allure.story("添加测试标签")
    # @pytest.mark.run(order=1)
    def test_setting_label_testsuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.add_lable("标签2")
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        ele = driver.find_elements(By.XPATH, '//div[@class="labelItem"]')
        sleep(1)
        assert any("标签2" in element.text for element in ele), "没有找到包含'标签2'的标签项"
        assert not setting.has_fail_message()

    @allure.story("添加重复标签名，不允许修改")
    # @pytest.mark.run(order=1)
    def test_setting_label_repeat(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签1"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="编辑"]'
        )
        setting.enter_texts('//div[text()="标签名："]/following-sibling::div/input', "标签2")

        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        mess = setting.get_error_message()
        assert mess == "记录已存在,请检查！"
        assert not setting.has_fail_message()

    @allure.story("添加重复标签名，修改成功，添加查询数据")
    # @pytest.mark.run(order=1)
    def test_setting_label_updatesuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签1"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="编辑"]'
        )
        setting.enter_texts('//div[text()="标签名："]/following-sibling::div/input', "标签3")
        # 定位名称输入框
        element_to_double_click = driver.find_element(
            By.XPATH,
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[4]',
        )
        # 创建一个 ActionChains 对象
        actions = ActionChains(driver)
        # 双击命令
        actions.double_click(element_to_double_click).perform()
        sleep(1)
        # 点击物料代码
        setting.click_button('//div[text()="物料代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        setting.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        setting.click_button('//div[text()="包含" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        setting.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            "产品A",
        )
        sleep(1)
        setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        sleep(1)
        ele = driver.find_elements(By.XPATH, '//div[@class="labelItem"]')
        sleep(1)
        assert any("标签3" in element.text for element in ele), "没有找到包含'标签3'的标签项"
        assert not setting.has_fail_message()

    @allure.story("标签设置显示在快速查询下放")
    # @pytest.mark.run(order=1)
    def test_setting_label_display(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签3"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        sleep(1)
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="编辑"]'
        )
        ele = setting.get_find_element_xpath('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
        if ele.get_attribute("class") == "ivu-checkbox":
            setting.click_button('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        else:
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')

        setting.get_find_message()
        driver.refresh()
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        eles = driver.find_elements(By.XPATH, '//div[@class="labelItemDIv"]')
        assert any(lable in element.text for element in eles), f"没有找到包含'{lable}'的标签项"
        assert not setting.has_fail_message()

    @allure.story("标签功能生效")
    # @pytest.mark.run(order=1)
    def test_setting_label_success(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签3"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        sleep(1)
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="编辑"]'
        )
        ele = setting.get_find_element_xpath('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
        if ele.get_attribute("class") == "ivu-checkbox":
            setting.click_button('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        else:
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')

        setting.get_find_message()
        driver.refresh()
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_button(f'//div[@class="labelItemDIv" and text()="{lable}"]')
        sleep(3)
        # 定位第一行是否为产品A
        itemcode = setting.get_find_element_xpath(
            '(//table[contains(@class, "vxe-table--body")])[2]//tr[@class="vxe-body--row"][1]/td[2]'
        ).text
        assert "产品A" in itemcode
        assert not setting.has_fail_message()

    @allure.story("标签设置不显示在快速查询下放")
    # @pytest.mark.run(order=1)
    def test_setting_label_nodisplay(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签3"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="编辑"]'
        )
        ele = setting.get_find_element_xpath('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
        if ele.get_attribute("class") == "ivu-checkbox":
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')
        else:
            setting.click_button('//div[text()="是否显示在快速查询下方:"]/following-sibling::label/span')
            setting.click_button('(//button[@class="ivu-btn ivu-btn-primary"])[last()]')

        sleep(1)
        driver.refresh()
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        eles = driver.find_elements(By.XPATH, '//div[@class="labelItemDIv"]')
        all_text = " ".join([element.get_attribute("innerText") for element in eles])
        assert lable not in all_text, f"页面上没有找到'{lable}'"
        assert not setting.has_fail_message()

    @allure.story("删除标签成功")
    # @pytest.mark.run(order=1)
    def test_setting_label_delete(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        lable = "标签3"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[5]//i')
        setting.click_button(
            f'//div[@class="labelItem" and ./div[text()=" {lable} "]]//i[@title="删除"]'
        )
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        ele = driver.find_elements(By.XPATH, f'//div[@class="labelItem"]/div[text()=" {lable} "]')
        assert ele == []
        assert not setting.has_fail_message()

    @allure.story("布局列表拖拽互换位置成功")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_dragsuceess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        sleep(2)
        afert_name = setting.get_find_element_xpath('//div[@class="tabsDivItemCon"]/div[1]').text
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        sleep(1)

        div1 = setting.get_find_element_xpath('(//i[@class="ivu-icon ivu-icon-ios-move"])[1]')
        div2 = setting.get_find_element_xpath('(//i[@class="ivu-icon ivu-icon-ios-move"])[2]')
        # 1> 实例化鼠标对象(关联浏览器对象)
        action = ActionChains(driver)
        # 2> 调用方法(传入目标元素)
        action.drag_and_drop(div1, div2)
        # 3> 执行方法
        action.perform()
        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        driver.refresh()
        sleep(2)
        before_name = setting.get_find_element_xpath('//div[@class="tabsDivItemCon"]/div[2]')
        assert before_name.text == afert_name
        assert not setting.has_fail_message()

    @allure.story("修改布局名称成功")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_updatesuceess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局B"
        sleep(2)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        sleep(1)

        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)

        setting.click_button(f'(//div[text()="重命名"])[{index + 1}]')
        ele = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]//input'
        )
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        setting.enter_texts(f'//div[@id="container"]/div[.//text()="{layout}"]//input', "修改布局")

        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        driver.refresh()
        name = setting.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" 修改布局 "]'
        ).text
        assert name == "修改布局"
        assert not setting.has_fail_message()

    @allure.story("重复修改布局 不允许修改")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_updatefail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "修改布局"
        sleep(2)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        sleep(1)

        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)
        setting.click_button(f'(//div[text()="重命名"])[{index + 1}]')
        ele = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]//input'
        )
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        setting.enter_texts(f'//div[@id="container"]/div[.//text()="{layout}"]//input', "测试布局A")

        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        # 获取设置后的提示信息
        message = setting.get_error_message()
        # 断言提示信息是否符合预期，以验证设置是否生效
        assert message == "布局名称不能重复！"
        assert not setting.has_fail_message()

    @allure.story("布局删除成功")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_deletesuccess(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "修改布局"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)

        sleep(2)
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        driver.refresh()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        # 断言目标 div 已经被成功删除
        assert len(after_layout) == 0
        assert not setting.has_fail_message()

    @allure.story("布局删除成功")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_deletesuccess1(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "测试布局A"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)

        sleep(3)
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(2)
        driver.refresh()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        # 断言目标 div 已经被成功删除
        assert len(after_layout) == 0
        assert not setting.has_fail_message()

    @allure.story("默认布局不允许删除")
    # @pytest.mark.run(order=1)
    def test_setting_layout_deletefail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "默认"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        # 获取设置后的提示信息
        message = setting.get_error_message()
        # 断言提示信息是否符合预期，以验证设置是否生效
        assert message == "不能删除默认布局!"
        assert not setting.has_fail_message()

    @allure.story("复制列表成功")
    # @pytest.mark.run(order=1)
    def test_setting_layoutlist_deletefail(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "默认"
        sleep(1)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        sleep(1)
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{layout}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.hover(layout)
        setting.click_button(f'(//li[text()="复制"])[{index + 1}]')
        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        driver.refresh()
        eles = setting.finds_elements(By.XPATH, '//div[@class="tabsDivItemCon"]/div')
        sleep(1)
        name = [ele.text for ele in eles]
        first_long_name = next((text for text in name if len(text) > 10), None)
        assert layout in first_long_name
        assert not setting.has_fail_message()

    @allure.story("设置默认布局默认启动-成功，删除Copy布局")
    # @pytest.mark.run(order=1)
    def test_setting_default_start_success2(self, login_to_setting):
        driver = login_to_setting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = "默认"
        setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        sleep(1)
        setting.click_setting_button()
        checkbox = setting.get_find_element_xpath(
            '//div[text()="是否默认启动:"]/following-sibling::label/span'
        )
        # 检查复选框是否未被选中
        if checkbox.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button(
                '//div[text()="是否默认启动:"]/following-sibling::label/span'
            )
            sleep(1)
            # 点击确定按钮保存设置
            setting.click_confirm_button()
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_confirm_button()

        sleep(1)
        safe_quit(driver)
        # 重新打开浏览器
        driver_path = DateDriver().driver_path
        driver = create_driver(driver_path)
        driver.implicitly_wait(3)

        # 重新登录并进入目标页面
        page = LoginPage(driver)
        page.navigate_to(DateDriver().url)
        page.login(DateDriver().username, DateDriver().password, DateDriver().planning)
        # 用新 driver 初始化 SettingPage
        setting = SettingPage(driver)
        page.click_button('(//span[text()="计划管理"])[1]')
        page.click_button('(//span[text()="计划基础数据"])[1]')
        page.click_button('(//span[text()="物品"])[1]')
        sleep(1)
        eles = setting.finds_elements(By.XPATH, '//div[@class="tabsDivItemCon"]/div')
        sleep(1)
        name = [ele.text for ele in eles]
        first_long_name = next((text for text in name if len(text) > 10), None)
        setting.click_button('//i[@id="tabsDrawerIcon"]')
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = setting.get_find_element_xpath(
            f'//div[@id="container"]/div[.//text()="{first_long_name}"]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = setting.get_find_element_xpath(f'//div[@id="container"]')
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        setting.click_button(f'//div[@id="container"]/div[{index + 1}]/span')
        setting.hover(first_long_name)
        setting.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(1)
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')

        setting.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(1)
        driver.refresh()
        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {first_long_name} "]'
        )
        assert after_layout == []
        assert not setting.has_fail_message()
        safe_quit(driver)