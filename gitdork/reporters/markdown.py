"""Markdown reporter — great for saving to a file or pasting into notes."""

from __future__ import annotations

from pathlib import Path

from ..models import CATEGORY_LABELS, DorkCategory, DorkEngine, DorkResult

ENGINE_EMOJIS = {
    DorkEngine.GOOGLE: "🔍",
    DorkEngine.SHODAN: "🌐",
    DorkEngine.GITHUB: "🐙",
}


def to_markdown(result: DorkResult) -> str:
    lines: list[str] = []

    lines.append(f"# gitdork — {result.target.display}")
    lines.append("")
    lines.append(f"**Target:** `{result.target.raw}`")
    if result.target.tech_stack:
        lines.append(
            f"**Tech stack:** {', '.join(result.target.tech_stack)}"
        )
    lines.append(
        f"**Total dorks:** {result.total} "
        f"(Google: {result.google_count}, "
        f"Shodan: {result.shodan_count}, "
        f"GitHub: {result.github_count})"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    for engine in DorkEngine:
        dorks = result.by_engine(engine)
        if not dorks:
            continue

        emoji = ENGINE_EMOJIS[engine]
        lines.append(f"## {emoji} {engine.value.capitalize()} Dorks")
        lines.append("")

        current_cat = None
        for dork in dorks:
            if dork.category != current_cat:
                current_cat = dork.category
                label = CATEGORY_LABELS.get(current_cat, current_cat.value)
                lines.append(f"### {label}")
                lines.append("")

            lines.append(f"**{dork.description}**")
            lines.append(f"```")
            lines.append(dork.query)
            lines.append(f"```")
            if dork.url:
                lines.append(f"[Open in {engine.value.capitalize()}]({dork.url})")
            lines.append("")

    return "\n".join(lines)


def write(result: DorkResult, output_path: Path):
    output_path.write_text(to_markdown(result), encoding="utf-8")
