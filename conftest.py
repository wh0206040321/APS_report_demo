import subprocess
import allure
from allure_commons.types import AttachmentType
import time
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
from Utils.screenshot_helper import is_driver_alive
from Utils.driver_manager import cleanup_all_drivers
from Utils.mail_helper import send_test_failure_email
from Pages.base_page import BasePage
from pathlib import Path
from Utils.self_healing_driver import SelfHealingDriver

from Utils.video_recorder import video_recorder

# 存储重试状态的字典
retry_video_started = {}

test_failures = []
# 存储第一次失败的测试用例
first_time_failures = {}
# 存储每个测试用例的重试状态
retries = {}

# 路径配置
REPORT_DIR = os.path.abspath("report")
LOG_DIR = os.path.join(REPORT_DIR, "log")
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "test.log")
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except locale.Error:
    pass

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ],
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def capture_and_attach(driver, test_name: str, recipient: str = None):
    """截图并保存到指定目录，同时附加到 Allure 报告"""
    screenshot_dir = os.path.abspath("report/screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    # 加入时间戳和随机数，确保文件名唯一
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = sanitize_filename(test_name)
    random_suffix = str(int(time.time() * 1000))  # 用当前时间戳的一部分作为唯一标识
    filename = f"{clean_name}_{timestamp}_{random_suffix}.png"
    file_path = os.path.join(screenshot_dir, filename)

    driver.save_screenshot(file_path)
    logger.info(f"[{clean_name}] 截图已保存：{file_path}")
    logger.info(f"[{clean_name}] 截图时间：{timestamp}")

    with open(file_path, "rb") as f:
        allure.attach(f.read(), name=f"{clean_name}_{timestamp}", attachment_type=AttachmentType.PNG)

    return file_path


def try_capture(test_name: str):
    """尝试对所有活跃的 WebDriver 实例进行截图"""
    for driver in list(all_driver_instances.values()):
        alive = isinstance(driver, WebDriver) and is_driver_alive(driver)
        logger.info(f"[DEBUG] try_capture for {test_name}, driver_id={id(driver)}, alive={alive}")
        if alive:
            try:
                file_path = capture_and_attach(driver, test_name, recipient="1121470915@qq.com")
                logger.info(f"[DEBUG] 截图成功: {test_name}, 文件路径: {file_path}")
            except Exception as e:
                logger.warning(f"[DEBUG] 截图失败: {test_name}, error={e}")


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)


# ==================== 每个测试 setup 阶段都启动录屏 ====================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    outcome = yield

    test_name = sanitize_filename(item.nodeid.split("::")[-1])

    # 启动录屏前检查是否已经在录制
    if not video_recorder.recording:
        if all_driver_instances:
            driver = list(all_driver_instances.values())[-1]
            try:
                video_recorder.start(driver, test_name)  # 启动录屏
                logger.info(f"🎬 测试开始，启动录屏: {test_name}")
            except Exception as e:
                logger.warning(f"⚠️ 启动录屏失败: {test_name}, error={e}")
    else:
        logger.info(f"🎬 录屏已在进行中，跳过启动: {test_name}")


