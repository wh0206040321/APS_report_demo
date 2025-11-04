# pages/base_page.py
import logging
from time import sleep

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        try:
            driver.maximize_window()
        except Exception as e:
            print(f"⚠️ 无法最大化窗口：{e}")
            driver.set_window_size(1920, 1080)  # 使用默认分辨率

    def find_element(self, by, value, wait_time=10):
        """查找单个元素"""
        logging.info(f"查找元素：{by} = {value}")
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logging.warning(f"❌ 未找到元素：{by} = {value}，等待超时 {wait_time}s")
            raise

    def finds_elements(self, by, value):
        """查找多个元素，并返回这些元素."""
        logging.info(f"查找元素：{by} = {value}")
        return self.driver.find_elements(by, value)

    def click(self, by_or_element, value=None, wait_time=10, retries=2):
        """
        更稳健的点击方法：支持定位符或 WebElement，自动处理 stale 元素、点击拦截等问题。
        """
        for attempt in range(retries):
            try:
                if value is not None:
                    by = by_or_element
                    logging.info(f"点击元素：By = {by}, Value = {value}")
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((by, value))
                    )
                else:
                    logging.info("点击元素：WebElement 对象")
                    element = by_or_element

                element.click()
                logging.info("✅ 点击成功")
                return

            except ElementClickInterceptedException:
                logging.warning("⚠️ 原生点击被拦截，尝试使用 JS 点击")
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    logging.info("✅ JS 点击成功")
                    return
                except Exception as js_error:
                    logging.warning(f"⚠️ JS 点击失败：{js_error}")
                    sleep(1)
                    continue  # 下一轮重试

            except StaleElementReferenceException:
                logging.warning(f"⚠️ 第 {attempt + 1} 次点击失败：元素过期，尝试重新定位")
                sleep(1)
                continue  # 下一轮重试时重新定位

            except TimeoutException:
                logging.error(f"❌ 元素未在 {wait_time} 秒内变为可点击")
                raise TimeoutException(f"点击失败，找不到元素：{by_or_element} = {value}")

            except Exception as e:
                logging.warning(f"点击失败：{e}")
                if attempt == retries - 1:
                    raise Exception(f"点击失败：{e}")
                sleep(1)

        raise RuntimeError(f"点击失败：元素 {by_or_element} = {value} 多次尝试仍失败")

    def enter_text(self, by, value, text, wait_time=10):
        """在指定位置输入文本，等待元素可见后操作."""
        element = WebDriverWait(self.driver, wait_time).until(
            EC.visibility_of_element_located((by, value))
        )
        sleep(0.5)
        try:
            element.clear()
        except Exception as e:
            logging.warning(f"⚠️ clear() 清空失败：{e}，尝试使用 JS 清空")
            try:
                self.driver.execute_script("arguments[0].value = '';", element)
                logging.info("✅ JS 清空成功")
            except Exception as js_error:
                logging.warning(f"❌ JS 清空也失败：{js_error}")
        element.send_keys(text)

    def navigate_to(self, url):
        """导航到指定URL，若提供wait_for_element，则等待该元素加载完成."""
        self.driver.get(url)

    def close(self):
        """关闭浏览器驱动."""
        self.driver.quit()

    def has_fail_message(self):
        """获取服务器内部错误."""
        mes = self.finds_elements(By.XPATH, '//div[@class="ivu-modal-content"]//div[text()=" 对不起,在处理您的请求期间,产生了一个服务器内部错误! "]')
        return bool(mes)  # 有元素返回 True，无元素返回 False
