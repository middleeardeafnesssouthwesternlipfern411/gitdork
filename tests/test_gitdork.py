"""Comprehensive tests for gitdork."""

from __future__ import annotations

import pytest

from gitdork.dork_engine import generate
from gitdork.extractor import parse_target
from gitdork.models import (
    Dork,
    DorkCategory,
    DorkEngine,
    DorkResult,
    Target,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def has_query_containing(dorks: list[Dork], text: str) -> bool:
    return any(text.lower() in d.query.lower() for d in dorks)


def has_description_containing(dorks: list[Dork], text: str) -> bool:
    return any(text.lower() in d.description.lower() for d in dorks)


# ── Target parser ─────────────────────────────────────────────────────────────

class TestTargetParser:
    def test_github_full_url(self):
        t = parse_target("https://github.com/ExploitCraft/ReconNinja")
        assert t.org == "ExploitCraft"
        assert t.repo == "ReconNinja"
        assert t.is_github is True

    def test_github_shorthand(self):
        t = parse_target("ExploitCraft/ReconNinja")
        assert t.org == "ExploitCraft"
        assert t.repo == "ReconNinja"
        assert t.is_github is True

    def test_github_org_only(self):
        t = parse_target("github.com/ExploitCraft")
        assert t.org == "ExploitCraft"
        assert t.repo is None
        assert t.is_github is True

    def test_plain_domain(self):
        t = parse_target("example.com")
        assert t.domain == "example.com"
        assert t.org is None
        assert t.is_github is False

    def test_domain_with_http(self):
        t = parse_target("https://example.com")
        assert t.domain == "example.com"

    def test_domain_with_subdomain(self):
        t = parse_target("api.example.com")
        assert t.domain == "api.example.com"

    def test_display_github_full(self):
        t = parse_target("ExploitCraft/ReconNinja")
        assert t.display == "ExploitCraft/ReconNinja"

    def test_display_domain(self):
        t = parse_target("example.com")
        assert t.display == "example.com"

    def test_display_org_only(self):
        t = parse_target("github.com/ExploitCraft")
        assert t.display == "ExploitCraft"


# ── Dork model ────────────────────────────────────────────────────────────────

class TestDorkModel:
    def test_with_url_google(self):
        d = Dork(
            engine=DorkEngine.GOOGLE,
            category=DorkCategory.SECRETS,
            query='site:github.com "api_key"',
            description="Test",
        )
        d.with_url()
        assert d.url.startswith("https://www.google.com/search?q=")

    def test_with_url_shodan(self):
        d = Dork(
            engine=DorkEngine.SHODAN,
            category=DorkCategory.MISCONFIGS,
            query='hostname:"example.com" port:22',
            description="Test",
        )
        d.with_url()
        assert d.url.startswith("https://www.shodan.io/search?query=")

    def test_with_url_github(self):
        d = Dork(
            engine=DorkEngine.GITHUB,
            category=DorkCategory.SECRETS,
            query='org:ExploitCraft "api_key"',
            description="Test",
        )
        d.with_url()
        assert d.url.startswith("https://github.com/search?type=code&q=")


# ── DorkResult ────────────────────────────────────────────────────────────────

class TestDorkResult:
    def setup_method(self):
        target = Target(raw="example.com", domain="example.com")
        self.result = DorkResult(target=target, dorks=[
            Dork(DorkEngine.GOOGLE, DorkCategory.SECRETS,
                 'site:example.com secret', "Google secret"),
            Dork(DorkEngine.GOOGLE, DorkCategory.MISCONFIGS,
                 'site:example.com admin', "Google admin"),
            Dork(DorkEngine.SHODAN, DorkCategory.MISCONFIGS,
                 'hostname:"example.com" port:22', "Shodan SSH"),
            Dork(DorkEngine.GITHUB, DorkCategory.SECRETS,
                 'org:example "api_key"', "GitHub key"),
        ])

    def test_total(self):
        assert self.result.total == 4

    def test_google_count(self):
        assert self.result.google_count == 2

    def test_shodan_count(self):
        assert self.result.shodan_count == 1

    def test_github_count(self):
        assert self.result.github_count == 1

    def test_by_engine(self):
        google = self.result.by_engine(DorkEngine.GOOGLE)
        assert len(google) == 2

    def test_by_category(self):
        secrets = self.result.by_category(DorkCategory.SECRETS)
        assert len(secrets) == 2


# ── Google dork generation ────────────────────────────────────────────────────

class TestGoogleDorks:
    def setup_method(self):
        self.target = parse_target("example.com")
        self.result = generate(
            self.target, engines=[DorkEngine.GOOGLE]
        )
        self.dorks = self.result.dorks

    def test_generates_dorks(self):
        assert len(self.dorks) > 0

    def test_all_google_engine(self):
        assert all(d.engine == DorkEngine.GOOGLE for d in self.dorks)

    def test_has_secrets_category(self):
        secrets = self.result.by_category(DorkCategory.SECRETS)
        assert len(secrets) > 0

    def test_has_sensitive_files_category(self):
        files = self.result.by_category(DorkCategory.SENSITIVE_FILES)
        assert len(files) > 0

    def test_has_misconfigs_category(self):
        misconfigs = self.result.by_category(DorkCategory.MISCONFIGS)
        assert len(misconfigs) > 0

    def test_has_login_panels_category(self):
        logins = self.result.by_category(DorkCategory.LOGIN_PANELS)
        assert len(logins) > 0

    def test_has_exposed_dirs_category(self):
        dirs = self.result.by_category(DorkCategory.EXPOSED_DIRS)
        assert len(dirs) > 0

    def test_has_error_pages_category(self):
        errors = self.result.by_category(DorkCategory.ERROR_PAGES)
        assert len(errors) > 0

    def test_domain_in_queries(self):
        assert has_query_containing(self.dorks, "example.com")

    def test_site_operator_present(self):
        assert any("site:" in d.query for d in self.dorks)

    def test_filetype_operator_present(self):
        assert any("filetype:" in d.query for d in self.dorks)

    def test_intitle_operator_present(self):
        assert any("intitle:" in d.query for d in self.dorks)

    def test_all_dorks_have_description(self):
        assert all(d.description for d in self.dorks)

    def test_all_dorks_have_url(self):
        assert all(d.url.startswith("https://www.google.com") for d in self.dorks)

    def test_github_org_target(self):
        target = parse_target("ExploitCraft/ReconNinja")
        result = generate(target, engines=[DorkEngine.GOOGLE])
        assert has_query_containing(result.dorks, "ExploitCraft")

    def test_env_file_dork(self):
        assert has_description_containing(self.dorks, ".env")

    def test_private_key_dork(self):
        assert has_query_containing(self.dorks, "RSA PRIVATE KEY")


# ── Shodan dork generation ────────────────────────────────────────────────────

class TestShodanDorks:
    def setup_method(self):
        self.target = parse_target("example.com")
        self.result = generate(
            self.target, engines=[DorkEngine.SHODAN]
        )
        self.dorks = self.result.dorks

    def test_generates_dorks(self):
        assert len(self.dorks) > 0

    def test_all_shodan_engine(self):
        assert all(d.engine == DorkEngine.SHODAN for d in self.dorks)

    def test_hostname_operator_present(self):
        assert any("hostname:" in d.query for d in self.dorks)

    def test_port_operator_present(self):
        assert any("port:" in d.query for d in self.dorks)

    def test_ssl_operator_present(self):
        assert any("ssl." in d.query for d in self.dorks)

    def test_has_common_ports(self):
        queries = " ".join(d.query for d in self.dorks)
        assert "22" in queries    # SSH
        assert "6379" in queries  # Redis
        assert "9200" in queries  # Elasticsearch
        assert "27017" in queries # MongoDB

    def test_all_dorks_have_url(self):
        assert all(d.url.startswith("https://www.shodan.io") for d in self.dorks)

    def test_root_domain_used(self):
        # Should use example.com not the full subdomain
        assert has_query_containing(self.dorks, "example.com")


# ── GitHub dork generation ────────────────────────────────────────────────────

class TestGitHubDorks:
    def setup_method(self):
        self.target = parse_target("ExploitCraft/ReconNinja")
        self.result = generate(
            self.target, engines=[DorkEngine.GITHUB]
        )
        self.dorks = self.result.dorks

    def test_generates_dorks(self):
        assert len(self.dorks) > 0

    def test_all_github_engine(self):
        assert all(d.engine == DorkEngine.GITHUB for d in self.dorks)

    def test_org_operator_present(self):
        assert any("org:" in d.query for d in self.dorks)

    def test_filename_operator_present(self):
        assert any("filename:" in d.query for d in self.dorks)

    def test_extension_operator_present(self):
        assert any("extension:" in d.query for d in self.dorks)

    def test_has_secrets_category(self):
        assert len(self.result.by_category(DorkCategory.SECRETS)) > 0

    def test_has_sensitive_files_category(self):
        assert len(
            self.result.by_category(DorkCategory.SENSITIVE_FILES)
        ) > 0

    def test_env_file_dork(self):
        assert has_query_containing(self.dorks, "filename:.env")

    def test_private_key_dork(self):
        assert has_query_containing(self.dorks, "RSA PRIVATE KEY")

    def test_all_dorks_have_url(self):
        assert all(
            d.url.startswith("https://github.com/search") for d in self.dorks
        )


# ── Engine filter ─────────────────────────────────────────────────────────────

class TestEngineFilter:
    def test_google_only(self):
        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        assert result.shodan_count == 0
        assert result.github_count == 0
        assert result.google_count > 0

    def test_shodan_only(self):
        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.SHODAN])
        assert result.google_count == 0
        assert result.github_count == 0
        assert result.shodan_count > 0

    def test_github_only(self):
        t = parse_target("ExploitCraft")
        result = generate(t, engines=[DorkEngine.GITHUB])
        assert result.google_count == 0
        assert result.shodan_count == 0
        assert result.github_count > 0

    def test_two_engines(self):
        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE, DorkEngine.SHODAN])
        assert result.github_count == 0
        assert result.google_count > 0
        assert result.shodan_count > 0


