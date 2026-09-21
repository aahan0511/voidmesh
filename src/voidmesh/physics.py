"""The dependency-free force simulation used by the renderer."""

from __future__ import annotations

import math
from collections.abc import Iterable

from .models import Link, Node


class Physics:
    """A stable force-directed layout with springs and center gravity."""

    def __init__(
        self,
        *,
        center_force: float = 0.12,
        repel_force: float = 4.0,
        link_force: float = 0.35,
        link_distance: float = 150.0,
        damping: float = 0.9,
        max_speed: float = 520.0,
        gravity: float | None = None,
        repulsion: float | None = None,
    ) -> None:
        if gravity is not None:
            center_force = gravity / 0.12
        if repulsion is not None:
            repel_force = repulsion / 900.0
        self.center_force = center_force
        self.repel_force = repel_force
        self.link_force = link_force
        self.link_distance = link_distance
        self.damping = damping
        self.max_speed = max_speed

    def step(
        self,
        nodes: dict[str, Node],
        links: Iterable[Link],
        dt: float,
    ) -> None:
        """Advance the layout by ``dt`` seconds, mutating node positions."""
        if not nodes or dt <= 0:
            return
        dt = min(dt, 1 / 20)
        forces = {node_id: [0.0, 0.0] for node_id in nodes}
        node_list = list(nodes.values())

        for index, left in enumerate(node_list):
            for right in node_list[index + 1 :]:
                dx = right.x - left.x
                dy = right.y - left.y
                distance_sq = dx * dx + dy * dy
                if distance_sq < 1.0:
                    dx, dy, distance_sq = 1.0, 0.5, 1.25
                distance = math.sqrt(distance_sq)
                magnitude = (self.repel_force * 900.0) / distance_sq
                fx = magnitude * dx / distance
                fy = magnitude * dy / distance
                forces[left.id][0] -= fx
                forces[left.id][1] -= fy
                forces[right.id][0] += fx
                forces[right.id][1] += fy

        for link in links:
            source = nodes.get(link.source)
            target = nodes.get(link.target)
            if source is None or target is None:
                continue
            dx = target.x - source.x
            dy = target.y - source.y
            distance = max(math.hypot(dx, dy), 0.001)
            preferred_length = link.length * (self.link_distance / 115.0)
            magnitude = link.elasticity * self.link_force * 4.0 * (distance - preferred_length)
            fx = magnitude * dx / distance
            fy = magnitude * dy / distance
            forces[source.id][0] += fx
            forces[source.id][1] += fy
            forces[target.id][0] -= fx
            forces[target.id][1] -= fy

        fixed_nodes = [node for node in node_list if node.fixed]
        if fixed_nodes:
            center_x = sum(node.x for node in fixed_nodes) / len(fixed_nodes)
            center_y = sum(node.y for node in fixed_nodes) / len(fixed_nodes)
        else:
            center_x = center_y = 0.0

        for node in node_list:
            if node.fixed:
                node.vx = node.vy = 0.0
                continue
            fx, fy = forces[node.id]
            gravity = self.center_force * 0.12
            fx -= (node.x - center_x) * gravity
            fy -= (node.y - center_y) * gravity
            node.vx = (node.vx + fx * dt * 60.0) * self.damping
            node.vy = (node.vy + fy * dt * 60.0) * self.damping
            speed = math.hypot(node.vx, node.vy)
            if speed > self.max_speed:
                scale = self.max_speed / speed
                node.vx *= scale
                node.vy *= scale
            node.x += node.vx * dt
            node.y += node.vy * dt
