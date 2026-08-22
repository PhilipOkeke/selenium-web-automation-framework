# Contributing to the Selenium Web Automation Framework

This project welcomes focused changes that improve browser coverage, framework design, reliability, or documentation.

## Local setup

1. Start the TaskFlow API.
2. Create and activate a virtual environment in this repository.
3. Install development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

4. Start the web client:

```bash
python scripts/serve_web_app.py
```

5. Run the browser tests:

```bash
pytest
```

Selenium Manager resolves the matching browser driver automatically.

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
```

Use `pytest -m smoke` for critical journeys and `pytest -m regression` for the wider suite.

## Automation conventions

- Keep test scenarios readable and focused on user behaviour.
- Store locators and UI actions in Page Objects.
- Keep browser creation, API setup, cleanup, and evidence capture in fixtures.
- Prefer explicit waits over fixed sleeps.
- Add assertions that explain the expected user-visible outcome.
- Save screenshots and service logs when failures need diagnostic evidence.
- Test selectors should be stable and should not depend on styling or element order.
- Validate changes in headless Chrome before opening a pull request.

## Commit messages

Use concise messages that describe the outcome:

- `Add browser coverage for task priority changes`
- `Replace fixed delay with explicit wait`
- `Improve failure screenshot naming`

## Pull-request checklist

- New flows follow the Page Object Model
- Tests are independent and repeatable
- Failure evidence is useful
- Smoke and regression markers are appropriate
- Linting, formatting, and browser tests pass
- Documentation reflects any setup or behaviour change
