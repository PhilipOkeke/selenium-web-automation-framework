"""Browser tests for filters and search behavior."""

from collections.abc import Callable
from typing import Any

import pytest

from taskflow_web_automation.pages.taskflow_page import TaskFlowPage

pytestmark = pytest.mark.regression


def test_user_combines_status_and_priority_filters(
    page: TaskFlowPage,
    seed_task: Callable[..., dict[str, Any]],
) -> None:
    expected = seed_task(title="Critical completed release", status="done", priority="high")
    seed_task(title="Routine completed cleanup", status="done", priority="low")
    seed_task(title="Critical upcoming review", status="todo", priority="high")
    page.load()

    page.filter_by_status("done")
    page.filter_by_priority("high")

    assert page.task_titles() == [expected["title"]]
    assert page.task_count() == 1


def test_user_searches_for_matching_task(
    page: TaskFlowPage,
    seed_task: Callable[..., dict[str, Any]],
) -> None:
    expected = seed_task(title="Investigate billing regression")
    seed_task(title="Document login workflow")
    page.load()

    page.search("billing")

    assert page.task_titles() == [expected["title"]]
    assert page.task_count() == 1
