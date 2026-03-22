"""GitHub code search dork templates."""

from __future__ import annotations

from ..models import Dork, DorkCategory, DorkEngine, Target


def generate(target: Target) -> list[Dork]:
    dorks: list[Dork] = []
    org = target.org or target.domain or target.raw
    d = target.domain or target.raw

    def add(category: DorkCategory, query: str, description: str):
        dorks.append(Dork(
            engine=DorkEngine.GITHUB,
            category=category,
            query=query,
            description=description,
        ))

    # ── Secrets in Code ────────────────────────────────────────────────────
    add(DorkCategory.SECRETS,
        f'org:{org} "api_key"',
        "API key assignments in org repos")
    add(DorkCategory.SECRETS,
        f'org:{org} "secret_key"',
        "Secret key assignments")
    add(DorkCategory.SECRETS,
        f'org:{org} "access_token"',
        "Access token assignments")
    add(DorkCategory.SECRETS,
        f'org:{org} "private_key"',
        "Private key references")
    add(DorkCategory.SECRETS,
        f'org:{org} "password" extension:env',
        "Passwords in .env files")
    add(DorkCategory.SECRETS,
        f'org:{org} "DB_PASSWORD" extension:env',
        "Database passwords in .env files")
    add(DorkCategory.SECRETS,
        f'org:{org} "AKIA" extension:py OR extension:js OR extension:go',
        "AWS access keys in source code")
    add(DorkCategory.SECRETS,
        f'org:{org} "sk_live_" OR "sk_test_"',
        "Stripe API keys in code")
    add(DorkCategory.SECRETS,
        f'org:{org} "ghp_" OR "github_pat_"',
        "GitHub PATs hardcoded in repos")
    add(DorkCategory.SECRETS,
        f'org:{org} "xoxb-" OR "xoxp-"',
        "Slack bot/user tokens")
    add(DorkCategory.SECRETS,
        f'org:{org} "BEGIN RSA PRIVATE KEY"',
        "RSA private keys in repos")
    add(DorkCategory.SECRETS,
        f'org:{org} "BEGIN OPENSSH PRIVATE KEY"',
        "OpenSSH private keys in repos")
    add(DorkCategory.SECRETS,
        f'org:{org} "SG." extension:env OR extension:py',
        "SendGrid API keys")
    add(DorkCategory.SECRETS,
        f'org:{org} "AIza" extension:js OR extension:py',
        "Google API keys")

    # ── Sensitive Files ────────────────────────────────────────────────────
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:.env',
        ".env files committed to repos")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:.env.production OR filename:.env.local',
        "Production/local .env files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:id_rsa OR filename:id_ed25519',
        "SSH private key files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:credentials extension:json',
        "JSON credential files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:secrets.yml OR filename:secrets.yaml',
        "YAML secrets files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:docker-compose extension:yml "password"',
        "Docker Compose with hardcoded passwords")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:*.pem OR filename:*.key',
        "PEM/key certificate files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:wp-config.php',
        "WordPress config files")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:.npmrc "_authToken"',
        "npm auth tokens in .npmrc")
    add(DorkCategory.SENSITIVE_FILES,
        f'org:{org} filename:.pypirc "password"',
        "PyPI credentials in .pypirc")

    # ── Misconfigurations ──────────────────────────────────────────────────
    add(DorkCategory.MISCONFIGS,
        f'org:{org} "DEBUG = True" extension:py',
        "Django DEBUG mode enabled")
    add(DorkCategory.MISCONFIGS,
        f'org:{org} "debug: true" extension:yml OR extension:yaml',
        "Debug mode in config files")
    add(DorkCategory.MISCONFIGS,
        f'org:{org} "allow_all_origins = True" extension:py',
        "CORS allow all origins (Django)")
    add(DorkCategory.MISCONFIGS,
        f'org:{org} "ALLOWED_HOSTS = [\"*\"]"',
        "Django ALLOWED_HOSTS wildcard")
    add(DorkCategory.MISCONFIGS,
        f'org:{org} "0.0.0.0" extension:env OR extension:yml',
        "Services bound to 0.0.0.0")

    # ── Code Leaks ─────────────────────────────────────────────────────────
    add(DorkCategory.CODE_LEAKS,
        f'org:{org} "TODO: remove" "key" OR "password" OR "secret"',
        "TODO comments mentioning credentials")
    add(DorkCategory.CODE_LEAKS,
        f'org:{org} "hardcoded" "password" OR "key"',
        "Hardcoded credential comments")
    add(DorkCategory.CODE_LEAKS,
        f'org:{org} "internal use only"',
        "Internal-only code accidentally public")
    add(DorkCategory.CODE_LEAKS,
        f'org:{org} "do not commit" OR "do not push"',
        "Files flagged not to commit")

    # ── Domain-based (for non-GitHub targets) ─────────────────────────────
    if target.domain and "github.com" not in target.domain:
        add(DorkCategory.SECRETS,
            f'"{d}" "api_key" OR "secret" OR "token"',
            f"Secrets referencing {d} domain")
        add(DorkCategory.SENSITIVE_FILES,
            f'"{d}" filename:.env',
            f".env files referencing {d}")
        add(DorkCategory.MISCONFIGS,
            f'"{d}" "DB_HOST" OR "DATABASE_URL"',
            f"Database configs referencing {d}")

    # ── Tech-specific ──────────────────────────────────────────────────────
    for tech in target.tech_stack:
        if tech == "aws":
            add(DorkCategory.SECRETS,
                f'org:{org} "aws_access_key_id"',
                "AWS credentials in repos")
        elif tech == "gcp":
            add(DorkCategory.SECRETS,
                f'org:{org} "type" "service_account" filename:*.json',
                "GCP service account JSON keys")
        elif tech == "azure":
            add(DorkCategory.SECRETS,
                f'org:{org} "DefaultEndpointsProtocol=https;AccountName"',
                "Azure storage connection strings")
        elif tech == "terraform":
            add(DorkCategory.MISCONFIGS,
                f'org:{org} filename:terraform.tfvars "password" OR "secret"',
                "Terraform var files with secrets")
        elif tech == "django":
            add(DorkCategory.SECRETS,
                f'org:{org} "SECRET_KEY" extension:py OR extension:env',
                "Django SECRET_KEY exposed")

    return dorks
