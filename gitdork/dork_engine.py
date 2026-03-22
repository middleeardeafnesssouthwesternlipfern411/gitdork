"""Core dork generation engine."""

from __future__ import annotations

from .models import DorkCategory, DorkEngine, DorkResult, Target
from .templates import github, google, shodan


def generate(
    target: Target,
    engines: list[DorkEngine] | None = None,
    categories: list[DorkCategory] | None = None,
) -> DorkResult:
    """
    Generate dorks for a target across selected engines and categories.

    Args:
        target: Parsed Target object
        engines: Which engines to generate for (default: all)
        categories: Which categories to include (default: all)

    Returns:
        DorkResult containing all generated dorks
    """
    if engines is None:
        engines = list(DorkEngine)

    result = DorkResult(target=target)

    if DorkEngine.GOOGLE in engines:
        result.dorks.extend(google.generate(target))

    if DorkEngine.SHODAN in engines:
        result.dorks.extend(shodan.generate(target))

    if DorkEngine.GITHUB in engines:
        result.dorks.extend(github.generate(target))

    # Apply category filter
    if categories:
        result.dorks = [d for d in result.dorks if d.category in categories]

    # Populate search URLs
    for dork in result.dorks:
        dork.with_url()

    return result
