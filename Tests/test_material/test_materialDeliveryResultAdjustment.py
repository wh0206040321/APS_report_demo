# import logging
# import os
# from datetime import datetime
# from time import sleep
#
# import allure
# import pytest
# from selenium.webdriver import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
#
# from Pages.itemsPage.adds_page import AddsPages
# from Pages.itemsPage.login_page import LoginPage
# from Pages.materialPage.materialControlDefinition_page import MaterialControlDefinition
# from Utils.data_driven import DateDriver
# from Utils.driver_manager import create_driver, safe_quit, capture_screenshot
#
#
# @pytest.fixture  # (scope="class")这个参数表示整个测试类共用同一个浏览器，默认一个用例执行一次
# def login_to_materialDeliveryResultAdjustment():
#     driver = None
#     try:
#         """初始化并返回 driver"""
#         date_driver = DateDriver()
#         driver = create_driver(date_driver.driver_path)
#         driver.implicitly_wait(3)
#
#         # 初始化登录页面
#         page = LoginPage(driver)  # 初始化登录页面
#         url = date_driver.url
#         print(f"[INFO] 正在导航到 URL: {url}")
#         # 尝试访问 URL，捕获连接错误
#         for attempt in range(2):
#             try:
#                 page.navigate_to(url)
#                 break
#             except WebDriverException as e:
#                 capture_screenshot(driver, f"login_fail_{attempt + 1}")
#                 logging.warning(f"第 {attempt + 1} 次连接失败: {e}")
#                 driver.refresh()
#                 sleep(date_driver.URL_RETRY_WAIT)
#         else:
#             logging.error("连接失败多次，测试中止")
#             safe_quit(driver)
#             raise RuntimeError("无法连接到登录页面")
#
#         page.login(date_driver.username, date_driver.password, date_driver.planning)
#         list_ = ["计划运行", "方案管理", "交付计算结果调整"]
#         for v in list_:
#             page.click_button(f'(//span[text()="{v}"])[1]')
#         yield driver  # 提供给测试用例使用
#     finally:
#         if driver:
#             safe_quit(driver)
#
#
# @allure.feature("交付结果调整页用例")
# @pytest.mark.run(order=145)
# class TestSMaterialDeliveryResultAdjustmentPage:
#
#     @allure.story("新增直接点击保存不允许添加")
#     # @pytest.mark.run(order=1)
#     def test_materialDeliveryResultAdjustment_addfail1(self, login_to_materialDeliveryResultAdjustment):
#         driver = login_to_materialDeliveryResultAdjustment  # WebDriver 实例
#         material = MaterialControlDefinition(driver)  # 用 driver 初始化 MaterialControlDefinition
#         material.click_all_button("新增")
#         sleep(1)
#         material.click_confirm()
#         message = material.get_error_message()
#         assert message == "请填写表单必填项!"
#         assert not material.has_fail_message()
