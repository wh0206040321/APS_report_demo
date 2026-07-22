import inspect
import json
import logging
import os
import time
from playwright.sync_api import TimeoutError as PWTimeoutError, expect

# 复用你的 AI 修复逻辑（你需要把 ai_decide / clean_json_response 放到 base_ai_fix.py）
from Pages.base.base_ai_fix import ai_decide, clean_json_response

AI_LOCATOR_DB = "ai_data/optimized_locators.json"
os.makedirs("ai_data", exist_ok=True)


class PlaywrightBasePage:
    """Playwright 版本 BasePage（带 AI 自愈 + 常用方法封装）"""

    def __init__(self, page):
        self.page = page

        self._ai_stats = {
            "total_calls": 0,
            "success": 0,
            "fail": 0,
            "records": []
        }

    # ============================
    # ⭐ AI 统计记录
    # ============================
    def _record_ai_event(self, event_type, original, new, success, reason):
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
    # ⭐ 保存 AI 修复记录（JSON）
    # ============================
    def _save_ai_fix_record(self, original, new):
        record = {
            "original": original,
            "new": new,
            "testcase": self._get_current_testcase(),
            "location": self._get_call_location(),
            "date": time.strftime("%Y-%m-%d"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        data = []
        if os.path.exists(AI_LOCATOR_DB):
            try:
                with open(AI_LOCATOR_DB, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []

        data.append(record)

        with open(AI_LOCATOR_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"📌 AI 修复记录已写入 ai_data：{original} → {new}")

    # ============================
    # ⭐ 获取测试用例名称
    # ============================
    def _get_current_testcase(self):
        for frame in inspect.stack():
            filename = frame.filename
            if filename.endswith(".py") and ("test_" in filename or "/tests/" in filename.replace("\\", "/")):
                return os.path.basename(filename)
        return "unknown_testcase"

    # ============================
    # ⭐ 获取调用位置
    # ============================
    def _get_call_location(self):
        frame = inspect.stack()[2]
        filename = os.path.basename(frame.filename)
        return f"{filename}:{frame.lineno}"

    # ============================
    # ⭐ find（带 AI 自愈）
    # ============================
    def find(self, locator, timeout=5000):
        try:
            return self.page.locator(locator).first.wait_for(state="visible", timeout=timeout)

        except PWTimeoutError as e:
            logging.warning(f"❌ 未找到元素：{locator}")

            try:
                ai_json = ai_decide(locator, str(e))
                cleaned = clean_json_response(ai_json)
                data = json.loads(cleaned)

                new_locator = data.get("locator")
                if not new_locator:
                    raise RuntimeError("AI 未返回 locator")

                logging.info(f"🤖 AI 修复成功：{locator} → {new_locator}")

                self._record_ai_event("fix", locator, new_locator, True, "find_fix_success")
                self._save_ai_fix_record(locator, new_locator)

                return self.page.locator(new_locator).first.wait_for(state="visible", timeout=timeout)

            except Exception as ai_error:
                self._record_ai_event("fix", locator, None, False, f"find_fix_fail: {ai_error}")
                raise PWTimeoutError(f"定位失败（AI 也无法修复）：{locator}")

    # ============================
    # ⭐ click（带 AI 自愈）
    # ============================
    def click(self, locator, timeout=5000):
        try:
            self.page.locator(locator).click(timeout=timeout)
            return

        except Exception as e:
            logging.warning(f"⚠️ 点击失败：{locator} → 尝试 AI 修复")

            try:
                ai_json = ai_decide(locator, str(e))
                cleaned = clean_json_response(ai_json)
                data = json.loads(cleaned)

                new_locator = data.get("locator")
                if not new_locator:
                    raise RuntimeError("AI 未返回 locator")

                logging.info(f"🤖 AI 修复成功：{locator} → {new_locator}")

                self._record_ai_event("fix", locator, new_locator, True, "click_fix_success")
                self._save_ai_fix_record(locator, new_locator)

                self.page.locator(new_locator).click(timeout=timeout)
                return

            except Exception as ai_error:
                self._record_ai_event("fix", locator, None, False, f"click_fix_fail: {ai_error}")
                raise RuntimeError(f"点击失败（AI 也无法修复）：{locator}")

    # ============================
    # ⭐ fill（带 AI 自愈）
    # ============================
    def fill(self, locator, text, timeout=5000):
        try:
            self.page.locator(locator).fill(text, timeout=timeout)
            return

        except Exception as e:
            logging.warning(f"⚠️ 输入失败：{locator} → 尝试 AI 修复")

            try:
                ai_json = ai_decide(locator, str(e))
                cleaned = clean_json_response(ai_json)
                data = json.loads(cleaned)

                new_locator = data.get("locator")
                if not new_locator:
                    raise RuntimeError("AI 未返回 locator")

                logging.info(f"🤖 AI 修复成功：{locator} → {new_locator}")

                self._record_ai_event("fix", locator, new_locator, True, "fill_fix_success")
                self._save_ai_fix_record(locator, new_locator)

                self.page.locator(new_locator).fill(text, timeout=timeout)
                return

            except Exception as ai_error:
                self._record_ai_event("fix", locator, None, False, f"fill_fix_fail: {ai_error}")
                raise RuntimeError(f"输入失败（AI 也无法修复）：{locator}")

    # ============================
    # ⭐ click_text（点击文本）
    # ============================
    def click_text(self, text):
        self.page.get_by_text(text).click()

    # ============================
    # ⭐ click_button（按按钮名称点击）
    # ============================
    def click_button(self, name):
        self.page.get_by_role("button", name=name).click()

    # ============================
    # ⭐ fill_input（按输入框名称输入）
    # ============================
    def fill_input(self, name, text):
        self.page.get_by_role("textbox", name=name).fill(text)

    # ============================
    # ⭐ assert_text_visible（断言文本可见）
    # ============================
    def assert_text_visible(self, text, timeout=15000):
        expect(self.page.get_by_text(text)).to_be_visible(timeout=timeout)

    # ============================
    # ⭐ assert_not_url（断言 URL 不匹配）
    # ============================
    def assert_not_url(self, pattern, timeout=15000):
        expect(self.page).not_to_have_url(pattern, timeout=timeout)

    # ============================
    # ⭐ wait_network_idle（等待加载完成）
    # ============================
    def wait_network_idle(self):
        self.page.wait_for_load_state("networkidle")

    # ============================
    # ⭐ 登录封装
    # ============================
    def login(self, username, password):
        self.fill_input("请输入账户", username)
        self.fill_input("请输入密码", password)
        self.click_button("登录")

    # ============================
    # ⭐ 导航
    # ============================
    def navigate_to(self, url):
        self.page.goto(url)

    # ============================
    # ⭐ 关闭
    # ============================
    def close(self):
        self.page.context.close()
