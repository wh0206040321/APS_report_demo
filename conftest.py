import subprocess
import allure
from allure_commons.types import AttachmentType

import pytest
import os
import re
import shutil
import logging
import locale
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from Utils.driver_manager import create_driver, safe_quit, all_driver_instances
from Utils.data_driven import DateDriver
from Utils.screenshot_helper import capture_and_attach
from Utils.screenshot_helper import is_driver_alive
from Utils.driver_manager import cleanup_all_drivers
from Utils.mail_helper import send_test_failure_email
from Pages.base_page import BasePage
from pathlib import Path

test_failures = []
# 存储第一次失败的测试用例
first_time_failures = {}

# 路径配置
REPORT_DIR = os.path.abspath("report")
LOG_DIR = os.path.join(REPORT_DIR, "log")
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "test.log")
try:
    # 设置locale为中文环境
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except locale.Error:
    # 如果设置失败，静默跳过
    pass

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 设置日志记录级别为INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # 定义日志记录的格式
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),  # 将日志写入文件，指定编码为utf-8
        logging.StreamHandler()  # 同时将日志输出到控制台
    ],
    encoding='utf-8'  # 整体配置的编码设置为utf-8
)
logger = logging.getLogger(__name__)  # 创建一个日志记录器，用于记录当前模块的日志