# ── Category filter ───────────────────────────────────────────────────────────

class TestCategoryFilter:
    def test_secrets_only(self):
        t = parse_target("example.com")
        result = generate(t, categories=[DorkCategory.SECRETS])
        non_secrets = [
            d for d in result.dorks
            if d.category != DorkCategory.SECRETS
        ]
        assert len(non_secrets) == 0

    def test_misconfigs_only(self):
        t = parse_target("example.com")
        result = generate(t, categories=[DorkCategory.MISCONFIGS])
        assert all(
            d.category == DorkCategory.MISCONFIGS for d in result.dorks
        )

    def test_two_categories(self):
        t = parse_target("example.com")
        result = generate(t, categories=[
            DorkCategory.SECRETS, DorkCategory.MISCONFIGS
        ])
        allowed = {DorkCategory.SECRETS, DorkCategory.MISCONFIGS}
        assert all(d.category in allowed for d in result.dorks)


# ── Tech stack ────────────────────────────────────────────────────────────────

class TestTechStack:
    def test_django_dorks_added(self):
        t = Target(
            raw="example.com", domain="example.com", tech_stack=["django"]
        )
        result = generate(t, engines=[DorkEngine.GOOGLE])
        assert has_query_containing(result.dorks, "DEBUG")

    def test_wordpress_dorks_added(self):
        t = Target(
            raw="example.com", domain="example.com",
            tech_stack=["wordpress"]
        )
        result = generate(t, engines=[DorkEngine.GOOGLE])
        assert has_query_containing(result.dorks, "wp-content")

    def test_aws_github_dorks_added(self):
        t = Target(
            raw="ExploitCraft", org="ExploitCraft", tech_stack=["aws"]
        )
        result = generate(t, engines=[DorkEngine.GITHUB])
        assert has_query_containing(result.dorks, "aws_access_key_id")

    def test_no_stack_no_tech_dorks(self):
        t = Target(raw="example.com", domain="example.com", tech_stack=[])
        result = generate(t)
        # Should still generate base dorks
        assert result.total > 0


