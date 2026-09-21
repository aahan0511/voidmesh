"""The graph model and its live-window lifecycle."""

from __future__ import annotations

import math
import random
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from typing import Any, Self

from .layout import TreeLayout
from .models import Color, Link, Node
from .physics import Physics


class Canvas:
    """A mutable graph displayed on a clean, physics-based canvas.

    Graph operations are thread-safe. Call ``show(block=False)`` to keep
    executing Python while the window reflects later changes in real time.
    """

    def __init__(
        self,
        *,
        title: str = "Voidmesh",
        width: int = 1000,
        height: int = 700,
        background: Color = "#090b12",
        center_force: float = 0.12,
        repel_force: float = 4.0,
        link_force: float = 0.35,
        link_distance: float = 150.0,
        damping: float = 0.9,
        layout: str = "force",
        tree_horizontal_spacing: float = 150.0,
        tree_vertical_spacing: float = 110.0,
        grid: bool = False,
        grid_color: Color = "#30384a",
        controls: bool = True,
        ui_scale: float | None = None,
        node_font: str = "sans",
        node_font_size: float = 15.0,
        node_padding: tuple[float, float] = (12.0, 7.0),
        node_roundness: float = 9.0,
        link_width: float = 1.5,
        fps: int = 60,
        gravity: float | None = None,
        repulsion: float | None = None,
    ) -> None:
        if width < 200 or height < 200:
            raise ValueError("width and height must be at least 200")
        if layout not in {"force", "tree"}:
            raise ValueError("layout must be 'force' or 'tree'")
        if node_font_size <= 0 or node_roundness < 0 or link_width <= 0:
            raise ValueError(
                "font size/link width must be positive; roundness cannot be negative"
            )
        if len(node_padding) != 2 or min(node_padding) < 0:
            raise ValueError("node_padding must contain two non-negative values")
        self.title = title
        self.width = width
        self.height = height
        self.background = background
        self.grid = grid
        self.grid_color = grid_color
        self.controls = controls
        self.layout = layout
        if ui_scale is not None and ui_scale <= 0:
            raise ValueError("ui_scale must be positive")
        self.ui_scale = ui_scale
        self.node_font = node_font
        self.node_font_size = float(node_font_size)
        self.node_padding = (float(node_padding[0]), float(node_padding[1]))
        self.node_roundness = float(node_roundness)
        self.default_link_width = float(link_width)
        self.fps = fps
        self.nodes: dict[str, Node] = {}
        self.links: dict[str, Link] = {}
        self.physics = Physics(
            center_force=center_force,
            repel_force=repel_force,
            link_force=link_force,
            link_distance=link_distance,
            damping=damping,
            gravity=gravity,
            repulsion=repulsion,
        )
        self.tree_layout = TreeLayout(
            horizontal_spacing=tree_horizontal_spacing,
            vertical_spacing=tree_vertical_spacing,
        )
        self._lock = threading.RLock()
        self._window_thread: threading.Thread | None = None
        self._renderer: Any = None
        self._ready = threading.Event()
        self._window_error: BaseException | None = None

    def add_node(
        self,
        value: object = "",
        *,
        node_id: str | None = None,
        color: Color = "#a78bfa",
        position: tuple[float, float] | None = None,
        radius: float = 10.0,
        fixed: bool = False,
        font: str | None = None,
        font_size: float | None = None,
    ) -> Node:
        """Add and return a node."""
        node_id = node_id or f"node-{uuid.uuid4().hex[:8]}"
        if radius <= 0:
            raise ValueError("radius must be positive")
        if font_size is not None and font_size <= 0:
            raise ValueError("font_size must be positive")
        if position is None:
            angle = random.random() * math.tau
            distance = random.uniform(20.0, 85.0)
            position = math.cos(angle) * distance, math.sin(angle) * distance
        with self._lock:
            if node_id in self.nodes:
                raise ValueError(f"node {node_id!r} already exists")
            node = Node(
                id=node_id,
                value=value,
                color=color,
                x=float(position[0]),
                y=float(position[1]),
                radius=float(radius),
                fixed=fixed,
                font=font,
                font_size=float(font_size) if font_size is not None else None,
            )
            self.nodes[node_id] = node
            return node

    def update_node(self, node: str | Node, **changes: object) -> Node:
        """Change a node's value, color, position, radius, or fixed state."""
        allowed = {"value", "color", "position", "radius", "fixed", "font", "font_size"}
        unknown = changes.keys() - allowed
        if unknown:
            raise TypeError(f"unknown node properties: {', '.join(sorted(unknown))}")
        with self._lock:
            current = self._get_node(node)
            if "position" in changes:
                position = changes.pop("position")
                if not isinstance(position, (tuple, list)) or len(position) != 2:
                    raise ValueError("position must contain two numbers")
                current.x, current.y = float(position[0]), float(position[1])
                current.vx = current.vy = 0.0
            if "radius" in changes and float(changes["radius"]) <= 0:
                raise ValueError("radius must be positive")
            if "radius" in changes:
                changes["radius"] = float(changes["radius"])
            if "font_size" in changes and changes["font_size"] is not None:
                if float(changes["font_size"]) <= 0:
                    raise ValueError("font_size must be positive")
                changes["font_size"] = float(changes["font_size"])
            for name, value in changes.items():
                setattr(current, name, value)
            return current

    def delete_node(self, node: str | Node) -> Node:
        """Delete a node and all links attached to it."""
        with self._lock:
            current = self._get_node(node)
            attached = [
                link.id
                for link in self.links.values()
                if current.id in (link.source, link.target)
            ]
            for link_id in attached:
                del self.links[link_id]
            return self.nodes.pop(current.id)

    remove_node = delete_node

    def link(
        self,
        source: str | Node,
        target: str | Node,
        *,
        link_id: str | None = None,
        color: Color = "#64748b",
        width: float | None = None,
        length: float = 115.0,
        elasticity: float = 0.035,
    ) -> Link:
        """Create and return an elastic link between two nodes."""
        width = self.default_link_width if width is None else width
        if width <= 0 or length <= 0 or elasticity < 0:
            raise ValueError("width/length must be positive; elasticity cannot be negative")
        with self._lock:
            source_node = self._get_node(source)
            target_node = self._get_node(target)
            link_id = link_id or f"link-{uuid.uuid4().hex[:8]}"
            if link_id in self.links:
                raise ValueError(f"link {link_id!r} already exists")
            link = Link(
                id=link_id,
                source=source_node.id,
                target=target_node.id,
                color=color,
                width=float(width),
                length=float(length),
                elasticity=float(elasticity),
            )
            self.links[link_id] = link
            return link

    def update_link(self, link: str | Link, **changes: object) -> Link:
        """Change a link's color, width, length, or elasticity."""
        allowed = {"color", "width", "length", "elasticity"}
        unknown = changes.keys() - allowed
        if unknown:
            raise TypeError(f"unknown link properties: {', '.join(sorted(unknown))}")
        if "width" in changes and float(changes["width"]) <= 0:
            raise ValueError("width must be positive")
        if "length" in changes and float(changes["length"]) <= 0:
            raise ValueError("length must be positive")
        if "elasticity" in changes and float(changes["elasticity"]) < 0:
            raise ValueError("elasticity cannot be negative")
        with self._lock:
            current = self._get_link(link)
            for name, value in changes.items():
                setattr(current, name, float(value) if name != "color" else value)
            return current

    def unlink(
        self, link_or_source: str | Node | Link, target: str | Node | None = None
    ) -> Link:
        """Remove a link by link/id, or remove the first link between two nodes."""
        with self._lock:
            if target is None:
                link = self._get_link(link_or_source)
            else:
                source_id = self._get_node(link_or_source).id
                target_id = self._get_node(target).id
                link = next(
                    (
                        item
                        for item in self.links.values()
                        if {item.source, item.target} == {source_id, target_id}
                    ),
                    None,
                )
                if link is None:
                    raise KeyError(f"no link between {source_id!r} and {target_id!r}")
            return self.links.pop(link.id)

    delete_link = unlink

    def relink(
        self,
        link: str | Link,
        *,
        source: str | Node | None = None,
        target: str | Node | None = None,
    ) -> Link:
        """Move either end of an existing link."""
        with self._lock:
            current = self._get_link(link)
            if source is not None:
                current.source = self._get_node(source).id
            if target is not None:
                current.target = self._get_node(target).id
            return current

    def clear(self) -> None:
        """Remove every node and link."""
        with self._lock:
            self.nodes.clear()
            self.links.clear()

    def configure_physics(
        self,
        *,
        center_force: float | None = None,
        repel_force: float | None = None,
        link_force: float | None = None,
        link_distance: float | None = None,
        damping: float | None = None,
    ) -> None:
        """Adjust the live force simulation programmatically."""
        changes = {
            "center_force": center_force,
            "repel_force": repel_force,
            "link_force": link_force,
            "link_distance": link_distance,
            "damping": damping,
        }
        with self._lock:
            for name, value in changes.items():
                if value is None:
                    continue
                if value < 0 or (name == "link_distance" and value == 0):
                    raise ValueError(f"{name} must be positive or zero")
                setattr(self.physics, name, float(value))

    def toggle_grid(self, visible: bool | None = None) -> bool:
        """Toggle the background grid and return its new visibility."""
        with self._lock:
            self.grid = not self.grid if visible is None else bool(visible)
            return self.grid

    def set_layout(self, layout: str) -> None:
        """Switch between the live ``force`` view and systematic ``tree`` view."""
        if layout not in {"force", "tree"}:
            raise ValueError("layout must be 'force' or 'tree'")
        with self._lock:
            self.layout = layout
            if layout == "tree":
                self.tree_layout.apply(self.nodes, self.links.values())

    def configure_style(
        self,
        *,
        node_font: str | None = None,
        node_font_size: float | None = None,
        node_padding: tuple[float, float] | None = None,
        node_roundness: float | None = None,
        link_width: float | None = None,
        grid_color: Color | None = None,
    ) -> None:
        """Change the graph's visual defaults while its window is open."""
        if node_font_size is not None and node_font_size <= 0:
            raise ValueError("node_font_size must be positive")
        if node_roundness is not None and node_roundness < 0:
            raise ValueError("node_roundness cannot be negative")
        if node_padding is not None and (len(node_padding) != 2 or min(node_padding) < 0):
            raise ValueError("node_padding must contain two non-negative values")
        if link_width is not None and link_width <= 0:
            raise ValueError("link_width must be positive")
        with self._lock:
            if node_font is not None:
                self.node_font = node_font
            if node_font_size is not None:
                self.node_font_size = float(node_font_size)
            if node_padding is not None:
                self.node_padding = (float(node_padding[0]), float(node_padding[1]))
            if node_roundness is not None:
                self.node_roundness = float(node_roundness)
            if link_width is not None:
                self.default_link_width = float(link_width)
                for link in self.links.values():
                    link.width = float(link_width)
            if grid_color is not None:
                self.grid_color = grid_color

    def snapshot(self) -> tuple[tuple[Node, ...], tuple[Link, ...]]:
        """Return detached copies of the current graph state."""
        with self._lock:
            return (
                tuple(replace(node) for node in self.nodes.values()),
                tuple(replace(link) for link in self.links.values()),
            )

    @contextmanager
    def _locked_graph(self) -> Iterator[tuple[dict[str, Node], dict[str, Link]]]:
        with self._lock:
            yield self.nodes, self.links

    def show(self, *, block: bool = True) -> Canvas:
        """Open the live canvas; non-blocking mode lets the script keep running."""
        if self.is_open:
            return self
        self._ready.clear()
        self._window_error = None
        if block:
            self._run_window()
        else:
            self._window_thread = threading.Thread(
                target=self._run_window, name="voidmesh-window", daemon=True
            )
            self._window_thread.start()
            ready = self._ready.wait(timeout=5.0)
            if self._window_error is not None:
                raise RuntimeError("could not open the voidmesh window") from self._window_error
            if not ready:
                self.close()
                raise TimeoutError("the voidmesh window did not open within 5 seconds")
        return self

    run = show

    def close(self) -> None:
        """Ask the live window to close."""
        renderer = self._renderer
        if renderer is not None:
            renderer.stop()
        thread = self._window_thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def wait(self) -> None:
        """Wait for a non-blocking window to be closed by the user."""
        thread = self._window_thread
        if thread is not None and thread is not threading.current_thread():
            thread.join()

    @property
    def is_open(self) -> bool:
        return self._renderer is not None and self._renderer.running

    def _run_window(self) -> None:
        try:
            from .renderer import Renderer

            self._renderer = Renderer(self)
            self._renderer.run()
        except BaseException as error:
            self._window_error = error
            self._ready.set()
            if self._window_thread is None:
                raise
        finally:
            self._renderer = None

    def _get_node(self, node: str | Node | Link) -> Node:
        node_id = node.id if isinstance(node, Node) else node
        if not isinstance(node_id, str) or node_id not in self.nodes:
            raise KeyError(f"unknown node {node_id!r}")
        return self.nodes[node_id]

    def _get_link(self, link: str | Node | Link) -> Link:
        link_id = link.id if isinstance(link, Link) else link
        if not isinstance(link_id, str) or link_id not in self.links:
            raise KeyError(f"unknown link {link_id!r}")
        return self.links[link_id]

    def __enter__(self) -> Self:
        return self.show(block=False)

    def __exit__(self, *_: object) -> None:
        self.close()
