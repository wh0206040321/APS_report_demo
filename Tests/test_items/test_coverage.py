import logging
import random
from datetime import datetime
from time import sleep

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Pages.itemsPage.adds_page import AddsPages
from Pages.itemsPage.coverage_page import Coverage
from Pages.itemsPage.login_page import LoginPage
from Utils.data_driven import DateDriver
from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
from Utils.shared_data_util import SharedDataUtil


@pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
def login_to_coverage():
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
        page.click_button('(//span[text()="覆盖日历"])[1]')  # 点击覆盖日历
        yield driver  # 提供给测试用例使用
    finally:
        if driver:
            safe_quit(driver)


@allure.feature("覆盖日历表测试用例")
@pytest.mark.run(order=10)
class TestCoveragePage:
    @allure.story("添加覆盖日历信息 不填写数据点击确认 不允许提交，增加布局")
    # @pytest.mark.run(order=1)
    def test_coverage_addfail(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        layout = "测试布局A"
        coverage.add_layout(layout)

        # 获取布局名称的文本元素
        name = coverage.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        ).text
        coverage.click_add_button()
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 资源
        resource_box = coverage.get_find_element_xpath(
            '//div[@id="2ssy7pog-1nb7"]//input'
        )
        # 时序
        chronology_box = coverage.get_find_element_xpath(
            '//div[@id="tg89jocr-6to2"]//input'
        )
        # 资源量
        resources_box = coverage.get_find_element_xpath(
            '//div[@id="k0z05daz-8tok"]//input'
        )

        # 断言边框颜色是否为红色（可以根据实际RGB值调整）
        sleep(1)
        resource_box_color = resource_box.value_of_css_property("border-color")
        chronology_box_color = chronology_box.value_of_css_property("border-color")
        resources_box_color = resources_box.value_of_css_property("border-color")
        expected_color = "rgb(255, 0, 0)"  # 红色的 rgb 值
        assert resource_box_color == expected_color
        assert chronology_box_color == expected_color
        assert resources_box_color == expected_color
        assert layout == name
        assert not coverage.has_fail_message()

    @allure.story("数字文本框 只允许填写数字")
    # @pytest.mark.run(order=1)
    def test_coverage_addnum(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage

        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        coverage.enter_texts(
            '//div[@id="9la8xi09-07ws"]//input',
            "e1文字abc。？~1++3.,/.=8",
        )
        sleep(1)
        # 获取表示顺序数字框
        coveragenum = coverage.get_find_element_xpath(
            '//div[@id="9la8xi09-07ws"]//input'
        ).get_attribute("value")
        assert coveragenum == "1138", f"预期{coveragenum}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框的校验，只填写一个时间，文本框爆红")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence1(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': "2026/08/21",
        }
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        assert all(color == "rgb(255, 0, 0)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框和资源量的校验，设置不合法，文本框爆红")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence2(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': "2026/08/21;202e/08/21",
            '//div[@id="k0z05daz-8tok"]//input': "e1;2",
        }
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        assert all(color == "rgb(255, 0, 0)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框和资源量的校验，设置不合法，文本框爆红")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence3(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': "226/08/2r",
            '//div[@id="k0z05daz-8tok"]//input': "1;d2",
        }
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        assert all(color == "rgb(255, 0, 0)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框和资源量的校验，设置为中文分号，文本框爆红")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence4(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': "2026/08/21；2027/08/21",
            '//div[@id="k0z05daz-8tok"]//input': "1；2",
        }
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        assert all(color == "rgb(255, 0, 0)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框和资源量的校验，输入多个时间段和资源量，可通过")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence5(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': "2026/08/21;2027/08/21;2028/08/21;2029/08/21",
            '//div[@id="k0z05daz-8tok"]//input': "1;2;19;300",
        }
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        assert all(color == "rgb(220, 222, 226)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert not coverage.has_fail_message()

    @allure.story("时序文本框的校验，当后面的时间段比前面的时间段早，会自动纠正")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence6(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        start = "2026/08/21 00:00:00"
        end = "2025/07/21 00:00:00"
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': f"{start};{end}",
        }
        xpath_list = [
            '//div[@id="dnj11joa-anmy"]//input',
            '//div[@id="qqs38txd-vd0r"]//input',
        ]
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        value_list = add.batch_acquisition_input(xpath_list)
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        value = coverage.get_find_element_xpath(key_list[0]).get_attribute("value")
        assert all(color == "rgb(220, 222, 226)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert value == end + ";" + start
        assert value_list[0] == end and value_list[1] == start
        assert not coverage.has_fail_message()

    @allure.story("时序文本框的校验，输入三个时间段，当中间的时间段比前面的时间段早，会自动纠正")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence7(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        start = "2026/08/21 00:00:00"
        middle = "2025/08/22 00:00:00"
        end = "2027/07/21 00:00:00"
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': f"{start};{middle};{end}",
        }
        xpath_list = [
            '//div[@id="dnj11joa-anmy"]//input',
            '//div[@id="qqs38txd-vd0r"]//input',
        ]
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        sleep(1)
        # 获取表示顺序数字框
        value_list = add.batch_acquisition_input(xpath_list)
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        value = coverage.get_find_element_xpath(key_list[0]).get_attribute("value")
        assert all(color == "rgb(220, 222, 226)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert value == middle + ";" + start + ";" + end
        assert value_list[0] == middle and value_list[1] == end
        assert not coverage.has_fail_message()

    @allure.story("时序文本框的校验，输入错误的年份会爆红，点击确定时间标记会显示当前时间")
    # @pytest.mark.run(order=1)
    def test_coverage_timesequence8(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        add = AddsPages(driver)
        start = "202/08/21 00:00:00"
        end = "2025/07/21 00:00:00"
        xpath_value_map = {
            '//div[@id="tg89jocr-6to2"]//input': f"{start};{end}",
        }
        xpath_list = [
            '//div[@id="dnj11joa-anmy"]//input',
            '//div[@id="qqs38txd-vd0r"]//input',
            '//div[@id="dmnoa1tj-z7w5"]//input',
        ]
        coverage.click_add_button()  # 检查点击添加
        # 输入文本
        add.batch_modify_inputs(xpath_value_map)
        coverage.click_button('//div[@class="vxe-modal--footer"]//span[text()="确定"]')
        # 获取当前时间
        current_time = datetime.now()
        # 格式化为 年/月/日 的字符串
        formatted_date = current_time.strftime("%Y/%m/%d")
        sleep(1)
        # 获取表示顺序数字框
        value_list = add.batch_acquisition_input(xpath_list)
        key_list = list(xpath_value_map.keys())
        sequence_box_color = add.get_border_color(key_list)
        value = coverage.get_find_element_xpath(xpath_list[2]).get_attribute("value")
        assert all(color == "rgb(255, 0, 0)" for color in sequence_box_color), f"预期{sequence_box_color}"
        assert formatted_date in value
        assert value_list[0] == "" and value_list[1] == end
        assert not coverage.has_fail_message()

    @allure.story("校验数字文本框和文本框成功")
    # @pytest.mark.run(order=1)
    def test_coverage_textverify(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        start = "2027/08/21 00:00:00"
        end = "2028/07/21 00:00:00"
        name = '111111111111111133331122221111222221111111113333111111144444111111111111111111111111111111111111111111111111'
        coverage.click_add_button()

        # 点击资源
        coverage.click_button(
            '//div[@id="2ssy7pog-1nb7"]//i'
        )
        # 勾选框
        random_int = random.randint(1, 8)
        sleep(1)
        coverage.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
        sleep(1)
        coverage.click_button(
            '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = coverage.get_find_element_xpath(
            '//div[@id="2ssy7pog-1nb7"]//input'
        ).get_attribute("value")

        coverage.enter_texts(f'//div[@id="9la8xi09-07ws"]//input', 3)

        # 时序
        coverage.enter_texts(
            '//div[@id="tg89jocr-6to2"]//input', f"{start};{end}"
        )
        chronology = coverage.get_find_element_xpath(
            '//div[@id="tg89jocr-6to2"]//input'
        ).get_attribute("value")

        # 资源量
        coverage.enter_texts('//div[@id="k0z05daz-8tok"]//input', "4")
        resources = coverage.get_find_element_xpath(
            '//div[@id="k0z05daz-8tok"]//input'
        ).get_attribute("value")
        # 校验文本框
        coverage.enter_texts('//div[@id="9la8xi09-07ws"]//input', name)
        coverage.enter_texts('//div[@id="luvfyssv-uxe2"]//input', name)
        sleep(1)
        coverage.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        driver.execute_script("document.body.style.zoom='0.6'")
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        addcoverage = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addstart = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        addend = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        addchronology = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        addresources = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[8]'
        ).text
        text_ = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[12]'
        ).text
        num_ = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[5]'
        ).text
        assert (
                resource == addcoverage
                and start == addstart
                and end == addend
                and chronology == addchronology
                and resources == addresources
                and text_ == name
                and num_ == '10000'
        )
        assert not coverage.has_fail_message()

    @allure.story("添加数据成功")
    # @pytest.mark.run(order=1)
    def test_coverage_addweeksuccess1(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        start = "2027/08/21 00:00:00"
        end = "2028/07/21 00:00:00"
        coverage.click_add_button()

        # 点击资源
        coverage.click_button(
            '//div[@id="2ssy7pog-1nb7"]//i'
        )
        # 勾选框
        random_int = random.randint(1, 8)
        sleep(1)
        coverage.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
        sleep(1)
        coverage.click_button(
            '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
        )

        coverage.enter_texts(f'//div[@id="9la8xi09-07ws"]//input', 3)

        # 时序
        coverage.enter_texts(
            '//div[@id="tg89jocr-6to2"]//input', f"{start};{end}"
        )

        # 资源量
        coverage.enter_texts('//div[@id="k0z05daz-8tok"]//input', "4")
        sleep(1)
        # 获取勾选的资源代码
        resource = coverage.get_find_element_xpath(
            '//div[@id="2ssy7pog-1nb7"]//input'
        ).get_attribute("value")
        chronology = coverage.get_find_element_xpath(
            '//div[@id="tg89jocr-6to2"]//input'
        ).get_attribute("value")
        resources = coverage.get_find_element_xpath(
            '//div[@id="k0z05daz-8tok"]//input'
        ).get_attribute("value")

        sleep(1)
        coverage.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        coverage.wait_for_loading_to_disappear()
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        addcoverage = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addstart = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        addend = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        addchronology = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        addresources = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[8]'
        ).text
        assert (
            resource == addcoverage
            and start == addstart
            and end == addend
            and chronology == addchronology
            and resources == addresources
        )
        assert not coverage.has_fail_message()

    @allure.story("输入全部数据，添加保存成功")
    # @pytest.mark.run(order=1)
    def test_coverage_addall(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        # 清空之前的共享数据
        SharedDataUtil.clear_data()
        data_list = "20"
        coverage.click_add_button()  # 检查点击添加
        resource, selClass, start, end = coverage.add_input_all(data_list)
        # 保存数据
        SharedDataUtil.save_data(
            {"resource": resource, "selClass": selClass, "start": start, "end": end}
        )
        sleep(1)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)

            if i == 6:
                try:
                    label = td.find_element(By.TAG_NAME, "span")
                    label_class = label.get_attribute("class")
                    print(f"第 {i} 个单元格中 <label> 的 class 属性：{label_class}")
                    columns_text.append(label_class)
                except NoSuchElementException:
                    print(f"⚠️ 第 {i} 个单元格中未找到 <label> 元素")
                    columns_text.append("")
            else:
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
        # 获取当前时间
        current_time = datetime.now()
        # 格式化为 年/月/日 的字符串
        formatted_date = current_time.strftime("%Y/%m/%d")
        print(columns_text)
        bef_text = [f'{resource}', f'{start}', f'{end}', f'{data_list}', f'{selClass}', f'{start};{end}', f'{data_list}', '2025', f'{formatted_date}',
                    '2', f'{data_list}', f'{data_list}',  f'{DateDriver.username}']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text),start=1):
            if i == 8:
                assert str(e) in str(a), f"第8项包含断言失败：'{e}' not in '{a}'"
            elif i == 9:
                assert str(e) in str(a), f"第9项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not coverage.has_fail_message()

    @allure.story("重新打开浏览器，数据还存在")
    # @pytest.mark.run(order=1)
    def test_coverage_restart(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        shared_data = SharedDataUtil.load_data()
        resource = shared_data.get("resource")
        start = shared_data.get("start")
        end = shared_data.get("end")
        selClass = shared_data.get("selClass")
        data_list = "20"
        sleep(1)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        # 缩放到最小（例如 25%）
        driver.execute_script("document.body.style.zoom='0.25'")
        sleep(1)

        row_xpath = '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]'
        # 获取目标行
        target_row = driver.find_element(By.XPATH, row_xpath)

        # 获取该行下所有 td 元素
        td_elements = target_row.find_elements(By.XPATH, "./td")
        td_count = len(td_elements)
        print(f"该行共有 {td_count} 个 <td> 元素")
        columns_text = []
        # 遍历每个 td[i]
        # 遍历每个 td[i] 并提取文本
        for i in range(2, td_count + 1):
            td_xpath = f'{row_xpath}/td[{i}]'
            sleep(0.2)
            try:
                td = driver.find_element(By.XPATH, td_xpath)
            except StaleElementReferenceException:
                print(f"⚠️ 第 {i} 个单元格引用失效，尝试重新查找")
                sleep(0.2)
                td = driver.find_element(By.XPATH, td_xpath)

            if i == 6:
                try:
                    label = td.find_element(By.TAG_NAME, "span")
                    label_class = label.get_attribute("class")
                    print(f"第 {i} 个单元格中 <label> 的 class 属性：{label_class}")
                    columns_text.append(label_class)
                except NoSuchElementException:
                    print(f"⚠️ 第 {i} 个单元格中未找到 <label> 元素")
                    columns_text.append("")
            else:
                text = td.text.strip()
                print(f"第 {i} 个单元格内容：{text}")
                columns_text.append(text)
        # 获取当前时间
        current_time = datetime.now()
        # 格式化为 年/月/日 的字符串
        formatted_date = current_time.strftime("%Y/%m/%d")
        print(columns_text)
        bef_text = [f'{resource}', f'{start}', f'{end}', f'{data_list}', f'{selClass}', f'{start};{end}',
                    f'{data_list}', '2025', f'{formatted_date}',
                    '2', f'{data_list}', f'{data_list}', f'{DateDriver.username}']
        assert len(columns_text) == len(bef_text), f"长度不一致：actual={len(columns_text)}, expected={len(bef_text)}"
        for i, (a, e) in enumerate(zip(columns_text, bef_text), start=1):
            if i == 8:
                assert str(e) in str(a), f"第8项包含断言失败：'{e}' not in '{a}'"
            elif i == 9:
                assert str(e) in str(a), f"第9项包含断言失败：'{e}' not in '{a}'"
            else:
                assert a == e, f"第{i + 1}项不一致：actual='{a}', expected='{e}'"
        assert not coverage.has_fail_message()

    @allure.story("删除全部input数据成功")
    # @pytest.mark.run(order=1)
    def test_coverage_delall(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        coverage.wait_for_loading_to_disappear(coverage)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        coverage.click_button('//span[text()=" 更新时间"]/following-sibling::div')
        sleep(1)
        coveragedata1 = coverage.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        coverage.click_button('(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]')
        coverage.click_del_button()  # 点击删除
        coverage.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        coverage.get_find_message()
        sleep(1)
        coveragerdata = coverage.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        assert (
                coveragerdata != coveragedata1
        ), f"删除后的数据{coveragerdata}，删除前的数据{coveragedata1}"
        assert not coverage.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_coverage_addweeksuccess2(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        start = "2027/08/21 00:00:00"
        end = "2028/07/21 00:00:00"
        coverage.click_add_button()

        # 点击资源
        coverage.click_button(
            '//div[@id="2ssy7pog-1nb7"]//i'
        )
        # 勾选框
        random_int = random.randint(1, 8)
        sleep(1)
        coverage.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
        sleep(1)
        coverage.click_button(
            '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = coverage.get_find_element_xpath(
            '//div[@id="2ssy7pog-1nb7"]//input'
        ).get_attribute("value")
        coverage.enter_texts(f'//div[@id="9la8xi09-07ws"]//input', 3)

        # 时序
        coverage.enter_texts(
            '//div[@id="tg89jocr-6to2"]//input', f"{start};{end}"
        )
        chronology = coverage.get_find_element_xpath(
            '//div[@id="tg89jocr-6to2"]//input'
        ).get_attribute("value")

        # 资源量
        coverage.enter_texts('//div[@id="k0z05daz-8tok"]//input', "4")
        resources = coverage.get_find_element_xpath(
            '//div[@id="k0z05daz-8tok"]//input'
        ).get_attribute("value")

        sleep(1)
        coverage.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        coverage.wait_for_loading_to_disappear()
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        addcoverage = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addstart = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        addend = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        addchronology = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        addresources = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[8]'
        ).text
        assert (
            resource == addcoverage
            and start == addstart
            and end == addend
            and chronology == addchronology
            and resources == addresources
        )
        assert not coverage.has_fail_message()

    @allure.story("添加测试数据")
    # @pytest.mark.run(order=1)
    def test_coverage_addweeksuccess3(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        start = "2027/08/21 00:00:00"
        end = "2028/07/21 00:00:00"
        coverage.click_add_button()

        # 点击资源
        coverage.click_button(
            '//div[@id="2ssy7pog-1nb7"]//i'
        )
        sleep(1)
        coverage.click_button(
            '(//td[.//span[text()="A"]][./preceding-sibling::td//span])[1]/preceding-sibling::td//span'
        )
        sleep(1)
        coverage.click_button(
            '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = coverage.get_find_element_xpath(
            '//div[@id="2ssy7pog-1nb7"]//input'
        ).get_attribute("value")
        coverage.enter_texts(f'//div[@id="9la8xi09-07ws"]//input', 3)

        # 时序
        coverage.enter_texts(
            '//div[@id="tg89jocr-6to2"]//input', f"{start};{end}"
        )
        chronology = coverage.get_find_element_xpath(
            '//div[@id="tg89jocr-6to2"]//input'
        ).get_attribute("value")

        # 资源量
        coverage.enter_texts('//div[@id="k0z05daz-8tok"]//input', "4")
        resources = coverage.get_find_element_xpath(
            '//div[@id="k0z05daz-8tok"]//input'
        ).get_attribute("value")

        sleep(1)
        coverage.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        coverage.wait_for_loading_to_disappear()
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        addcoverage = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        addstart = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[3]'
        ).text
        addend = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[4]'
        ).text
        addchronology = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[7]'
        ).text
        addresources = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[8]'
        ).text
        assert (
            resource == addcoverage
            and start == addstart
            and end == addend
            and chronology == addchronology
            and resources == addresources
        )
        assert not coverage.has_fail_message()

    @allure.story("取消删除数据")
    # @pytest.mark.run(order=1)
    def test_coverage_delcancel(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage

        # 定位第一行
        coverage.click_button(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        )
        coveragedata1 = coverage.get_find_element_xpath(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        ).text
        coverage.click_del_button()  # 点击删除
        sleep(1)
        # 点击取消
        coverage.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="取消"]')
        sleep(1)
        # 定位第一行
        coveragedata = coverage.get_find_element_xpath(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        ).text
        assert coveragedata1 == coveragedata, f"预期{coveragedata}"
        assert not coverage.has_fail_message()

    @allure.story("刷新成功")
    # @pytest.mark.run(order=1)
    def test_coverage_refreshsuccess(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        coverage.wait_for_loading_to_disappear()
        # 覆盖日历筛选框输入123
        coverage.enter_texts(
            '//div[span[text()=" 资源代码"]]/following-sibling::div//input',
            "123",
        )
        coverage.click_ref_button()
        coveragetext = coverage.get_find_element_xpath(
            '//div[span[text()=" 资源代码"]]/following-sibling::div//input'
        ).text
        assert coveragetext == "", f"预期{coveragetext}"
        assert not coverage.has_fail_message()

    @allure.story("查询资源成功")
    # @pytest.mark.run(order=1)
    def test_coverage_selectcodesuccess(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage

        resource = coverage.get_find_element_xpath('(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[2]/td[2]').text

        # 点击查询
        coverage.click_sel_button()
        sleep(1)
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
        # 点击覆盖日历代码
        coverage.click_button('//div[text()="资源代码" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击比较关系框
        coverage.click_button(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[5]//input'
        )
        sleep(1)
        # 点击=
        coverage.click_button('//div[text()="=" and contains(@optid,"opt_")]')
        sleep(1)
        # 点击输入数值
        coverage.enter_texts(
            '(//div[@class="vxe-table--render-wrapper"])[3]/div[1]/div[2]//tr[1]/td[6]//input',
            resource,
        )
        sleep(3)

        # 点击确认
        coverage.click_button('(//div[@class="demo-drawer-footer"])[2]/button[2]')
        sleep(2)
        # 定位第一行
        coveragecode = coverage.get_find_element_xpath(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        ).text
        assert coveragecode == resource
        assert not coverage.has_fail_message()

    @allure.story("修改覆盖日历资源成功")
    # @pytest.mark.run(ordr=1)
    def test_coverage_editcodesuccess(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        coverage.wait_for_loading_to_disappear()
        # 定位第一行
        coverage.click_button(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        )
        # 点击修改按钮
        coverage.click_edi_button()

        # 点击资源
        coverage.click_button(
            '//div[@id="2zfqnpsf-3nsq"]//i'
        )
        # 勾选框
        random_int = random.randint(1, 8)
        coverage.click_button(f'(//span[@class="vxe-cell--checkbox"])[{random_int}]')
        coverage.click_button(
            '(//div[@class="h-40px flex-justify-end vxe-modal-footer1 flex-align-items-end b-t-s-d9e3f3"])[2]/button[1]'
        )
        sleep(1)
        # 获取勾选的资源代码
        resource = coverage.get_find_element_xpath(
            '//div[@id="2zfqnpsf-3nsq"]//input'
        ).get_attribute("value")

        coverage.click_button(
            '//div[@class="vxe-modal--footer"]//span[text()="确定"]'
        )
        coverage.wait_for_loading_to_disappear()
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        sleep(1)
        coverage.click_button(
            '//span[text()=" 更新时间"]/following-sibling::div'
        )
        adddata = coverage.get_find_element_xpath(
            f'(//span[text()="{resource}"])[1]/ancestor::tr[1]/td[2]'
        ).text
        assert adddata == resource
        assert not coverage.has_fail_message()

    @allure.story("删除数据成功，删除布局成功")
    # @pytest.mark.run(order=1)
    def test_coverage_delsuccess(self, login_to_coverage):
        driver = login_to_coverage  # WebDriver 实例
        coverage = Coverage(driver)  # 用 driver 初始化 Coverage
        layout = "测试布局A"
        coverage.wait_for_loading_to_disappear()
        # 定位第一行
        coverage.click_button(
            '(//div[@id="canvasGird0"]//table[@class="vxe-table--body"])[1]//tr[1]/td[2]'
        )
        coveragedata1 = coverage.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        coverage.click_del_button()  # 点击删除
        coverage.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        coverage.get_find_message()
        sleep(1)
        coveragedata = coverage.get_find_element_xpath(
            '(//span[contains(text(),"条记录")])[1]'
        ).text
        # 获取目标 div 元素，这里的目标是具有特定文本的 div
        target_div = coverage.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )

        # 获取父容器下所有 div
        # 这一步是为了确定目标 div 在其父容器中的位置
        parent_div = coverage.get_find_element_xpath(
            f'//div[@class="tabsDivItemCon" and ./div[text()=" {layout} "]]'
        )
        all_children = parent_div.find_elements(By.XPATH, "./div")

        # 获取目标 div 的位置索引（从0开始）
        # 这里是为了后续操作，比如点击目标 div 相关的按钮
        index = all_children.index(target_div)
        print(f"目标 div 是第 {index + 1} 个 div")  # 输出 3（如果从0开始则是2）
        sleep(2)
        coverage.click_button(
            f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]//i'
        )
        # 根据目标 div 的位置，点击对应的“删除布局”按钮
        coverage.click_button(f'(//li[text()="删除布局"])[{index + 1}]')
        sleep(2)
        # 点击确认删除的按钮
        coverage.click_button('//div[@class="ivu-modal-confirm-footer"]//span[text()="确定"]')
        # 等待一段时间，确保删除操作完成
        sleep(1)

        # 再次查找页面上是否有目标 div，以验证是否删除成功
        after_layout = driver.find_elements(
            By.XPATH, f'//div[@class="tabsDivItemCon"]/div[text()=" {layout} "]'
        )
        assert (
            coveragedata != coveragedata1 and 0 == len(after_layout)
        ), f"删除后的数据{coveragedata}，删除前的数据{coveragedata1}"
        assert not coverage.has_fail_message()