def capture_and_attach(driver, test_name: str, recipient: str = None):
    """
       截图并保存到指定目录，同时附加到 Allure 报告，返回文件路径。
    """
    screenshot_dir = os.path.abspath("report/screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{id(driver)}_{timestamp}.png"
    file_path = os.path.join(screenshot_dir, filename)

    # 保存截图到文件
    driver.save_screenshot(file_path)
    logger.info(f"[{test_name}] 截图已保存：{file_path}")

    # ✅ 附加到 Allure 报告
    with open(file_path, "rb") as f:
        allure.attach(f.read(), name=test_name, attachment_type=AttachmentType.PNG)

    # 如果需要，可以在这里调用邮件发送逻辑
    if recipient:
        # send_test_failure_email(...) 或者其他逻辑
        pass

    # 返回文件路径，方便外部调用打印
    return file_path

# 公共截图函数
def try_capture(test_name: str):
    for driver in list(all_driver_instances.values()):
        alive = isinstance(driver, WebDriver) and is_driver_alive(driver)
        logger.info(f"[DEBUG] try_capture for {test_name}, driver_id={id(driver)}, alive={alive}")
        if alive:
            try:
                file_path = capture_and_attach(driver, test_name, recipient="1121470915@qq.com")
                logger.info(f"[DEBUG] 截图成功: {test_name}, 文件路径: {file_path}")
            except Exception as e:
                logger.warning(f"[DEBUG] 截图失败: {test_name}, error={e}")


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """
    fixture 初始化阶段报错时截图
    """
    outcome = yield
    if outcome.excinfo is not None:
        test_name = sanitize_filename(request.node.nodeid)
        logger.warning(f"[DEBUG] fixture_setup failed: {fixturedef.argname}")
        try_capture(test_name)

@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_post_finalizer(fixturedef, request):
    """
    fixture 结束阶段报错时截图（比如 scope="module" 的 yield 后出错）
    """
    outcome = yield
    if outcome.excinfo is not None:
        test_name = sanitize_filename(request.node.nodeid)
        logger.warning(f"[DEBUG] fixture_teardown failed: {fixturedef.argname}")
        try_capture(test_name)

def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """测试会话开始前清理截图目录"""
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    在每个测试项执行后生成报告，记录第一次失败并截图
    """
    outcome = yield
    report = outcome.get_result()

    test_name = sanitize_filename(item.nodeid.split("::")[-1])
    test_id = item.nodeid

    if report.when == "call":
        if report.failed:
            if test_id not in first_time_failures:
                first_time_failures[test_id] = {
                    'name': test_name,
                    'failed': True,
                    'rerun': False
                }
                logger.info(f"📝 记录第一次失败: {test_name}")
            elif hasattr(item, 'execution_count') and item.execution_count > 1:
                first_time_failures[test_id]['rerun'] = True
                if test_name not in test_failures:
                    test_failures.append(test_name)
                    logger.info(f"❌ 重试后仍然失败: {test_name}")
        else:
            if test_id in first_time_failures and hasattr(item, 'execution_count') and item.execution_count > 1:
                logger.info(f"✅ 重试后成功: {test_name}")
                del first_time_failures[test_id]

    # 覆盖 setup/call/teardown 阶段失败
    if report.failed and report.when in ("setup", "call", "teardown"):
        logger.info(f"[DEBUG] {test_name} failed at {report.when}")
        try_capture(test_name)


    # # 原有的截图逻辑
    # if report.when == "call" and report.failed:
    #     for driver in list(all_driver_instances.values()):
    #         # 检查实例是否为WebDriver类型
    #         if isinstance(driver, WebDriver):
    #             # debug信息：判断driver是否存活
    #             logging.debug(f"[{test_name}] 正在判断 driver: {id(driver)} 是否存活")
    #             # 如果driver已退出，则记录警告并跳过截图操作
    #             if not is_driver_alive(driver):
    #                 logging.warning(f"[{test_name}] driver {id(driver)} 已退出，跳过截图")
    #                 continue
    #             try:
    #                 # 尝试执行截图并附加到报告中，同时指定邮件接收方
    #                 capture_and_attach(driver, test_name, recipient="1121470915@qq.com")
    #             except Exception as e:
    #                 # 如果截图失败，记录警告信息
    #                 logger.warning(f"自动截图失败：{e}")


@pytest.fixture(scope="class")
def class_driver(request):
    """
    为每个测试类提供一个WebDriver实例

    参数:
    request - 当前测试请求对象
    """
    driver_path = DateDriver().driver_path
    driver = create_driver(driver_path)
    driver.set_window_size(1920, 1080)

    request.cls.driver = driver
    request.instance.driver = driver

    yield driver
    safe_quit(driver)


@pytest.fixture
def function_driver():
    """
    为每个测试函数提供一个WebDriver实例
    """
    driver_path = DateDriver().driver_path
    driver = create_driver(driver_path)
    yield driver
    safe_quit(driver)


@pytest.fixture(scope="module")
def module_driver():
    driver_path = DateDriver().driver_path
    driver = create_driver(driver_path)
    driver.set_window_size(1920, 1080)
    try:
        yield driver
    except Exception:
        try_capture("module_driver_teardown_failed")
        raise
    finally:
        safe_quit(driver)


def pytest_sessionfinish(session, exitstatus):
    """
    pytest 会话结束时自动发送邮件报告，同时自动部署到 GitHub Pages
    """
    # 处理最终失败列表：只包含那些重试后仍然失败的用例
    final_failures = []
    for test_id, failure_info in first_time_failures.items():
        if failure_info['rerun']:  # 只有重试后仍然失败的
            final_failures.append(failure_info['name'])

    # 更新全局的test_failures
    global test_failures
    test_failures = final_failures

    # 🚨 判断当前是否为 Git 仓库
    if not Path(".git").exists():
        logging.warning("⚠️ 当前目录不是 Git 仓库，跳过自动部署")
        return

    allure_output_dir = Path("report/allure_report")
    docs_dir = Path("docs")
    # ✅ 链接用于邮件
    report_link = "https://wh0206040321.github.io/APS_report_demo/"

    # ✅ 生成 Allure 静态报告
    os.system(f"allure generate report/allure_results -o {str(allure_output_dir)} --clean")

    # ✅ 构造 HTML 邮件内容
    if test_failures:
        # ✅ 去重失败用例
        unique_failures = list(dict.fromkeys(test_failures))
        failure_count = len(test_failures)
        total_count = session.testscollected
        pass_count = total_count - failure_count
        pass_rate = round((pass_count / total_count) * 100, 2)  # 保留两位小数
        failure_items = "".join(f"<li>{name}</li>" for name in unique_failures)
        body = f"""
        <html>
        <body>
            <h2>❌ 以下测试用例执行失败：</h2>
            <p>总测试用例数量: <strong>{total_count}</strong></p>
            <p>失败用例数量: <strong>{failure_count}</strong></p>
            <p>通过率: <strong>{pass_rate}%</strong></p>
            <ul>{failure_items}</ul>
            <p>📎 点击下方按钮查看详细测试报告：</p>
            <a href="{report_link}" style="display:inline-block;padding:10px 20px;background:#dc3545;color:#fff;text-decoration:none;border-radius:5px;">查看报告</a>
        </body>
        </html>
        """
        subject = "✅ 自动化测试演示环境执行完毕 - 失败汇总"
    else:
        total_count = session.testscollected
        pass_rate = 100.0
        body = f"""
        <html>
        <body>
            <h2>🎉 恭喜！本轮测试全部通过，无失败用例。</h2>
            <p>总测试用例数量: <strong>{total_count}</strong></p>
            <p>失败用例数量: <strong>0</strong></p>
            <p>通过率: <strong>{pass_rate}%</strong></p>
            <p>📎 点击下方按钮查看完整测试报告：</p>
            <a href="{report_link}" style="display:inline-block;padding:10px 20px;background:#28a745;color:#fff;text-decoration:none;border-radius:5px;">查看报告</a>
        </body>
        </html>
        """
        subject = "✅ 自动化测试演示环境全部通过"

    # ✅ 发送 HTML 邮件
    send_test_failure_email(
        subject=subject,
        body=body,
        to_emails=["1121470915@qq.com"],
        html=True
    )

    # ✅ 清理残留浏览器实例
    cleanup_all_drivers()
    logging.info("✅ 所有残留浏览器已关闭")

    # ✅ 部署报告到 GitHub Pages
    try:
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
            logging.info("🧹 已清空旧的 docs/ 目录")

        shutil.copytree(allure_output_dir, docs_dir)
        logging.info(f"📦 report/allure_report 文件数：{len(list(allure_output_dir.rglob('*')))}")
        logging.info(f"📦 docs/ 文件数：{len(list(docs_dir.rglob('*')))}")

        # ✅ 添加 .nojekyll 文件
        Path("docs/.nojekyll").touch()
        logging.info("✅ 已复制报告并添加 .nojekyll 文件")

        compare_file_counts(allure_output_dir, docs_dir)

        # ✅ 检查关键文件是否存在
        for file in ["index.html", "app.js", "styles.css"]:
            if not (docs_dir / file).exists():
                logging.warning(f"❌ 缺失关键文件：{file}")
            else:
                logging.info(f"✅ 存在关键文件：{file}")

        # ✅ 添加并提交 docs/
        subprocess.run(["git", "add", str(Path("docs").resolve())], check=True)

        # ✅ 提交变更（忽略无变更错误）
        subprocess.run(["git", "commit", "-m", "自动更新 Allure 报告"], check=False)

        # ✅ 添加空提交，确保触发构建
        subprocess.run(["git", "commit", "--allow-empty", "-m", "强制触发 GitHub Pages 构建"], check=False)

        # ✅ 推送到远程
        result = subprocess.run(["git", "push", "demo", "main"], capture_output=True, text=True)
        if result.returncode != 0:
            logging.warning(f"🚨 Git push 失败：{result.stderr}")
        else:
            logging.info("✅ Git push 成功")

        logging.info("✅ Allure 报告已自动部署到 GitHub Pages")

    except Exception as e:
        logging.warning(f"🚨 GitHub Pages 部署失败：{e}")


def compare_file_counts(src: Path, dst: Path):
    src_files = set(f.relative_to(src) for f in src.rglob("*") if f.is_file())
    dst_files = set(f.relative_to(dst) for f in dst.rglob("*") if f.is_file())
    diff = src_files.symmetric_difference(dst_files)
    if diff:
        logging.warning(f"❌ 报告文件不一致：{len(diff)} 个差异")
        for f in diff:
            logging.warning(f"↪️ 差异文件：{f}")
    else:
        logging.info("✅ 报告文件完全一致")