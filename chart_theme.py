"""Light / dark chart themes — background matches slide."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChartTheme:
    name: str
    bg: str
    text: str
    palette: tuple[str, ...]
    axis: str
    grid: str


LIGHT = ChartTheme(
    name="light",
    bg="#f1f3f5",
    text="#0a1f3d",
    palette=(
        "#0a1f3d", "#1e4a7a", "#2d6cb5", "#5b8fc9", "#8fb3dc",
        "#c4a574", "#8b6b4a", "#6b4c8a", "#3d8b7a", "#b85c4a",
    ),
    axis="#5a6d85",
    grid="rgba(10,31,61,.12)",
)

DARK = ChartTheme(
    name="dark",
    bg="#0a1f3d",
    text="#e8ecf2",
    palette=(
        "#e8ecf2", "#b8c9e0", "#8fb3dc", "#5b8fc9", "#3d7ab8",
        "#e8d4b0", "#c4a574", "#a88bc4", "#6bc4b0", "#d49a8a",
    ),
    axis="#8fa3bf",
    grid="rgba(232,236,242,.15)",
)
