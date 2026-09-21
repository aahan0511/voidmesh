# Voidmesh

A small Python 3.12+ library for building and displaying live, Obsidian-inspired
force-directed graphs. Values are rendered inside draggable rounded nodes;
links act like springs; gravity and repulsion settle the graph into place.

## Install

```console
uv add voidmesh
```

Or with `pip`:

```console
python -m pip install voidmesh
```

For local development:

```console
uv sync
uv run voidmesh-demo
```

## Quick start

```python
from voidmesh import Canvas

canvas = Canvas(title="My graph", grid=True)
python = canvas.add_node("Python", color="#fbbf24")
graphs = canvas.add_node("Graphs", color="#a78bfa")
edge = canvas.link(python, graphs, color="#38bdf8")

# Keep executing code while the window stays responsive.
canvas.show(block=False)

canvas.update_node(graphs, value="Live graphs", color="#34d399")
canvas.update_link(edge, color="#fb7185", elasticity=0.06)
canvas.wait()  # Keep the script alive until the window is closed.
```

All mutating methods update an open window immediately:

```python
third = canvas.add_node("New")
canvas.relink(edge, target=third)
canvas.unlink(edge)  # or canvas.unlink(python, third)
canvas.delete_node(graphs)  # also deletes attached links
canvas.clear()
canvas.close()
```

Call `canvas.show()` without arguments for a blocking window. Drag nodes with
the left mouse button, pan with the right mouse button, zoom with the wheel, and
press Escape to close. `fixed=True` pins a node after it is dragged. The force
center is the origin until fixed nodes exist, then becomes their shared center.
There is no artificial limit on graph zoom.

Press `E` in an open window to export its graph view to `voidmesh-export.png` at
4K (3840×2160). To choose the output location or a higher resolution:

```python
canvas.export_png("exports/my-graph.png", width=7680, height=4320)
```

The **Controls** panel changes center force, repulsion, link force, and link
distance while the graph is moving. Drag its heading to reposition it, or click
the chevron to collapse it. Press `F` to hide or show the panel and `G` to
toggle the background grid.

Physics and the grid can also be controlled from Python:

```python
canvas.configure_physics(
    center_force=0.2,
    repel_force=8,
    link_force=0.4,
    link_distance=190,
    damping=0.92,
)
canvas.toggle_grid(True)
```

The same values can be passed to `Canvas(...)`. Set `controls=False` for a
minimal window without the controls panel. Controls scale automatically with the
window; use `ui_scale=1.5` (or another positive multiplier) to override their
size on a HiDPI display. Graph zoom and UI scale are intentionally independent.

Switch to a deterministic, physics-free hierarchy with `layout="tree"`, the
Tree button in the panel, or the `T` key. Links are interpreted as parent to
child in this view. See the bundled example:

```console
uv run python examples/tree_view.py
```

Fonts, type size, node padding and roundness, link thickness, and grid color
can be set on `Canvas(...)` or changed live with `configure_style()`.

## Development

```console
uv run pytest
uv run ruff check .
uv build
uv run mkdocs serve
```

Complete documentation lives in [`docs/`](docs/index.md). Build it with
`uv run mkdocs build --strict`.

Voidmesh is licensed under the MIT License.
