"""Shodan dork templates."""

from __future__ import annotations

from ..models import Dork, DorkCategory, DorkEngine, Target


def generate(target: Target) -> list[Dork]:
    dorks: list[Dork] = []
    d = target.domain or target.raw

    # Strip subdomains to get root domain for hostname searches
    parts = d.split(".")
    root = ".".join(parts[-2:]) if len(parts) >= 2 else d

    def add(category: DorkCategory, query: str, description: str):
        dorks.append(Dork(
            engine=DorkEngine.SHODAN,
            category=category,
            query=query,
            description=description,
        ))

    # ── Infrastructure & Exposure ──────────────────────────────────────────
    add(DorkCategory.SUBDOMAINS,
        f'hostname:"{root}"',
        "All hosts under this domain")
    add(DorkCategory.SUBDOMAINS,
        f'ssl.cert.subject.cn:"{root}"',
        "Hosts by SSL certificate CN")
    add(DorkCategory.SUBDOMAINS,
        f'ssl.cert.subject.commonName:"*.{root}"',
        "Wildcard certificate hosts")
    add(DorkCategory.SUBDOMAINS,
        f'http.title:"{target.org or root}"',
        "Hosts with org name in page title")

    # ── Exposed Services ───────────────────────────────────────────────────
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:22',
        "SSH exposed on this domain")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:3389',
        "RDP exposed (Windows Remote Desktop)")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:5900',
        "VNC exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:6379',
        "Redis exposed (often no auth)")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:27017',
        "MongoDB exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:9200',
        "Elasticsearch exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:5601',
        "Kibana exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:8080',
        "HTTP alt port (Jenkins, dev servers)")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:4444',
        "Port 4444 — common C2/Metasploit default")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:2375',
        "Docker API exposed (no TLS)")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:2376',
        "Docker API with TLS")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:6443 OR port:8443',
        "Kubernetes API server")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:9090',
        "Prometheus metrics exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:3000',
        "Grafana / dev server exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:5432',
        "PostgreSQL exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:3306',
        "MySQL exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:1521',
        "Oracle DB exposed")
    add(DorkCategory.MISCONFIGS,
        f'hostname:"{root}" port:25 OR port:587 OR port:465',
        "Mail server (SMTP) exposed")

    # ── Admin / Login Panels ───────────────────────────────────────────────
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"admin"',
        "Admin panel by page title")
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"login"',
        "Login page by title")
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"phpMyAdmin"',
        "phpMyAdmin panel")
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"Grafana"',
        "Grafana dashboard")
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"Jenkins"',
        "Jenkins CI panel")
    add(DorkCategory.LOGIN_PANELS,
        f'hostname:"{root}" http.title:"GitLab"',
        "GitLab instance")

    # ── Sensitive Content ──────────────────────────────────────────────────
    add(DorkCategory.SENSITIVE_FILES,
        f'hostname:"{root}" http.html:"index of /"',
        "Open directory listings")
    add(DorkCategory.SENSITIVE_FILES,
        f'hostname:"{root}" http.html:"DB_PASSWORD"',
        ".env content in HTTP response")
    add(DorkCategory.SENSITIVE_FILES,
        f'hostname:"{root}" http.html:"BEGIN RSA PRIVATE KEY"',
        "RSA private key in HTTP response")
    add(DorkCategory.SENSITIVE_FILES,
        f'hostname:"{root}" http.html:"stack trace"',
        "Stack traces in HTTP responses")

    # ── SSL / Certificate ──────────────────────────────────────────────────
    add(DorkCategory.SUBDOMAINS,
        f'ssl.cert.subject.cn:"{root}" 200',
        "Live hosts with valid SSL cert")
    add(DorkCategory.MISCONFIGS,
        f'ssl.cert.expired:true hostname:"{root}"',
        "Hosts with expired SSL certificates")

    # ── Tech-specific ──────────────────────────────────────────────────────
    for tech in target.tech_stack:
        if tech == "elasticsearch":
            add(DorkCategory.MISCONFIGS,
                f'hostname:"{root}" port:9200 product:"Elastic"',
                "Elasticsearch cluster")
        elif tech == "redis":
            add(DorkCategory.MISCONFIGS,
                f'hostname:"{root}" port:6379 product:"Redis"',
                "Redis server (check for no-auth)")
        elif tech == "kubernetes":
            add(DorkCategory.MISCONFIGS,
                f'hostname:"{root}" product:"Kubernetes"',
                "Kubernetes API")
        elif tech == "docker":
            add(DorkCategory.MISCONFIGS,
                f'hostname:"{root}" port:2375 product:"Docker"',
                "Unauthenticated Docker daemon")

    return dorks
