# self_healing_driver.py
import time
import json
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from difflib import SequenceMatcher
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


client = _build_openai_client()

LOCATOR_MEMORY = "locator_memory.json"


class SelfHealingDriver:
    def __init__(self, driver):
        self.driver = driver
        self.memory = self._load_memory()

    # ---------------------------
    # 内部：加载定位器记忆库
    # ---------------------------
    def _load_memory(self):
        if not os.path.exists(LOCATOR_MEMORY):
            return {}
        with open(LOCATOR_MEMORY, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------------------
    # 内部：保存定位器记忆库
    # ---------------------------
    def _save_memory(self):
        with open(LOCATOR_MEMORY, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    # ---------------------------
    # 核心：自愈 find_element
    # ---------------------------
    def find_element(self, by, value):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            print(f"[自愈] 定位器失效: {by}={value}")

            # 1. 尝试从记忆库修复
            healed = self._try_memory(by, value)
            if healed:
                return healed

            # 2. 尝试模糊匹配
            healed = self._try_fuzzy_match(value)
            if healed:
                return healed

            # 3. AI 修复
            healed = self._try_ai_fix(by, value)
            if healed:
                return healed

            # 4. 全部失败 → 抛出异常
            raise

    # ---------------------------
    # 方案 1：从记忆库修复
    # ---------------------------
    def _try_memory(self, by, value):
        key = f"{by}:{value}"
        if key in self.memory:
            new_by, new_value = self.memory[key]["new"]
            print(f"[自愈] 使用记忆库修复 → {new_by}={new_value}")
            try:
                return self.driver.find_element(new_by, new_value)
            except:
                return None
        return None

    # ---------------------------
    # 方案 2：模糊匹配 DOM
    # ---------------------------
    def _try_fuzzy_match(self, old_value):
        print("[自愈] 尝试模糊匹配 DOM…")
        elements = self.driver.find_elements(By.XPATH, "//*")

        best_score = 0
        best_element = None

        for el in elements:
            try:
                text = el.text or ""
                score = SequenceMatcher(None, old_value, text).ratio()
                if score > best_score:
                    best_score = score
                    best_element = el
            except:
                continue

        if best_score > 0.6:
            print(f"[自愈] 模糊匹配成功（相似度 {best_score:.2f}）")
            return best_element

        return None

    # ---------------------------
    # 方案 3：AI 修复定位器（DeepSeek）
    # ---------------------------
    def _try_ai_fix(self, by, value):
        print("[自愈] 尝试 AI 修复定位器…")
        if client is None:
            print("[自愈] 未配置 DEEPSEEK_API_KEY，跳过 AI 修复。")
            return None

        html = self.driver.page_source

        prompt = f"""
页面 HTML:
{html}

定位器失效: {by}={value}

请给出新的定位器（CSS 或 XPath），只返回定位器字符串，不要解释。
"""

        try:
            res = client.chat.completions.create(
                model="deepseek-chat",   # DeepSeek 的模型名
                messages=[{"role": "user", "content": prompt}]
            )
            new_locator = res.choices[0].message.content.strip()

            print(f"[自愈] AI 修复定位器 → {new_locator}")

            # 尝试使用 AI 新定位器
            if new_locator.startswith("//"):
                new_by = By.XPATH
                new_value = new_locator
            else:
                new_by = By.CSS_SELECTOR
                new_value = new_locator

            el = self.driver.find_element(new_by, new_value)

            # 写入记忆库
            key = f"{by}:{value}"
            self.memory[key] = {"new": [new_by, new_value]}
            self._save_memory()

            return el

        except Exception as e:
            print("[自愈] AI 修复失败:", e)
            return None

    # ---------------------------
    # 代理其他属性
    # ---------------------------
    def __getattr__(self, item):
        return getattr(self.driver, item)
