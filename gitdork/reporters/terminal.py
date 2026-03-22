"""Rich terminal reporter."""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import (
    CATEGORY_LABELS,
    DorkCategory,
    DorkEngine,
    DorkResult,
)

console = Console(highlight=False)

ENGINE_COLORS = {
    DorkEngine.GOOGLE: "cyan",
    DorkEngine.SHODAN: "red",
    DorkEngine.GITHUB: "green",
}

ENGINE_LABELS = {
    DorkEngine.GOOGLE: "GOOGLE",
    DorkEngine.SHODAN: "SHODAN",
    DorkEngine.GITHUB: "GITHUB",
}


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]gitdork[/bold cyan] "
        "[dim]— Google, Shodan & GitHub dork generator[/dim]",
        border_style="cyan",
    ))


def print_results(result: DorkResult, group_by: str = "engine"):
    console.print(
        f"\n[dim]Target:[/dim] [bold white]{result.target.display}[/bold white]"
    )
    if result.target.tech_stack:
        stack = ", ".join(result.target.tech_stack)
        console.print(f"[dim]Tech stack detected:[/dim] [cyan]{stack}[/cyan]")
    console.print()

    if not result.dorks:
        console.print("[yellow]No dorks generated.[/yellow]")
        return

    if group_by == "engine":
        _print_by_engine(result)
    else:
        _print_by_category(result)

    _print_summary(result)


def _print_by_engine(result: DorkResult):
    for engine in DorkEngine:
        dorks = result.by_engine(engine)
        if not dorks:
            continue

        color = ENGINE_COLORS[engine]
        label = ENGINE_LABELS[engine]
        console.print(f"[bold {color}]── {label} ({'─' * (50 - len(label))})[/bold {color}]")

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="dim",
            padding=(0, 1),
            expand=True,
        )
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("CATEGORY", width=18, style="dim")
        table.add_column("DESCRIPTION", width=35)
        table.add_column("QUERY")

        for i, dork in enumerate(dorks, 1):
            cat_label = CATEGORY_LABELS.get(dork.category, dork.category.value)
            table.add_row(
                str(i),
                cat_label,
                dork.description,
                f"[{color}]{dork.query}[/{color}]",
            )

        console.print(table)


def _print_by_category(result: DorkResult):
    for cat in DorkCategory:
        dorks = result.by_category(cat)
        if not dorks:
            continue

        label = CATEGORY_LABELS.get(cat, cat.value)
        console.print(f"\n[bold white]── {label}[/bold white]")

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="dim",
            padding=(0, 1),
            expand=True,
        )
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("ENGINE", width=8)
        table.add_column("DESCRIPTION", width=38)
        table.add_column("QUERY")

        for i, dork in enumerate(dorks, 1):
            color = ENGINE_COLORS[dork.engine]
            table.add_row(
                str(i),
                f"[{color}]{dork.engine.value.upper()}[/{color}]",
                dork.description,
                dork.query,
            )

        console.print(table)


def _print_summary(result: DorkResult):
    table = Table(
        box=box.SIMPLE_HEAD, show_header=False, padding=(0, 2)
    )
    table.add_column(style="dim")
    table.add_column(justify="right")

    table.add_row("Total dorks", str(result.total))
    table.add_row(
        "[cyan]Google[/cyan]", f"[cyan]{result.google_count}[/cyan]"
    )
    table.add_row(
        "[red]Shodan[/red]", f"[red]{result.shodan_count}[/red]"
    )
    table.add_row(
        "[green]GitHub[/green]", f"[green]{result.github_count}[/green]"
    )

    console.print(Panel(
        table, title="[bold]Summary[/bold]", border_style="dim"
    ))
