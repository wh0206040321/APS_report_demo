# import re
# from playwright.sync_api import expect, sync_playwright
#
#
# def test_create_item_flow() -> None:
#     with sync_playwright() as playwright:
#         browser = playwright.chromium.launch(headless=False)
#         context = browser.new_context()
#         page = context.new_page()
#         page.goto("http://wkawka.vicp.net:27890/#/auth/login")
#
#         username_input = page.get_by_role("textbox", name="请输入账户")
#         password_input = page.get_by_role("textbox", name="请输入密码")
#         login_button = page.get_by_role("button", name="登录")
#         expect(username_input).to_be_visible()
#         expect(password_input).to_be_visible()
#         expect(login_button).to_be_visible()
#
#         username_input.click()
#         username_input.fill("hongaoqing")
#         password_input.click()
#         password_input.fill("1234qweR")
#         page.locator(".ivu-icon.ivu-icon-ios-arrow-down").click()
#         page.get_by_text("金属（演示）").click()
#         login_button.click()
#
#         page.wait_for_load_state("networkidle")
#         expect(page).not_to_have_url(re.compile(r".*/auth/login.*"), timeout=15000)
#         plan_menu = page.get_by_text("计划管理")
#         expect(plan_menu).to_be_visible(timeout=15000)
#         plan_menu.click()
#         page.locator("div").filter(has_text="计划基础数据 计划基础数据").nth(4).click()
#         item_menu = page.get_by_role("menuitem").filter(has_text=re.compile(r"物品\s*$"))
#         expect(item_menu).to_be_visible(timeout=15000)
#         item_menu.click()
#
#         page.wait_for_load_state("networkidle")
#         add_button = page.locator("div.tool-item:has(p:has-text('新增'))").first
#         expect(add_button).to_be_visible(timeout=15000)
#         add_button.click()
#         page.locator(".ivu-input.ivu-input-default").first.click()
#         page.locator(".ivu-input.ivu-input-default").first.fill("123")
#         page.locator("div:nth-child(2) > .ivu-form-item > .ivu-form-item-content > .ivu-input-wrapper > .ivu-input").click()
#         page.locator("div:nth-child(2) > .ivu-form-item > .ivu-form-item-content > .ivu-input-wrapper > .ivu-input").fill("123")
#         page.get_by_role("button", name="确定").click()
#
#         alert_message = page.get_by_role("alert")
#         expect(alert_message).to_be_visible(timeout=15000)
#         expect(alert_message).to_contain_text("成功")
#         alert_message.click()
#
#         created_item = page.get_by_text("123").first
#         expect(created_item).to_be_visible(timeout=15000)
#         created_item.click()
#
#         context.close()
#         browser.close()
