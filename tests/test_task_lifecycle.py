"""Browser tests for creating, updating, and deleting tasks."""

import pytest

from taskflow_web_automation.pages.taskflow_page import TaskFlowPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_user_creates_a_high_priority_task(page: TaskFlowPage) -> None:
    title = "Philip's release checklist"

    page.add_task(title, description="Verify the release workflow", priority="high")
    page.wait_for_task(title)

    assert title in page.task_titles()
    assert page.task_status(title) == "todo"
    assert page.task_count() == 1


def test_user_moves_task_to_done(page: TaskFlowPage) -> None:
    title = "Complete browser regression"
    page.add_task(title)
    page.wait_for_task(title)

    page.set_task_status(title, "done")

    assert page.task_status(title) == "done"


def test_user_deletes_task_after_confirmation(page: TaskFlowPage) -> None:
    title = "Remove obsolete test task"
    page.add_task(title)
    page.wait_for_task(title)

    page.delete_task(title)

    assert title not in page.task_titles()
    assert page.task_count() == 0
    assert page.empty_state_is_visible()