# ==================== 测试报告钩子 ====================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    test_name = sanitize_filename(item.nodeid.split("::")[-1])

    # 只在测试失败时执行
    if report.when == "call" and report.failed:
        # 确保停止录屏并处理失败的录制
        try:
            if video_recorder.recording:
                video_path = video_recorder.stop()

                logger.info(f"🛑 停止录屏: {test_name}，录制停止")

                # =========================
                # 添加视频到 Allure
                # =========================
                if video_path and os.path.exists(video_path):
                    allure.attach.file(
                        video_path,
                        name=f"{test_name}_video",
                        attachment_type=allure.attachment_type.MP4
                    )

                    logger.info(f"🎥 视频已附加到 Allure: {video_path}")

        except Exception as e:
            logger.warning(f"⚠️ 停止录屏失败: {test_name}, error={e}")

        # 记录第一次失败并准备重试
        if test_name not in first_time_failures:
            first_time_failures[test_name] = {"failed": True, "rerun": False}
            logger.info(f"❌ 第一次失败: {test_name}，准备重新录制视频")

            # 确保重新启动录制
            if all_driver_instances:
                driver = list(all_driver_instances.values())[-1]
                try:
                    video_recorder.start(driver, test_name)  # 重新开始录制
                    logger.info(f"🎬 测试开始，重新启动录屏: {test_name}")
                except Exception as e:
                    logger.warning(f"⚠️ 启动录屏失败: {test_name}, error={e}")
        else:
            first_time_failures[test_name]["failed"] = True

    # ✅ 测试成功后删除视频
    elif report.when == "call" and report.passed:
        logger.info(f"✅ 用例成功: {test_name}，删除视频")
        # 成功时也先停止录屏
        video_path = None
        # 成功时也先停止录屏
        if video_recorder.recording:
            video_path = video_recorder.stop()

        # 标记为已重试
        if test_name in first_time_failures and first_time_failures[test_name]["failed"]:
            first_time_failures[test_name]["rerun"] = True

        # 删除视频文件（仅在成功的情况下）
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"🗑️ 已删除成功用例视频: {video_path}")
            except Exception as e:
                logger.warning(f"⚠️ 删除视频失败: {test_name}, error={e}")
        else:
            logger.warning(f"⚠️ 视频文件不存在: {video_path}")

    # ============================
    # 任意阶段失败截图
    # ============================
    if report.failed and report.when in ("setup", "call", "teardown"):
        try_capture(test_name)


# ==================== Fixture 钩子 ====================
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """fixture 初始化阶段报错时截图"""
    outcome = yield
    if outcome.excinfo is not None:
        test_name = sanitize_filename(request.node.nodeid)
        logger.warning(f"[DEBUG] fixture_setup failed: {fixturedef.argname}")
        try_capture(test_name)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_post_finalizer(fixturedef, request):
    """fixture 结束阶段报错时截图"""
    outcome = yield
    if outcome.excinfo is not None:
        test_name = sanitize_filename(request.node.nodeid)
        logger.warning(f"[DEBUG] fixture_teardown failed: {fixturedef.argname}")
        try_capture(test_name)


# ==================== 会话钩子 ====================

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """测试会话开始前清理截图目录"""
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # 🟢 新增：清理视频目录（每次运行 pytest 时清空）
    video_dir = os.path.abspath("report/videos")
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
        logger.info("🧹 已清除上一次运行的视频文件")
    os.makedirs(video_dir, exist_ok=True)


# ==================== Fixtures ====================

@pytest.fixture(scope="class")
def class_driver(request):
    driver_path = DateDriver().driver_path
    raw_driver = create_driver(driver_path)
    driver = SelfHealingDriver(raw_driver)
    driver.set_window_size(1920, 1080)

    request.cls.driver = driver
    request.instance.driver = driver

    yield driver
    safe_quit(driver)


@pytest.fixture
def function_driver(request):
    driver_path = DateDriver().driver_path
    raw_driver = create_driver(driver_path)
    driver = SelfHealingDriver(raw_driver)

    yield driver
    safe_quit(driver)


@pytest.fixture(scope="module")
def module_driver(request):
    driver_path = DateDriver().driver_path
    raw_driver = create_driver(driver_path)
    driver = SelfHealingDriver(raw_driver)
    driver.set_window_size(1920, 1080)
    try:
        yield driver
    except Exception:
        try_capture("module_driver_teardown_failed")
        raise
    finally:
        safe_quit(driver)


# ==================== 会话结束处理 ====================

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


