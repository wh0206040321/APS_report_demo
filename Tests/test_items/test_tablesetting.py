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

from Pages.itemsPage.item_page import ItemPage
from Pages.itemsPage.login_page import LoginPage
from Pages.itemsPage.setting_page import SettingPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot


@pytest.fixture(scope="module")  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_tablesetting():
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
        page.wait_for_loading_to_disappear()
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("表格右键设置设置测试用例")
@pytest.mark.run(order=30)
class TestTableSettingPage:
    @allure.story("添加布局")
    # @pytest.mark.run(order=1)
    def test_tablesetting_addlayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        item = ItemPage(driver)  # 用 driver 初始化 ItemPage
        layout = "测试布局A"
        item.add_layout(layout)
        # 获取布局名称的文本元素
        name = item.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        assert layout == name
        assert not item.has_fail_message()

    @allure.story("右键复制编号成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_rightclickcopy(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '复制')
        setting.click_button('//p[text()="物料代码"]/ancestor::div[2]//input')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        sleep(1)
        ele = setting.get_find_element_xpath('//p[text()="物料代码"]/ancestor::div[2]//input').get_attribute('value')
        setting.right_refresh('物品')
        assert ele == '1'
        assert not setting.has_fail_message()

    @allure.story("右键隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_hiddenrow1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '隐藏行')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("右键取消隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_unhiderow1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '取消隐藏行')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("多选行点击隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_hiddenrow2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[3]//td[2]').text
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        setting.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = setting.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        ele = setting.get_find_element_xpath(elements[0])
        ActionChains(driver).context_click(ele).perform()
        setting.click_button(f'//li//span[text()="隐藏行"]')
        sleep(1)
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("点击图标取消隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_unhiderow2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '隐藏行')

        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        setting.click_button('//span[@class="hiddenRowIcon hiddenRowIcon_Top"]/i')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        setting.right_refresh('物品')
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("右键切换工艺产能成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchingmaster(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换工艺产能')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 工艺产能 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 工艺产能 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("右键切换图形制造成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchGraphicManufacturing(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换图形制造')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 工艺产能图形化 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 工艺产能图形化 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("右键切换订单")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchOrder(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换订单')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 制造订单 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 制造订单 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("右键切换订单+资源甘特图:分派资源")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchOrderChart1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                                      '订单+资源甘特图:分派资源')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 复合图表-订单+资源甘特图 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 复合图表-订单+资源甘特图 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("右键切换订单+资源甘特图:候补资源")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchOrderChart2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                                      '订单+资源甘特图:候补资源')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 复合图表-订单+资源甘特图 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 复合图表-订单+资源甘特图 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("右键筛选过滤成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_filter(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ele1 = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        ele = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]')
        ActionChains(setting.driver).context_click(ele).perform()
        container = setting.get_find_element_xpath(
            f'//li//span[text()="筛选"]'
        )
        sleep(3)
        ActionChains(driver).move_to_element(container).perform()
        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//li//span[text()="包含"]'
            ))
        )
        # 3️⃣ 再点击图标
        delete_icon.click()
        sleep(1)
        eles = setting.finds_elements(By.XPATH, '//table[@class="vxe-table--body"]//tr//td[2]')
        ele2 = [ele.text for ele in eles]
        ele3 = setting.get_find_element_xpath('//p[text()="物料代码"]/ancestor::div[2]//input').get_attribute('value')
        assert ele1 == ele3
        assert all(ele1 in e for e in ele2)
        assert not setting.has_fail_message()

    @allure.story("资源右键设置无效资源成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_invalidresource(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//div[label[text()="无效资源"]]/div/label'
        setting.click_button('(//span[text()="资源"])[1]')
        setting.wait_for_loading_to_disappear()
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '资源无效')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' in cla
        assert not setting.has_fail_message()

    @allure.story("资源右键设置取消无效资源成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_effectiveresource(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//div[label[text()="无效资源"]]/div/label'
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' not in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '资源无效')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' not in cla
        assert not setting.has_fail_message()

    @allure.story("工序右键设置无效标识成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_invalidprocess(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('//div[div[text()=" 资源 "]]/span')
        xpath = '//div[label[text()="无效标志"]]/div/label'
        setting.click_button('(//span[text()="工序"])[1]')
        setting.wait_for_loading_to_disappear()
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])', '工序无效')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' in cla
        assert not setting.has_fail_message()

    @allure.story("工序右键设置取消无效标识成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_effectiveprocess(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//div[label[text()="无效标志"]]/div/label'
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' not in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.click_right_click_row('(//table[@class="vxe-table--body"]//tr[1]//td[1])', '工序无效')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' not in cla
        assert not setting.has_fail_message()

    @allure.story("订单右键复制编号成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_rightclickcopy(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('//div[div[text()=" 工序 "]]/span')
        setting.click_button('(//span[text()="计划业务数据"])[1]')
        setting.click_button('(//span[text()="制造订单"])[1]')
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '复制')
        setting.click_button('//p[text()="订单代码"]/ancestor::div[2]//input')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        sleep(1)
        ele = setting.get_find_element_xpath('//p[text()="订单代码"]/ancestor::div[2]//input').get_attribute('value')
        setting.right_refresh('制造订单')
        assert ele == '1'
        assert not setting.has_fail_message()

    @allure.story("订单右键隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_hiddenrow1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '隐藏行')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("订单右键取消隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_unhiderow1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '取消隐藏行')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("订单多选行点击隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_hiddenrow2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[3]//td[2]').text
        elements = ['(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                    '(//table[@class="vxe-table--body"]//tr[2]//td[1])[2]']
        setting.click_button(elements[0])
        # 第二个单元格 Shift+点击（选择范围）
        cell2 = setting.get_find_element_xpath(elements[1])
        ActionChains(driver).key_down(Keys.SHIFT).click(cell2).key_up(Keys.SHIFT).perform()
        sleep(1)
        element = setting.get_find_element_xpath(elements[0])

        # 获取元素位置和大小
        location = element.location
        size = element.size

        # 计算中心点坐标
        center_x = size['width'] // 2
        center_y = size['height'] // 2

        # ✅ 向左偏移 10 像素，向上偏移 10 像素
        offset_left = 10
        offset_up = 10

        center_x -= offset_left  # 向左移动
        center_y -= offset_up  # 向上移动（Y轴坐标向上是减少）

        # 精确移动到偏移后的位置（左上方）
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(element, center_x, center_y)
        actions.pause(0.1)
        actions.context_click()
        actions.perform()
        setting.click_button(f'//li//span[text()="隐藏行"]')
        sleep(1)
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("订单点击图标取消隐藏行成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_unhiderow2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '隐藏行')

        after_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[1]//td[2]').text
        setting.click_button('//span[@class="hiddenRowIcon hiddenRowIcon_Top"]/i')
        before_ = setting.get_find_element_xpath('//table[@class="vxe-table--body"]//tr[2]//td[2]').text
        setting.right_refresh('制造订单')
        assert after_ == before_
        assert not setting.has_fail_message()

    @allure.story("订单右键切换工艺产能成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_switchingmaster(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换工艺产能')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 工艺产能 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 工艺产能 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("订单右键切换图形制造成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_switchGraphicManufacturing(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换图形制造')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 工艺产能图形化 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 工艺产能图形化 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("订单右键切换工作")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_switchOrder(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '切换工作')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 工作明细 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 工作明细 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("订单右键切换订单+资源甘特图:分派资源")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_switchOrderChart1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                                      '订单+资源甘特图:分派资源')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 复合图表-订单+资源甘特图 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 复合图表-订单+资源甘特图 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("订单右键切换订单+资源甘特图:候补资源")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_switchOrderChart2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]',
                                      '订单+资源甘特图:候补资源')
        ele = setting.finds_elements(By.XPATH, '//div[@class="labelTitle"][text()=" 复合图表-订单+资源甘特图 "]')
        err = setting.finds_elements(By.XPATH, '//i[@class="ivu-icon ivu-icon-ios-close-circle"]')
        setting.click_button('//div[div[text()=" 复合图表-订单+资源甘特图 "]]/span')
        assert len(ele) == 1 and len(err) == 0
        assert not setting.has_fail_message()

    @allure.story("订单右键设置非分派对象成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_invalid(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//div[label[text()="非分派对象标志"]]/div/label'
        setting.wait_for_loading_to_disappear()
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '非分派对象')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' in cla
        assert not setting.has_fail_message()

    @allure.story("订单右键设置取消设置非分派对象成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_order_effective(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//div[label[text()="非分派对象标志"]]/div/label'
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'ivu-checkbox-wrapper-checked' not in cla:
            setting.click_button(xpath)
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        setting.wait_for_loading_to_disappear()
        setting.realistic_right_click('(//table[@class="vxe-table--body"]//tr[1]//td[1])[2]', '非分派对象')
        sleep(1)
        setting.click_button('//table[@class="vxe-table--body"]//tr[1]//td[2]')
        setting.click_button('//p[text()="编辑"]')
        setting.wait_for_loading_to_disappear()
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_button('//div[@class="vxe-modal--footer"]//span[text()="取消"]')
        assert 'ivu-checkbox-wrapper-checked' not in cla
        assert not setting.has_fail_message()

    @allure.story("复制列头成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_copyColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_button('//div[div[text()=" 制造订单 "]]/span')
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '复制')
        setting.click_button('//p[text()="物料代码"]/ancestor::div[2]//input')
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        sleep(1)
        ele = setting.get_find_element_xpath('//p[text()="物料代码"]/ancestor::div[2]//input').get_attribute('value')
        setting.right_refresh('物品')
        assert ele == '物品代码'
        assert not setting.has_fail_message()

    @allure.story("右键设置固定列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_fixedColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        xpath = '//tr[./td[3][.//span[text()="物料代码"]]]/td[9]//label'
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'is--checked' in cla:
            setting.click_button(xpath)
        setting.click_confirm_button()
        setting.right_refresh('物品')
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '固定列')
        # 保存布局
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[6]//i')
        setting.get_find_message()
        setting.right_refresh('物品')
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        ele = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_confirm_button()
        assert 'is--checked' in ele
        assert not setting.has_fail_message()

    @allure.story("右键取消设置固定列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_cancelfixedColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        xpath = '//tr[./td[3][.//span[text()="物料代码"]]]/td[9]//label'
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'is--checked' not in cla:
            setting.click_button(xpath)
        setting.click_confirm_button()
        setting.right_refresh('物品')
        sleep(2)
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[2]//p', '解除固定列')
        # 保存布局
        setting.click_button('//div[@class="toolTabsDiv"]/div[2]/div[6]//i')
        setting.get_find_message()
        setting.right_refresh('物品')
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        ele = setting.get_find_element_xpath(xpath).get_attribute('class')
        setting.click_confirm_button()
        assert 'is--checked' not in ele
        assert not setting.has_fail_message()

    @allure.story("表格设置中设置固定列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_setfixedColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        xpath = '//tr[./td[3][.//span[text()="物料代码"]]]/td[9]//label'
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'is--checked' not in cla:
            setting.click_button(xpath)
        setting.click_confirm_button()
        setting.right_refresh('物品')
        cla = setting.get_find_element_xpath('//table[@class="vxe-table--header"]//tr[1]/th[2]').get_attribute('class')
        assert 'col--fixed' in cla
        assert not setting.has_fail_message()

    @allure.story("表格设置中取消设置固定列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_setCancelFixedColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_setting_button()
        setting.click_button('//div[text()=" 显示设置 "]')
        xpath = '//tr[./td[3][.//span[text()="物料代码"]]]/td[9]//label'
        cla = setting.get_find_element_xpath(xpath).get_attribute('class')
        if 'is--checked' in cla:
            setting.click_button(xpath)
        setting.click_confirm_button()
        setting.right_refresh('物品')
        cla = setting.get_find_element_xpath('//table[@class="vxe-table--header"]//tr[1]/th[2]').get_attribute('class')
        assert 'col--fixed' not in cla
        assert not setting.has_fail_message()

    @allure.story("表格右键设置表格布局，设置列宽成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_FixedColumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '表格布局设置')
        setting.wait_for_el_loading_mask()
        setting.click_button('//div[text()=" 显示设置 "]')
        xpath = '//tr[./td[3][.//span[text()="物料代码"]]]/td[8]//input'
        ele = setting.get_find_element_xpath(xpath)
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(Keys.DELETE)
        setting.enter_texts(xpath, '120')
        setting.click_confirm_button()
        setting.right_refresh('物品')
        sty = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr[1]/th[2])[1]/div[1]').get_attribute('style')
        if sty and 'width:' in sty:
            # 提取宽度值
            width_part = sty.split('width:')[1].split(';')[0].strip()
            width_value = width_part.replace('px', '').strip()
            logging.info(f"宽度值: {width_value}")
            assert 120 - 2 == int(width_value)
        else:
            logging.info("未找到宽度设置")
            assert 1 == 0
        assert not setting.has_fail_message()

    @allure.story("表格右键添加新布局成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_setlayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = '右键添加新布局'
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '添加新布局')
        setting.wait_for_el_loading_mask()
        sleep(2)
        setting.enter_texts(
            '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
        )
        sleep(1)

        setting.click_button('(//div[text()=" 显示设置 "])[1]')
        sleep(1)
        # 获取是否可见选项的复选框元素
        checkbox2 = setting.get_find_element_xpath(
            '(//div[./div[text()="是否可见:"]])[1]/label/span'
        )
        # 检查复选框是否未被选中
        if checkbox2.get_attribute("class") == "ivu-checkbox":
            # 如果未选中，则点击复选框进行选中
            setting.click_button('(//div[./div[text()="是否可见:"]])[1]/label/span')
            # 点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        else:
            # 如果已选中，直接点击确定按钮保存设置
            setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
        message = setting.get_find_message()
        sleep(1)
        ele = setting.finds_elements(By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        assert message == '保存成功' and len(ele) == 1
        assert not setting.has_fail_message()

    @allure.story("表格右键删除布局成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_setdellayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = '右键添加新布局'
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '删除布局')
        setting.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        message = setting.get_find_message()
        setting.wait_for_loading_to_disappear()
        sleep(1)
        ele = setting.finds_elements(By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        assert message == '删除成功！' and len(ele) == 0
        assert not setting.has_fail_message()

    @allure.story("表格右键隐藏列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_hiddencolumn(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        before_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[3])[1]//p').text
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '隐藏列')
        sleep(1)
        after_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p').text
        assert before_name == after_name
        assert not setting.has_fail_message()

    @allure.story("表格右键取消隐藏列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_unhideColumn1(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        before_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p').text
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '取消隐藏列')
        sleep(1)
        after_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[3])[1]//p').text
        assert before_name == after_name
        assert not setting.has_fail_message()

    @allure.story("点击图标取消隐藏列成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_unhideColumn2(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.right_refresh('物品')
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '隐藏列')
        before_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p').text
        setting.click_button('//div[@class="colHideIcon" and @style != "display: none;"]/i')
        sleep(1)
        after_name = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[3])[1]//p').text
        assert before_name == after_name
        assert not setting.has_fail_message()

    @allure.story("右键点击布局列表切换布局成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_switchLayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        layout = '右键添加切换布局'
        lay = setting.finds_elements(By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
        if len(lay) == 0:
            setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '添加新布局')
            setting.wait_for_el_loading_mask()
            sleep(2)
            setting.enter_texts(
                '//div[text()="当前布局:"]/following-sibling::div//input', f"{layout}"
            )
            sleep(1)

            setting.click_button('(//div[text()=" 显示设置 "])[1]')
            sleep(1)
            # 获取是否可见选项的复选框元素
            checkbox2 = setting.get_find_element_xpath(
                '(//div[./div[text()="是否可见:"]])[1]/label/span'
            )
            # 检查复选框是否未被选中
            if checkbox2.get_attribute("class") == "ivu-checkbox":
                # 如果未选中，则点击复选框进行选中
                setting.click_button('(//div[./div[text()="是否可见:"]])[1]/label/span')
                # 点击确定按钮保存设置
                setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
            else:
                # 如果已选中，直接点击确定按钮保存设置
                setting.click_button('(//div[@class="demo-drawer-footer"])[3]/button[2]')
            setting.get_find_message()

        ele = setting.get_find_element_xpath(f'//div[@class="tabsDivItemCon"]/div[text()=" 测试布局A "]').get_attribute(
            'class')
        if 'tabsDivActive' in ele:
            setting.click_button(f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]')
            setting.wait_for_loading_to_disappear()
        setting.right_refresh('物品')

        setting.click_button('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p')
        ele = setting.get_find_element_xpath('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p')
        ActionChains(setting.driver).context_click(ele).perform()

        container = setting.get_find_element_xpath(
            f'//li//span[text()="布局列表"]'
        )
        sleep(3)
        ActionChains(driver).move_to_element(container).perform()
        # 2️⃣ 等待图标可见
        delete_icon = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//li//span[text()="测试布局A"]'
            ))
        )
        # 3️⃣ 再点击图标
        delete_icon.click()
        setting.wait_for_loading_to_disappear()
        ele = setting.get_find_element_xpath(f'//div[@class="tabsDivItemCon"]/div[text()=" 测试布局A "]').get_attribute('class')
        assert 'tabsDivActive' in ele
        assert not setting.has_fail_message()

    @allure.story("右键保存布局成功")
    # @pytest.mark.run(order=1)
    def test_tablesetting_saveLayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.enter_texts('//p[text()="物料代码"]/ancestor::div[2]//input', '1')
        setting.click_right_click_row('(//table[@class="vxe-table--header"]//tr/th[2])[1]//p', '保存布局')
        setting.get_find_message()
        setting.wait_for_el_loading_mask()
        setting.right_refresh('物品')
        ele = setting.get_find_element_xpath(f'//p[text()="物料代码"]/ancestor::div[2]//input').get_attribute('value')
        assert ele == '1'
        assert not setting.has_fail_message()

    @allure.story("删除布局")
    # @pytest.mark.run(order=1)
    def test_tablesetting_delLayout(self, login_to_tablesetting):
        driver = login_to_tablesetting  # WebDriver 实例
        setting = SettingPage(driver)  # 用 driver 初始化 SettingPage
        setting.del_layout('测试布局A')
        sleep(1)
        setting.click_button('//div[@class="tabsDivItemCon"]/div[text()=" 右键添加切换布局 "]')
        setting.wait_for_loading_to_disappear()
        setting.del_layout('右键添加切换布局')
        sleep(1)
        ele1 = setting.finds_elements(By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" 测试布局A "]')
        ele2 = setting.finds_elements(By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" 右键添加切换布局 "]')
        assert len(ele1) == 0 and len(ele2) == 0
        assert not setting.has_fail_message()

