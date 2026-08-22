"""Page Object representing the TaskFlow dashboard."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import Select

from taskflow_web_automation.pages.base_page import BasePage, Locator


def xpath_literal(value: str) -> str:
    """Safely quote arbitrary text for an XPath expression."""

    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"


class TaskFlowPage(BasePage):
    """User-focused operations available on the TaskFlow dashboard."""

    PAGE_HEADING = (By.CSS_SELECTOR, "h1")
    API_STATUS = (By.ID, "api-status")
    TASK_FORM = (By.ID, "task-form")
    TITLE_INPUT = (By.ID, "task-title")
    DESCRIPTION_INPUT = (By.ID, "task-description")
    PRIORITY_INPUT = (By.ID, "task-priority")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#task-form button[type='submit']")
    SEARCH_INPUT = (By.ID, "search-input")
    STATUS_FILTER = (By.ID, "status-filter")
    PRIORITY_FILTER = (By.ID, "priority-filter")
    TASK_LIST = (By.ID, "task-list")
    TASK_CARDS = (By.CSS_SELECTOR, ".task-card")
    TASK_TITLES = (By.CSS_SELECTOR, ".task-card .task-title")
    EMPTY_STATE = (By.ID, "empty-state")
    TASK_COUNT = (By.ID, "task-count")
    TOAST = (By.ID, "toast")

    def load(self) -> "TaskFlowPage":
        self.open()
        self.visible(self.PAGE_HEADING)
        self.wait_until(conditions.text_to_be_present_in_element(self.API_STATUS, "API connected"))
        self.wait_for_list()
        return self

    def wait_for_list(self) -> None:
        self.wait_until(
            lambda driver: (
                driver.find_element(*self.TASK_LIST).get_attribute("aria-busy") == "false"
            )
        )

    def heading(self) -> str:
        return self.text(self.PAGE_HEADING)

    def api_status(self) -> str:
        return self.text(self.API_STATUS)

    def add_task(
        self,
        title: str,
        *,
        description: str = "Created by Selenium automation",
        priority: str = "medium",
    ) -> None:
        self.type_text(self.TITLE_INPUT, title)
        self.type_text(self.DESCRIPTION_INPUT, description)
        Select(self.visible(self.PRIORITY_INPUT)).select_by_value(priority)
        self.clickable(self.SUBMIT_BUTTON).click()

    def submit_empty_form(self) -> None:
        self.type_text(self.TITLE_INPUT, "")
        self.clickable(self.SUBMIT_BUTTON).click()

    def title_validation_message(self) -> str:
        title_input = self.visible(self.TITLE_INPUT)
        return str(
            self.driver.execute_script("return arguments[0].validationMessage;", title_input)
        )

    def wait_for_task(self, title: str) -> None:
        self.visible(self._task_card_locator(title))

    def task_titles(self) -> list[str]:
        self.wait_for_list()
        return [element.text for element in self.driver.find_elements(*self.TASK_TITLES)]

    def task_count(self) -> int:
        return int(self.text(self.TASK_COUNT))

    def set_task_status(self, title: str, status: str) -> None:
        status_locator = self._within_task(title, ".task-status-select")
        Select(self.visible(status_locator)).select_by_value(status)
        self.wait_for_toast("Task updated")
        self.wait_until(
            lambda driver: (
                Select(driver.find_element(*status_locator)).first_selected_option.get_attribute(
                    "value"
                )
                == status
            )
        )

    def task_status(self, title: str) -> str:
        select = Select(self.visible(self._within_task(title, ".task-status-select")))
        return str(select.first_selected_option.get_attribute("value"))

    def delete_task(self, title: str) -> None:
        card_locator = self._task_card_locator(title)
        self.clickable(self._within_task(title, ".delete-task")).click()
        alert = self.wait_until(conditions.alert_is_present())
        alert.accept()
        self.wait_until(conditions.invisibility_of_element_located(card_locator))
        self.wait_for_toast("Task deleted")

    def filter_by_status(self, status: str) -> None:
        Select(self.visible(self.STATUS_FILTER)).select_by_value(status)
        self.wait_for_list()

    def filter_by_priority(self, priority: str) -> None:
        Select(self.visible(self.PRIORITY_FILTER)).select_by_value(priority)
        self.wait_for_list()

    def search(self, phrase: str) -> None:
        self.type_text(self.SEARCH_INPUT, phrase)
        self.wait_for_list()

    def empty_state_is_visible(self) -> bool:
        return self.visible(self.EMPTY_STATE).is_displayed()

    def wait_for_toast(self, message: str) -> None:
        self.wait_until(conditions.text_to_be_present_in_element(self.TOAST, message))
        self.visible(self.TOAST)

    @staticmethod
    def _task_card_locator(title: str) -> Locator:
        title_value = xpath_literal(title)
        return (
            By.XPATH,
            "//article[contains(@class, 'task-card')]"
            f"[.//*[contains(@class, 'task-title') and normalize-space()={title_value}]]",
        )

    @classmethod
    def _within_task(cls, title: str, child_css: str) -> Locator:
        card_xpath = cls._task_card_locator(title)[1]
        return By.XPATH, f"{card_xpath}//*[contains(@class, '{child_css.removeprefix('.')}')]"
