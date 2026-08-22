"""Cross-browser WebDriver creation with CI-friendly defaults."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from taskflow_web_automation.config import Settings


def create_driver(settings: Settings) -> WebDriver:
    """Create the selected local browser through Selenium Manager."""

    if settings.browser == "chrome":
        options = ChromeOptions()
        if settings.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    if settings.browser == "firefox":
        options = FirefoxOptions()
        if settings.headless:
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    raise ValueError(f"Unsupported browser: {settings.browser}. Use 'chrome' or 'firefox'.")
