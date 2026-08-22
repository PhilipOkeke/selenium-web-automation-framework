"""Wait for both TaskFlow API and browser client during CI startup."""

import time

import requests

from taskflow_web_automation.config import Settings


def wait_for_url(url: str, attempts: int = 30, delay_seconds: float = 1.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"Ready: {url} after {attempt} attempt(s)")
                return
        except requests.RequestException:
            pass
        time.sleep(delay_seconds)
    raise RuntimeError(f"Service did not become ready: {url}")


def main() -> None:
    settings = Settings.from_env()
    wait_for_url(f"{settings.api_base_url}/health")
    wait_for_url(settings.web_base_url)


if __name__ == "__main__":
    main()
