"""BasePage: 提供 Selenium 基础操作 + AI 自愈能力。

职责：
1. 常规页面操作（查找、点击、输入、跳转、关闭）
2. 失败后的兜底策略（视觉识别 + AI 定位器修复）
3. AI 行为统计与报告导出
"""
import inspect
# pages/base_page.py
import logging
from time import sleep
import json
import time
import os
import re
from Pages.base.base_ai_fix import ai_decide, clean_json_response

try:
    from airtest.core.api import exists, touch, Template
    AIRTEST_AVAILABLE = True
except ImportError:
    AIRTEST_AVAILABLE = False
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def _build_openai_client():
    """按需构建 OpenAI 客户端；未配置 key 时返回 None。"""
    if not OPENAI_AVAILABLE:
        return None

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


client = None


AI_LOCATOR_DB = "ai_data/optimized_locators.json"
os.makedirs("ai_data", exist_ok=True)


class BasePage:
    """所有页面对象的基础类。

    说明：
    - 将常用 UI 操作集中在这里，减少各个页面重复代码。
    - 在 Selenium 常规定位失败时，尝试视觉点击与 AI 自愈，提高脚本稳定性。
    """

    def __init__(self, driver):
        self.driver = driver

        # AI 调用统计：用于后续导出自愈效果报告。
        self._ai_stats = {
            "total_calls": 0,
            "success": 0,
            "fail": 0,
            "records": []
        }

        try:
            driver.maximize_window()
        except Exception:
            driver.set_window_size(1920, 1080)

    # ============================
    # ⭐ 统计器记录
    # ============================
    def _record_ai_event(self, event_type, original, new, success, reason):
        """记录一次 AI 调用结果（优化/修复）。"""
        self._ai_stats["total_calls"] += 1
        if success:
            self._ai_stats["success"] += 1
        else:
            self._ai_stats["fail"] += 1

        self._ai_stats["records"].append({
            "type": event_type,
            "original": original,
            "new": new,
            "success": success,
            "reason": reason,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    # ============================
    # ⭐ AI 优化定位器（已禁用 - 避免成功时请求 AI）
    # ============================
    def _ai_optimize_locator(self, by, value):
        """在定位成功后尝试让定位器更稳（已禁用，避免成功时请求 AI）"""
        # 注释掉原有逻辑，保持成功时不请求 AI
        # if client is None:
        #     return
        #
        # try:
        #     html = self.driver.page_source[:8000]
        #
        #     prompt = f"""
        # 你是一个自动化测试定位器优化 AI。
        #
        # 任务：根据页面 HTML 和当前定位器，生成一个更稳、更短、更不容易变化的定位器。
        #
        # 返回 JSON：
        # {{
        #     "optimized_locator": "新的 XPath 或 CSS"
        # }}
        #
        # HTML:
        # {html}
        #
        # 当前定位器:
        # {value}
        # """
        #
        #     res = client.chat.completions.create(
        #         model="deepseek-chat",
        #         messages=[{"role": "user", "content": prompt}]
        #     )
        #     data = json.loads(res.choices[0].message.content)
        #     new_loc = data.get("optimized_locator")
        #
        #     if new_loc and new_loc != value:
        #         logging.info(f"🤖 AI 优化定位器：{value} → {new_loc}")
        #         self._record_ai_event("optimize", value, new_loc, True, "optimize_success")
        #
        # except Exception as e:
        #     self._record_ai_event("optimize", value, None, False, f"optimize_fail: {e}")
        pass

    # ============================
    # ⭐ 视觉兜底
    # ============================
    def visual_click(self, image_path, threshold=0.7):
        """使用 Airtest 做图像匹配点击，作为 DOM 定位失败时的兜底方案。"""
        if not AIRTEST_AVAILABLE:
            logging.warning("未安装 airtest，跳过视觉兜底点击。")
            return False

        pos = exists(Template(image_path, threshold=threshold))
        if pos:
            touch(pos)
            logging.info(f"🎯 视觉识别点击成功：{image_path}")
            return True
        return False

    # ============================
    # ⭐ find_element（AI 自愈）
    # ============================
    def find_element(self, by, value, wait_time=10):
        """查找单个元素。

        流程：
        1) 正常 Selenium 定位
        2) 失败后尝试视觉点击兜底
        3) 再失败则调用 AI 生成新定位器并重试
        """
        logging.info(f"查找元素：{by} = {value}")

        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )

        except TimeoutException as e:
            logging.warning(f"❌ 未找到元素：{by} = {value}，等待超时 {wait_time}s")

            # 视觉兜底
            try:
                image_path = f"images/{value}.png"
                if os.path.exists(image_path) and self.visual_click(image_path):
                    return True
            except:
                pass

            # AI 修复定位器
            if not os.getenv("DEEPSEEK_API_KEY"):
                logging.warning("未配置 DEEPSEEK_API_KEY，跳过 AI 修复")
                raise e
            try:
                logging.info("[AI Agent] find_element 失败 → AI 修复中…")

                failed_locator = value
                ai_json = ai_decide(failed_locator, str(e))
                # 清理 JSON 格式
                cleaned_json = clean_json_response(ai_json)
                data = json.loads(cleaned_json)

                new_locator = data.get("locator")
                if not new_locator:
                    raise RuntimeError("AI 未返回 locator")

                logging.info(f"🤖 AI 修复成功：{value} → {new_locator}")

                self._record_ai_event("fix", value, new_locator, True, "find_fix_success")
                self._save_ai_fix_record(value, new_locator)

                if new_locator.startswith("//"):
                    new_by = By.XPATH
                else:
                    new_by = By.CSS_SELECTOR

                return WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((new_by, new_locator))
                )

            except Exception as ai_error:
                logging.error(f"AI 修复失败：{ai_error}")
                self._record_ai_event("fix", value, None, False, f"find_fix_fail: {ai_error}")
                raise e

    def finds_elements(self, by, value):
        """查找多个元素，并返回这些元素."""
        logging.info(f"查找元素：{by} = {value}")
        return self.driver.find_elements(by, value)

    # ============================
    # ⭐ 六层防御点击 + AI 修复
    # ============================
    def click(self, by_or_element, value=None, wait_time=10, retries=2):
        """
        更稳健的点击方法：支持定位符或 WebElement，自动处理 stale 元素、点击拦截等问题。
        最后兜底：视觉识别 + AI 修复定位器
        """
        element = None  # 初始化，供后续异常处理使用
        last_error = None  # 保存最后一次 Selenium 异常

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

            except ElementClickInterceptedException as e:
                last_error = e
                logging.warning("⚠️ 原生点击被拦截，尝试使用 JS 点击")
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    logging.info("✅ JS 点击成功")
                    return
                except Exception as js_error:
                    logging.warning(f"⚠️ JS 点击失败：{js_error}")
                    sleep(1)
                    continue

            except StaleElementReferenceException as e:
                last_error = e
                logging.warning(f"⚠️ 第 {attempt + 1} 次点击失败：元素过期，尝试重新定位")
                sleep(1)
                continue

            except TimeoutException as e:
                last_error = e
                logging.error(f"❌ 元素未在 {wait_time} 秒内变为可点击")
                # 不立即抛出，先尝试兜底方案
                break

            except Exception as e:
                last_error = e
                logging.warning(f"点击失败：{e}")
                if attempt == retries - 1:
                    # 重试用完，准备进入兜底方案
                    break
                sleep(1)

        # ========== 兜底方案开始 ==========

        # 第二层：视觉兜底点击（需存在 images/{value}.png）
        try:
            if value is not None:
                image_path = f"images/{value}.png"
                if os.path.exists(image_path) and self.visual_click(image_path):
                    logging.info("🎯 视觉识别点击成功")
                    return
        except:
            pass

        # 第三层：AI 生成新定位器并再次点击
        # 没有配置 API Key，跳过 AI
        if not os.getenv("DEEPSEEK_API_KEY"):
            logging.warning("未配置 DEEPSEEK_API_KEY，跳过 AI 修复")

            if last_error is not None:
                raise last_error

            raise RuntimeError("点击失败，且未配置 AI 修复")
        try:
            print("[AI Agent] click 失败，交给 AI 修复定位器…")

            if value is None:
                raise RuntimeError("AI 修复 click 需要原始 locator（by + value），不能使用 WebElement 调用 click()")

            failed_locator = value

            ai_json = ai_decide(failed_locator, "click failed")
            cleaned_json = clean_json_response(ai_json)
            data = json.loads(cleaned_json)

            new_locator = data.get("locator")
            if not new_locator:
                raise RuntimeError("AI 未返回 locator")

            logging.info(f"🤖 AI 修复成功，新点击定位器：{new_locator}")

            self._record_ai_event("fix", value, new_locator, True, "click_fix_success")

            if new_locator.startswith("//"):
                new_by = By.XPATH
            else:
                new_by = By.CSS_SELECTOR

            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((new_by, new_locator))
            )
            element.click()
            logging.info("✅ 点击成功（AI 修复后）")
            self._save_ai_fix_record(value, new_locator)
            return

        except Exception as e:
            logging.error(f"AI 修复失败：{e}")
            self._record_ai_event("fix", value, None, False, f"click_fix_fail: {e}")
            raise RuntimeError(f"点击失败（AI 也无法修复）：{e}")

    # ============================
    # ⭐ 输入 + AI 修复
    # ============================
    def enter_text(self, by, value, text, wait_time=10, retries=2):
        """向输入框写入文本，失败后尝试 AI 修复定位器。"""
        # 第一阶段：常规定位 + 输入，带重试。
        for attempt in range(retries):
            try:
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.visibility_of_element_located((by, value))
                )
                sleep(0.3)

                try:
                    element.clear()
                except:
                    # 部分控件 clear() 不稳定，降级为 JS 置空。
                    self.driver.execute_script("arguments[0].value = '';", element)

                element.send_keys(text)
                logging.info(f"✅ 输入成功：{text}")
                return

            except Exception as e:
                logging.warning(f"输入失败：{e}")
                if attempt < retries - 1:
                    sleep(1)
                    continue

                # 第二阶段：重试失败后，交给 AI 修复定位器。
                # 没有配置 API Key，跳过 AI，抛出原始输入异常
                if not os.getenv("DEEPSEEK_API_KEY"):
                    logging.warning("未配置 DEEPSEEK_API_KEY，跳过 AI 修复")
                    raise e
                print("[AI Agent] 输入失败，交给 AI 修复定位器…")
                try:
                    failed_locator = value
                    ai_json = ai_decide(failed_locator, str(e))
                    # 清理 JSON 格式
                    cleaned_json = clean_json_response(ai_json)
                    data = json.loads(cleaned_json)

                    new_locator = data.get("locator")
                    if not new_locator:
                        raise RuntimeError("AI 未返回 locator")

                    logging.info(f"🤖 AI 修复成功，新输入定位器：{new_locator}")

                    self._record_ai_event("fix", value, new_locator, True, "input_fix_success")

                    # 约定：以 // 开头视为 XPath，否则按 CSS 处理。
                    if new_locator.startswith("//"):
                        new_by = By.XPATH
                    else:
                        new_by = By.CSS_SELECTOR

                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.visibility_of_element_located((new_by, new_locator))
                    )
                    element.send_keys(text)
                    logging.info(f"✅ 输入成功（AI 修复后）：{text}")
                    self._save_ai_fix_record(value, new_locator)
                    return

                except Exception as ai_error:
                    self._record_ai_event("fix", value, None, False, f"input_fix_fail: {ai_error}")
                    raise e

        raise RuntimeError(f"输入失败：{by}={value} 多次尝试仍失败")

    # ============================
    # ⭐ 导出 AI 报告（HTML）
    # ============================
    def export_ai_report(self, path="report/ai_locator_report.html"):
        """将当前运行周期的 AI 统计导出为 HTML 报告。"""
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)

        total = self._ai_stats["total_calls"]
        success = self._ai_stats["success"]
        fail = self._ai_stats["fail"]
        success_rate = f"{(success / total * 100):.2f}%" if total else "0.00%"

        rows = []
        for r in self._ai_stats["records"]:
            rows.append(f"""
    <tr>
        <td>{r['timestamp']}</td>
        <td>{r['type']}</td>
        <td>{r['original']}</td>
        <td>{r['new'] or ''}</td>
        <td>{'✅' if r['success'] else '❌'}</td>
        <td>{r['reason']}</td>
    </tr>
    """)

        html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <title>AI 定位器修复与优化报告</title>
    <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; }}
    th {{ background: #f5f5f5; }}
    </style>
    </head>
    <body>
    <h2>AI 定位器修复与优化报告</h2>
    <p>总调用次数：{total}</p>
    <p>成功次数：{success}</p>
    <p>失败次数：{fail}</p>
    <p>成功率：{success_rate}</p>

    <table>
    <tr>
      <th>时间</th>
      <th>类型</th>
      <th>原始定位器</th>
      <th>新定位器</th>
      <th>结果</th>
      <th>原因</th>
    </tr>
    {''.join(rows)}
    </table>
    </body>
    </html>
    """

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        logging.info(f"📄 AI 定位器报告已生成：{path}")

    def _save_ai_fix_record(self, original, new):
        """保存 AI 修复记录到 ai_data/optimized_locators.json"""

        record = {
            "original": original,
            "new": new,
            "testcase": self._get_current_testcase(),
            "location": self._get_call_location(),
            "date": time.strftime("%Y-%m-%d"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 读取旧数据
        data = []
        if os.path.exists(AI_LOCATOR_DB):
            try:
                with open(AI_LOCATOR_DB, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []

        # 追加新记录
        data.append(record)

        # 写回文件
        with open(AI_LOCATOR_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"📌 AI 修复记录已写入 ai_data：{original} → {new}")

    def _get_current_testcase(self):
        """自动获取当前运行的 pytest 测试用例名称"""
        for frame in inspect.stack():
            filename = frame.filename
            if filename.endswith(".py") and ("test_" in filename or "/tests/" in filename.replace("\\", "/")):
                return os.path.basename(filename)
        return "unknown_testcase"

    def _get_call_location(self):
        """获取触发 AI 修复的代码位置（文件名 + 行号）"""
        frame = inspect.stack()[2]
        filename = os.path.basename(frame.filename)
        return f"{filename}:{frame.lineno}"

    # ============================
    # 其他通用方法
    # ============================
    def navigate_to(self, url):
        """导航到指定 URL。"""
        self.driver.get(url)

    def close(self):
        """关闭浏览器驱动."""
        self.driver.quit()

    def has_fail_message(self):
        """判断页面是否出现后端内部错误弹窗文案。"""
        mes = self.finds_elements(By.XPATH, '//div[@class="ivu-modal-content"]//div[text()=" 对不起,在处理您的请求期间,产生了一个服务器内部错误! "]')
        return bool(mes)  # 有元素返回 True，无元素返回 False
