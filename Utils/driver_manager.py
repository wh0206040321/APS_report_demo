import os
import logging
from typing import Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Utils.path_helper import get_report_dir
from selenium.webdriver.chrome.options import Options
# 全局存储所有 WebDriver 实例
all_driver_instances = {}


def create_driver(driver_path: str, options: Optional[Options] = None) -> webdriver.Chrome:
    """
    根据指定的驱动路径创建一个Chrome浏览器实例。

    参数:
    - driver_path: str 驱动程序的文件路径。

    返回:
    - webdriver.Chrome: 创建的Chrome浏览器实例。
    """
    # 如果未传入 options，则使用默认配置
    if options is None:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 创建Chrome驱动服务
    service = Service(driver_path)
    # 初始化Chrome浏览器实例
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()  # 最大化浏览器窗口

    # 注册 driver 实例
    all_driver_instances[id(driver)] = driver
    return driver


def safe_quit(driver: webdriver.Chrome):
    """
    安全地关闭一个Chrome浏览器实例。

    参数:
    - driver: webdriver.Chrome 需要关闭的Chrome浏览器实例。
    """
    try:
        driver.quit()  # 尝试正常关闭浏览器
    except Exception as e:
        logging.error(f"关闭 driver 失败: {e}")  # 如果关闭失败，记录错误日志
    finally:
        # 自动从 all_driver_instances 中清理已退出的 driver
        all_driver_instances.pop(id(driver), None)
        logging.info(f"🛑 已从实例池移除并关闭 driver：{id(driver)}")  # 记录调试日志


def cleanup_all_drivers(verbose: Optional[bool] = True):
    """
    清理 all_driver_instances 中所有未释放的浏览器。
    会自动调用 safe_quit(driver)，并输出日志统计。
    """
    total = len(all_driver_instances)
    closed = 0

    for driver_id, driver in list(all_driver_instances.items()):
        try:
            safe_quit(driver)
            closed += 1
        except Exception as e:
            logging.warning(f"关闭 driver（id={driver_id}）失败：{e}")

    if verbose:
        logging.info(f"🌪️ cleanup_all_drivers 完成：共发现 {total} 个 driver，成功关闭 {closed} 个")


def capture_screenshot(driver: webdriver.Chrome, name: str) -> str:
    """
    捕获当前浏览器窗口的截图并保存。

    参数:
    - driver: webdriver.Chrome 需要截图的Chrome浏览器实例。
    - name: str 截图的名称，用于标识截图。

    返回:
    - str: 保存的截图文件路径。
    """
    # 生成截图的时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 定义截图保存的目录
    screenshot_dir = get_report_dir("screenshots")

    # 构造截图文件的完整路径
    filepath = os.path.join(screenshot_dir, f"{name}_{id(driver)}_{timestamp}.png")
    try:
        driver.save_screenshot(filepath)  # 尝试保存截图
    except Exception as e:
        logging.warning(f"截图失败：{e}")  # 如果截图失败，记录警告日志
    return filepath



