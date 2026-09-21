"""Deterministic, non-physical graph layouts."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Link, Node


class TreeLayout:
    """Lay directed source-to-target links out as a top-down forest."""

    def __init__(
        self, *, horizontal_spacing: float = 150, vertical_spacing: float = 110
    ) -> None:
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    def apply(self, nodes: dict[str, Node], links: Iterable[Link]) -> None:
        if not nodes:
            return

        children = {node_id: [] for node_id in nodes}
        parent: dict[str, str] = {}
        for link in links:
            if (
                link.source in nodes
                and link.target in nodes
                and link.source != link.target
                and link.target not in parent
            ):
                parent[link.target] = link.source
                children[link.source].append(link.target)

        roots = [node_id for node_id in nodes if node_id not in parent]
        if not roots:
            roots = [next(iter(nodes))]

        positions: dict[str, tuple[float, int]] = {}
        placed: set[str] = set()
        cursor = 0.0
        max_depth = 0

        def place(node_id: str, depth: int, left: float, visiting: set[str]) -> float:
            nonlocal max_depth
            if node_id in placed or node_id in visiting:
                return 0.0
            visiting.add(node_id)
            placed.add(node_id)
            max_depth = max(max_depth, depth)
            valid_children = [child for child in children[node_id] if child not in placed]
            own_width = max(
                self.horizontal_spacing,
                len(str(nodes[node_id].value)) * 9.0 + 54.0,
            )
            if not valid_children:
                positions[node_id] = (left + own_width / 2, depth)
                visiting.remove(node_id)
                return own_width

            child_left = left
            child_centers: list[float] = []
            total_width = 0.0
            for child in valid_children:
                width = place(child, depth + 1, child_left, visiting)
                if width > 0:
                    child_centers.append(positions[child][0])
                    child_left += width
                    total_width += width
            width = max(own_width, total_width)
            center = (
                sum(child_centers) / len(child_centers) if child_centers else left + width / 2
            )
            positions[node_id] = (center, depth)
            visiting.remove(node_id)
            return width

        for root in roots:
            width = place(root, 0, cursor, set())
            cursor += width + self.horizontal_spacing * 0.6
        for node_id in nodes:
            if node_id not in placed:
                width = place(node_id, 0, cursor, set())
                cursor += width + self.horizontal_spacing * 0.6

        total_width = max(cursor - self.horizontal_spacing * 0.6, 0.0)
        y_offset = max_depth * self.vertical_spacing / 2
        for node_id, (x, depth) in positions.items():
            node = nodes[node_id]
            node.x = x - total_width / 2
            node.y = depth * self.vertical_spacing - y_offset
            node.vx = node.vy = 0.0