def pytest_sessionfinish(session, exitstatus):
    """pytest 会话结束时生成报告、发送邮件；有 Git 时再尝试部署 GitHub Pages"""

    # 处理最终失败列表：只包含那些重试后仍然失败的用例
    final_failures = []
    for test_id, failure_info in first_time_failures.items():
        # 如果该用例失败并且有标记为重试成功的记录，则只加入仍然失败的用例
        if failure_info.get('failed', False) and not failure_info.get('rerun', False):
            final_failures.append(test_id)

    # 更新全局的test_failures
    global test_failures
    test_failures = final_failures

    allure_output_dir = Path("report/allure_report")
    docs_dir = Path("docs")
    report_link = "https://wh0206040321.github.io/APS_report_demo/"

    # 生成 Allure 静态报告（不依赖 Git）
    allure_cmd = shutil.which("allure")
    if allure_cmd:
        ret = os.system(f'"{allure_cmd}" generate report/allure_results -o {str(allure_output_dir)} --clean')
        if ret == 0:
            logging.info(f"✅ Allure 报告已生成：{allure_output_dir.resolve()}")
        else:
            logging.warning("⚠️ Allure 报告生成失败，请检查 Java / Allure 是否安装正确")
    else:
        logging.warning("⚠️ 未找到 allure 命令，跳过报告生成。可手动执行: allure serve report/allure_results")

    # 构造 HTML 邮件内容
    if test_failures:
        unique_failures = list(dict.fromkeys(test_failures))  # 去重
        failure_count = len(test_failures)
        total_count = session.testscollected
        pass_count = total_count - failure_count
        pass_rate = round((pass_count / total_count) * 100, 2) if total_count else 0
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
        subject = "自动化测试测试环境执行完毕 - 失败汇总"
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
        subject = "自动化测试测试环境全部通过"

    # 发送 HTML 邮件（不依赖 Git）
    try:
        send_test_failure_email(
            subject=subject,
            body=body,
            to_emails=["1121470915@qq.com"],
            html=True
        )
    except Exception as e:
        logging.warning(f"⚠️ 发送邮件失败：{e}")

    # 清理残留浏览器实例
    cleanup_all_drivers()
    logging.info("✅ 所有残留浏览器已关闭")

    # 没有 Git 仓库时，跳过 GitHub Pages 部署
    if not Path(".git").exists():
        logging.warning("⚠️ 当前目录不是 Git 仓库，跳过 GitHub Pages 自动部署")
        return

    # 部署报告到 GitHub Pages
    try:
        if not allure_output_dir.exists():
            logging.warning("⚠️ Allure 报告目录不存在，跳过部署")
            return

        if docs_dir.exists():
            shutil.rmtree(docs_dir)
            logging.info("🧹 已清空旧的 docs/ 目录")

        shutil.copytree(allure_output_dir, docs_dir)
        logging.info(f"📦 report/allure_report 文件数：{len(list(allure_output_dir.rglob('*')))}")
        logging.info(f"📦 docs/ 文件数：{len(list(docs_dir.rglob('*')))}")

        Path("docs/.nojekyll").touch()
        logging.info("✅ 已复制报告并添加 .nojekyll 文件")

        compare_file_counts(allure_output_dir, docs_dir)

        for file in ["index.html", "app.js", "styles.css"]:
            if not (docs_dir / file).exists():
                logging.warning(f"❌ 缺失关键文件：{file}")
            else:
                logging.info(f"✅ 存在关键文件：{file}")

        subprocess.run(["git", "add", str(Path("docs").resolve())], check=True)
        subprocess.run(["git", "commit", "-m", "自动更新 Allure 报告"], check=False)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "强制触发 GitHub Pages 构建"], check=False)

        result = subprocess.run(["git", "push", "demo", "main"], capture_output=True, text=True)
        if result.returncode != 0:
            logging.warning(f"🚨 Git push 失败：{result.stderr}")
        else:
            logging.info("✅ Git push 成功")
            logging.info("✅ Allure 报告已自动部署到 GitHub Pages")

    except Exception as e:
        logging.warning(f"🚨 GitHub Pages 部署失败：{e}")
