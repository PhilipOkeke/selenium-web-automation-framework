"""Shared explicit-wait and browser interaction helpers."""

from collections.abc import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    """Base class used by Page Objects, with no test assertions."""

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10.0) -> None:
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = "") -> None:
        self.driver.get(f"{self.base_url}{path}")

    def visible(self, locator: Locator) -> WebElement:
        return self.wait.until(conditions.visibility_of_element_located(locator))

    def clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(conditions.element_to_be_clickable(locator))

    def all_present(self, locator: Locator) -> list[WebElement]:
        return self.wait.until(conditions.presence_of_all_elements_located(locator))

    def type_text(self, locator: Locator, value: str) -> None:
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)

    def wait_until(self, condition: Callable[[WebDriver], object]) -> object:
        return self.wait.until(condition)

    def text(self, locator: Locator) -> str:
        return self.visible(locator).text
