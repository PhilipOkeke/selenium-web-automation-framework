# Project Walkthrough

Use this guide to understand the framework and explain your decisions in an interview.

## The problem it solves

An API can work correctly while the user interface is broken. This framework verifies TaskFlow through a real browser: users can create, update, find, filter, and delete tasks through the web application.

## Why Page Object Model?

`TaskFlowPage` owns page locators and user actions. Test files describe expected behavior without repeating Selenium commands. If the interface changes, most locator updates happen in one class rather than every test.

## Why explicit waits?

Modern web interfaces update asynchronously. Fixed sleeps make suites slow and unreliable. `WebDriverWait` waits for specific conditions, such as API connectivity, visible tasks, completed list refreshes, and browser alerts.

## How test data stays controlled

Tests use the API to prepare the exact data each browser scenario needs. An automatic fixture deletes tasks before and after every scenario. This makes tests independent and repeatable.

## How failures are investigated

The PyTest reporting hook detects failed browser tests and captures a PNG screenshot. CI also saves an HTML report, JUnit XML, screenshots, and service logs.

## How the application is connected

The repository includes a responsive JavaScript web client. A small same-origin proxy serves the client and forwards browser API requests to TaskFlow API. GitHub Actions starts both services before launching headless Chrome.

## Interview talking points

- "I used Page Object Model to separate browser mechanics from business scenarios."
- "I replaced fixed sleeps with explicit waits to reduce flaky tests."
- "My fixtures use the API for fast setup and cleanup while Selenium verifies the user experience."
- "Failed tests automatically capture screenshots, reports, and logs for diagnosis."
- "The workflow starts the application stack and runs end-to-end tests in headless Chrome on every change."
- "This repository also includes the HTML, CSS, and JavaScript client, so it shows both automation and development skills."

## A small change you can make yourself

Add a browser test for the `in_progress` filter. Seed one matching and one non-matching task, reload the page, select `in_progress`, and verify only the matching title remains.

Practice explaining that change before an interview.

