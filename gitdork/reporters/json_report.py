"""JSON reporter."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import DorkResult


def to_dict(result: DorkResult) -> dict:
    return {
        "target": {
            "raw": result.target.raw,
            "domain": result.target.domain,
            "org": result.target.org,
            "repo": result.target.repo,
            "tech_stack": result.target.tech_stack,
        },
        "summary": {
            "total": result.total,
            "google": result.google_count,
            "shodan": result.shodan_count,
            "github": result.github_count,
        },
        "dorks": [
            {
                "engine": d.engine.value,
                "category": d.category.value,
                "description": d.description,
                "query": d.query,
                "url": d.url,
            }
            for d in result.dorks
        ],
    }


def write(result: DorkResult, output_path: Path):
    output_path.write_text(
        json.dumps(to_dict(result), indent=2), encoding="utf-8"
    )


def print_json(result: DorkResult):
    import click
    click.echo(json.dumps(to_dict(result), indent=2))
