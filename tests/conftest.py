"""Shared browser, page, API data, and failure-artifact fixtures."""

import re
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
import requests
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from taskflow_web_automation.config import Settings
from taskflow_web_automation.driver_factory import create_driver
from taskflow_web_automation.pages.taskflow_page import TaskFlowPage

SCREENSHOT_DIRECTORY = Path("screenshots")
SELENIUM_EMAIL = "selenium@example.com"
SELENIUM_PASSWORD = "AutomationTest123!"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def api_session(settings: Settings) -> Generator[requests.Session, None, None]:
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        registration = session.post(
            f"{settings.api_base_url}/api/v1/auth/register",
            json={
                "email": SELENIUM_EMAIL,
                "password": SELENIUM_PASSWORD,
                "full_name": "Selenium Browser User",
            },
            timeout=10,
        )
        assert registration.status_code in {201, 400, 409}

        token_response = session.post(
            f"{settings.api_base_url}/api/v1/auth/token",
            data={"username": SELENIUM_EMAIL, "password": SELENIUM_PASSWORD},
            timeout=10,
        )
        token_response.raise_for_status()
        session.headers.update(
            {"Authorization": f"Bearer {token_response.json()['access_token']}"}
        )
        yield session


def delete_all_tasks(session: requests.Session, api_base_url: str) -> None:
    response = session.get(
        f"{api_base_url}/api/v1/tasks", params={"limit": 100}, timeout=10
    )
    response.raise_for_status()
    for task in response.json()["items"]:
        delete_response = session.delete(
            f"{api_base_url}/api/v1/tasks/{task['id']}",
            timeout=10,
        )
        assert delete_response.status_code in {204, 404}


@pytest.fixture(autouse=True)
def clean_taskflow_data(
    api_session: requests.Session,
    settings: Settings,
) -> Generator[None, None, None]:
    delete_all_tasks(api_session, settings.api_base_url)
    yield
    delete_all_tasks(api_session, settings.api_base_url)


@pytest.fixture
def seed_task(
    api_session: requests.Session,
    settings: Settings,
) -> Callable[..., dict[str, Any]]:
    def _seed(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": f"Browser task {uuid4().hex[:8]}",
            "description": "Seeded for a Selenium browser test",
            "status": "todo",
            "priority": "medium",
        }
        payload.update(overrides)
        response = api_session.post(
            f"{settings.api_base_url}/api/v1/tasks",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    return _seed


@pytest.fixture
def browser(settings: Settings) -> Generator[WebDriver, None, None]:
    driver = create_driver(settings)
    yield driver
    driver.quit()


@pytest.fixture
def page(browser: WebDriver, settings: Settings) -> TaskFlowPage:
    return TaskFlowPage(
        browser, settings.web_base_url, settings.explicit_wait
    ).load()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("browser")
    if driver is None:
        return

    SCREENSHOT_DIRECTORY.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
    try:
        driver.save_screenshot(str(SCREENSHOT_DIRECTORY / f"{safe_name}.png"))
    except WebDriverException:
        pass
