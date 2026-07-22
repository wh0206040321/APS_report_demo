from playwright.sync_api import Page


class ChangeRPlaywright:
    """Playwright 版本的资源切换页面"""

    def __init__(self, page: Page):
        self.page = page

    def click_add_button(self):
        self.page.click('button:has-text("添加")')

    def click_button(self, xpath: str):
        self.page.click(xpath)

    def enter_texts(self, xpath: str, text: str):
        self.page.fill(xpath, text)

    def get_border_color(self, xpath: str) -> str:
        return self.page.locator(xpath).evaluate('el => getComputedStyle(el).borderColor')

    def has_fail_message(self) -> bool:
        return self.page.locator('.error-message').is_visible()

    def right_refresh(self, tab_name: str):
        self.page.click(f'//span[text()="{tab_name}"]', button='right')
        self.page.click('//div[text()="刷新"]')