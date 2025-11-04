import os
import logging
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
import allure
from Utils.mail_helper import send_test_failure_email
from Utils.path_helper import get_report_dir


# noinspection PyUnresolvedReferences
def is_driver_alive(driver: WebDriver) -> bool:
    """
    检查WebDriver实例是否正常运行。

    Args:
        driver (WebDriver): 需要检查的WebDriver实例。

    Returns:
        bool: 如果driver的service属性存在且其process属性不为空，并且process的poll方法返回None，表明driver正在运行，返回True；否则返回False。
    """
    try:
        return hasattr(driver, "service") and driver.service.process and driver.service.process.poll() is None
    except Exception:
        return False


def capture_and_attach(driver: WebDriver, test_name: str, recipient: str = None):
    """
    截取WebDriver的当前屏幕并附加到Allure报告中，如果指定接收者，还会发送包含截图的邮件。

    Args:
        driver (WebDriver): 用于截屏的WebDriver实例。
        test_name (str): 测试用例的名称，用于文件命名和日志信息。
        recipient (str, optional): 如果提供了接收者邮箱地址，将发送测试失败邮件。默认为None。
    """
    if getattr(driver, "_email_sent", False):
        logging.debug(f"[{test_name}] 邮件已发送，跳过发送")
        return
    driver._email_sent = True
    if getattr(driver, "_has_screenshot", False):
        logging.debug(f"[{test_name}] driver {id(driver)} 已截过图，跳过")
        return
    driver._has_screenshot = True

    if not is_driver_alive(driver):
        logging.warning(f"[{test_name}] Driver ({id(driver)}) 已退出，跳过截图")
        return

    try:
        # 确保截图保存的目录存在
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = get_report_dir("screenshots")
        filepath = os.path.join(folder, f"{test_name}_{id(driver)}_{timestamp}.png")


        # 尝试保存截图
        if not driver.save_screenshot(filepath):
            logging.warning(f"[{test_name}] 无法保存截图，driver 返回 False")
            return

        logging.info(f"[{test_name}] 截图已保存：{filepath}")

        # 将截图附加到Allure报告
        allure.attach.file(
            filepath,
            name=f"{test_name}_failure",
            attachment_type=allure.attachment_type.PNG
        )

        # 将页面源代码附加到Allure报告
        page_source = driver.page_source
        allure.attach(
            page_source,
            name=f"{test_name}_source",
            attachment_type=allure.attachment_type.HTML
        )

        # 如果提供了接收者邮箱，发送测试失败邮件
        # if recipient:
        #     send_test_failure_email(
        #         subject=f"[自动化测试失败] {test_name}",
        #         body=f"测试失败截图见附件。\n用例名称：{test_name}",
        #         to_emails=[recipient],
        #         attachment_path=filepath
        #     )

    except Exception as e:
        logging.warning(f"[{test_name}] 截图或邮件发送失败：{e}")


