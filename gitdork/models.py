"""Core data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DorkEngine(str, Enum):
    GOOGLE = "google"
    SHODAN = "shodan"
    GITHUB = "github"


class DorkCategory(str, Enum):
    SECRETS         = "secrets"
    SENSITIVE_FILES = "sensitive_files"
    EXPOSED_DIRS    = "exposed_dirs"
    MISCONFIGS      = "misconfigs"
    SUBDOMAINS      = "subdomains"
    LOGIN_PANELS    = "login_panels"
    ERROR_PAGES     = "error_pages"
    CODE_LEAKS      = "code_leaks"


CATEGORY_LABELS = {
    DorkCategory.SECRETS:         "Secrets & Credentials",
    DorkCategory.SENSITIVE_FILES: "Sensitive Files",
    DorkCategory.EXPOSED_DIRS:    "Exposed Directories",
    DorkCategory.MISCONFIGS:      "Misconfigurations",
    DorkCategory.SUBDOMAINS:      "Subdomains & Infra",
    DorkCategory.LOGIN_PANELS:    "Login Panels",
    DorkCategory.ERROR_PAGES:     "Error Pages",
    DorkCategory.CODE_LEAKS:      "Code Leaks",
}


@dataclass
class Target:
    raw: str
    domain: str | None = None
    org: str | None = None
    repo: str | None = None
    tech_stack: list[str] = field(default_factory=list)

    @property
    def is_github(self) -> bool:
        return self.org is not None

    @property
    def display(self) -> str:
        if self.org and self.repo:
            return f"{self.org}/{self.repo}"
        if self.org:
            return self.org
        return self.domain or self.raw


@dataclass
class Dork:
    engine: DorkEngine
    category: DorkCategory
    query: str
    description: str
    url: str = ""

    def with_url(self) -> "Dork":
        """Return copy with search URL populated."""
        if self.engine == DorkEngine.GOOGLE:
            import urllib.parse
            self.url = (
                "https://www.google.com/search?q="
                + urllib.parse.quote(self.query)
            )
        elif self.engine == DorkEngine.SHODAN:
            import urllib.parse
            self.url = (
                "https://www.shodan.io/search?query="
                + urllib.parse.quote(self.query)
            )
        elif self.engine == DorkEngine.GITHUB:
            import urllib.parse
            self.url = (
                "https://github.com/search?type=code&q="
                + urllib.parse.quote(self.query)
            )
        return self


@dataclass
class DorkResult:
    target: Target
    dorks: list[Dork] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.dorks)

    def by_engine(self, engine: DorkEngine) -> list[Dork]:
        return [d for d in self.dorks if d.engine == engine]

    def by_category(self, category: DorkCategory) -> list[Dork]:
        return [d for d in self.dorks if d.category == category]

    @property
    def google_count(self) -> int:
        return len(self.by_engine(DorkEngine.GOOGLE))

    @property
    def shodan_count(self) -> int:
        return len(self.by_engine(DorkEngine.SHODAN))

    @property
    def github_count(self) -> int:
        return len(self.by_engine(DorkEngine.GITHUB))
