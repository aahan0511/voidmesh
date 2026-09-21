"""Public graph data types."""

from __future__ import annotations

from dataclasses import dataclass, field

type Color = str | tuple[int, int, int]


@dataclass(slots=True)
class Node:
    """A node on a :class:`voidmesh.Canvas`."""

    id: str
    value: object = ""
    color: Color = "#a78bfa"
    x: float = 0.0
    y: float = 0.0
    radius: float = 10.0
    fixed: bool = False
    font: str | None = None
    font_size: float | None = None
    vx: float = field(default=0.0, repr=False)
    vy: float = field(default=0.0, repr=False)

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y


@dataclass(slots=True)
class Link:
    """An elastic connection between two nodes."""

    id: str
    source: str
    target: str
    color: Color = "#64748b"
    width: float = 1.5
    length: float = 115.0
    elasticity: float = 0.035