# ── JSON reporter ─────────────────────────────────────────────────────────────

class TestJSONReporter:
    def test_json_structure(self):
        from gitdork.reporters.json_report import to_dict

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        data = to_dict(result)

        assert "target" in data
        assert "summary" in data
        assert "dorks" in data
        assert data["summary"]["total"] == len(data["dorks"])

    def test_json_dork_fields(self):
        from gitdork.reporters.json_report import to_dict

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        data = to_dict(result)

        d = data["dorks"][0]
        for field in ("engine", "category", "description", "query", "url"):
            assert field in d

    def test_json_write_to_file(self, tmp_path):
        import json
        from gitdork.reporters.json_report import write

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        out = tmp_path / "dorks.json"
        write(result, out)

        assert out.exists()
        data = json.loads(out.read_text())
        assert data["summary"]["total"] > 0


# ── Markdown reporter ─────────────────────────────────────────────────────────

class TestMarkdownReporter:
    def test_markdown_contains_target(self):
        from gitdork.reporters.markdown import to_markdown

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        md = to_markdown(result)

        assert "example.com" in md

    def test_markdown_contains_engine_headers(self):
        from gitdork.reporters.markdown import to_markdown

        t = parse_target("example.com")
        result = generate(t)
        md = to_markdown(result)

        assert "Google" in md
        assert "Shodan" in md

    def test_markdown_contains_queries(self):
        from gitdork.reporters.markdown import to_markdown

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        md = to_markdown(result)

        assert "site:" in md

    def test_markdown_write_to_file(self, tmp_path):
        from gitdork.reporters.markdown import write

        t = parse_target("example.com")
        result = generate(t, engines=[DorkEngine.GOOGLE])
        out = tmp_path / "dorks.md"
        write(result, out)

        assert out.exists()
        assert len(out.read_text()) > 100
