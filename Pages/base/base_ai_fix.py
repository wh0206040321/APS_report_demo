import os
import json
import time
from openai import OpenAI

# 构建 DeepSeek 客户端
def _build_openai_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

client = _build_openai_client()


# ============================
# ⭐ 清理 AI 返回的 JSON
# ============================
def clean_json_response(ai_response):
    """移除 ```json ``` 等 markdown 包裹"""
    if not ai_response:
        return ai_response

    cleaned = ai_response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


# ============================
# ⭐ AI 修复定位器（公共函数）
# ============================
def ai_decide(failed_locator, error=None, html=None):
    """
    公共 AI 修复函数
    SeleniumBasePage 和 PlaywrightBasePage 都会调用它
    """

    if client is None:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY，无法使用 AI 修复")

    # Playwright 和 Selenium 都可以传 HTML
    html = html or ""
    short_html = html[:8000]

    prompt = f"""
你是一个自动化测试定位器修复 AI。

任务：根据页面 HTML 片段、失败的定位器，返回一个**新的可用定位器**。

⚠️ 必须满足：
1. 只返回纯 JSON，不要用 ```json 或任何 markdown 格式包裹
2. JSON 中必须包含 "locator"
3. locator 必须是 XPath 或 CSS

HTML（截断）:
{short_html}

失败定位器:
{failed_locator}

错误:
{error}

返回纯 JSON（示例）：
{{"locator": "//div[@class='xxx']"}}
"""

    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content
