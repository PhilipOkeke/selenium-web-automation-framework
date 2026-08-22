"""Environment-driven configuration for local and CI browser runs."""

from dataclasses import dataclass
from os import getenv


def env_flag(name: str, default: bool) -> bool:
    value = getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    """URLs, browser choice, and wait settings used by the framework."""

    web_base_url: str = "http://127.0.0.1:3000"
    api_base_url: str = "http://127.0.0.1:8000"
    browser: str = "chrome"
    headless: bool = True
    explicit_wait: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            web_base_url=getenv("WEB_BASE_URL", defaults.web_base_url).rstrip("/"),
            api_base_url=getenv("API_BASE_URL", defaults.api_base_url).rstrip("/"),
            browser=getenv("BROWSER", defaults.browser).strip().lower(),
            headless=env_flag("HEADLESS", defaults.headless),
            explicit_wait=float(getenv("EXPLICIT_WAIT", str(defaults.explicit_wait))),
        )
