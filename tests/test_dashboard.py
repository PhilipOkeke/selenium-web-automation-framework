"""Smoke checks for the dashboard and API connection."""

import pytest

from taskflow_web_automation.pages.taskflow_page import TaskFlowPage


@pytest.mark.smoke
def test_dashboard_loads_with_connected_api(page: TaskFlowPage) -> None:
    assert page.heading() == "Plan work. Track progress."
    assert page.api_status() == "API connected"
    assert page.task_count() == 0
    assert page.empty_state_is_visible()


@pytest.mark.smoke
def test_required_title_validation_prevents_empty_task(page: TaskFlowPage) -> None:
    page.submit_empty_form()

    assert page.title_validation_message()
    assert page.task_count() == 0
