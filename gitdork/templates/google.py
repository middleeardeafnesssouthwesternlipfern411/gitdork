"""Google dork templates."""

from __future__ import annotations

from ..models import Dork, DorkCategory, DorkEngine, Target


def generate(target: Target) -> list[Dork]:
    dorks: list[Dork] = []
    d = target.domain or target.raw
    org = target.org or d

    def add(category: DorkCategory, query: str, description: str):
        dorks.append(Dork(
            engine=DorkEngine.GOOGLE,
            category=category,
            query=query,
            description=description,
        ))

    # ── Secrets & Credentials ──────────────────────────────────────────────
    add(DorkCategory.SECRETS,
        f'site:github.com "{org}" "api_key"',
        "API keys exposed in GitHub")
    add(DorkCategory.SECRETS,
        f'site:github.com "{org}" "secret_key"',
        "Secret keys in GitHub")
    add(DorkCategory.SECRETS,
        f'site:github.com "{org}" "access_token"',
        "Access tokens in GitHub")
    add(DorkCategory.SECRETS,
        f'site:github.com "{org}" "password" filetype:env',
        ".env files with passwords")
    add(DorkCategory.SECRETS,
        f'site:pastebin.com "{org}" password',
        "Credentials pasted on Pastebin")
    add(DorkCategory.SECRETS,
        f'site:pastebin.com "{d}" "api_key" OR "token" OR "secret"',
        "API keys pasted on Pastebin")
    add(DorkCategory.SECRETS,
        f'site:trello.com "{org}" password',
        "Passwords leaked on Trello boards")
    add(DorkCategory.SECRETS,
        f'site:jsfiddle.net "{d}" password OR secret OR token',
        "Secrets in JSFiddle snippets")
    add(DorkCategory.SECRETS,
        f'"{d}" "BEGIN RSA PRIVATE KEY"',
        "RSA private keys indexed by Google")
    add(DorkCategory.SECRETS,
        f'"{d}" "BEGIN OPENSSH PRIVATE KEY"',
        "OpenSSH private keys")
    add(DorkCategory.SECRETS,
        f'site:github.com "{org}" "AKIA" OR "ghp_" OR "sk-"',
        "AWS/GitHub/OpenAI keys in repos")

    # ── Sensitive Files ────────────────────────────────────────────────────
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:env',
        ".env files exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:log',
        "Log files exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:sql',
        "SQL dump files exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:bak OR filetype:backup OR filetype:old',
        "Backup files exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:conf OR filetype:config',
        "Config files exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:xml inurl:config',
        "XML config files")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} filetype:json inurl:config OR inurl:settings',
        "JSON config/settings files")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} "wp-config.php"',
        "WordPress config exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} inurl:".git/config"',
        "Git config file exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} inurl:"phpinfo.php"',
        "phpinfo page exposed")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} inurl:".DS_Store"',
        ".DS_Store file exposed (reveals directory structure)")
    add(DorkCategory.SENSITIVE_FILES,
        f'site:{d} inurl:"composer.json" OR inurl:"package.json"',
        "Dependency manifests with version info")

    # ── Exposed Directories ────────────────────────────────────────────────
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of /"',
        "Open directory listings")
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of" inurl:backup',
        "Backup directory listings")
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of" inurl:upload',
        "Upload directory exposed")
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of" inurl:admin',
        "Admin directory listing")
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of" "password"',
        "Directory listing containing password files")
    add(DorkCategory.EXPOSED_DIRS,
        f'site:{d} intitle:"index of" ".env"',
        "Directory with .env files")

    # ── Misconfigurations ──────────────────────────────────────────────────
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:phpMyAdmin',
        "phpMyAdmin exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:adminer',
        "Adminer DB interface exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/.env" "DB_PASSWORD"',
        ".env file with database password")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/_cpanel"',
        "cPanel exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/jenkins"',
        "Jenkins CI exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/grafana"',
        "Grafana dashboard exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/kibana"',
        "Kibana exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/actuator" OR inurl:"/actuator/health"',
        "Spring Boot actuator endpoints exposed")
    add(DorkCategory.MISCONFIGS,
        f'site:{d} inurl:"/.well-known/security.txt"',
        "Security.txt — useful for recon")

    # ── Login Panels ───────────────────────────────────────────────────────
    add(DorkCategory.LOGIN_PANELS,
        f'site:{d} inurl:login OR inurl:signin OR inurl:admin',
        "Login / admin panels")
    add(DorkCategory.LOGIN_PANELS,
        f'site:{d} intitle:"login" OR intitle:"sign in"',
        "Login page by title")
    add(DorkCategory.LOGIN_PANELS,
        f'site:{d} inurl:wp-login.php',
        "WordPress login page")
    add(DorkCategory.LOGIN_PANELS,
        f'site:{d} inurl:"/admin/login"',
        "Admin login panel")
    add(DorkCategory.LOGIN_PANELS,
        f'site:{d} inurl:"/user/login" OR inurl:"/account/login"',
        "User account login")

    # ── Error Pages ────────────────────────────────────────────────────────
    add(DorkCategory.ERROR_PAGES,
        f'site:{d} "Fatal error" OR "Warning:" "on line"',
        "PHP error messages revealing code paths")
    add(DorkCategory.ERROR_PAGES,
        f'site:{d} intext:"stack trace" "Exception"',
        "Stack traces exposed")
    add(DorkCategory.ERROR_PAGES,
        f'site:{d} intitle:"500 Internal Server Error"',
        "500 error pages")
    add(DorkCategory.ERROR_PAGES,
        f'site:{d} intext:"SQL syntax" OR intext:"mysql_fetch"',
        "SQL error messages — possible SQLi")
    add(DorkCategory.ERROR_PAGES,
        f'site:{d} intext:"Traceback (most recent call last)"',
        "Python tracebacks exposed")

    # ── Subdomains & Infra ─────────────────────────────────────────────────
    add(DorkCategory.SUBDOMAINS,
        f'site:{d} -www',
        "All subdomains except www")
    add(DorkCategory.SUBDOMAINS,
        f'site:*.{d}',
        "Wildcard subdomain enumeration")
    add(DorkCategory.SUBDOMAINS,
        f'site:{d} inurl:dev OR inurl:staging OR inurl:test',
        "Dev/staging/test environments")
    add(DorkCategory.SUBDOMAINS,
        f'site:{d} inurl:api',
        "API subdomains/endpoints")
    add(DorkCategory.SUBDOMAINS,
        f'site:{d} inurl:vpn OR inurl:remote OR inurl:mail',
        "VPN / remote access / mail portals")

    # ── Tech-specific dorks ────────────────────────────────────────────────
    for tech in target.tech_stack:
        if tech == "wordpress":
            add(DorkCategory.MISCONFIGS,
                f'site:{d} inurl:wp-content/uploads filetype:php',
                "PHP files in WordPress uploads")
        elif tech == "django":
            add(DorkCategory.ERROR_PAGES,
                f'site:{d} "Django" "DebugToolbar" OR "DEBUG = True"',
                "Django debug mode exposed")
        elif tech == "laravel":
            add(DorkCategory.MISCONFIGS,
                f'site:{d} inurl:"/.env" "APP_KEY"',
                "Laravel .env with APP_KEY")
        elif tech == "spring":
            add(DorkCategory.MISCONFIGS,
                f'site:{d} inurl:"/actuator/env"',
                "Spring Boot env actuator")

    return dorks
