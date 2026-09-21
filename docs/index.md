# Voidmesh

Voidmesh is a compact Python 3.14 library for displaying mutable graphs in a
clean desktop window. It supports two complementary views:

- **Force view** — nodes repel one another, links behave like springs, and a
  center force keeps the graph nearby.
- **Tree view** — directed parent→child links are arranged into a stable,
  top-down hierarchy with no physics.

Node values appear inside rounded, draggable tiles. A running window reflects
changes made by Python immediately.

```python
from voidmesh import Canvas

canvas = Canvas(title="Knowledge graph", grid=True)
root = canvas.add_node("Voidmesh", color="#f8fafc")
physics = canvas.add_node("Physics", color="#a78bfa")
trees = canvas.add_node("Trees", color="#38bdf8")
canvas.link(root, physics, color="#8b5cf6")
canvas.link(root, trees, color="#0ea5e9")
canvas.show()
```

## Highlights

- Add, update, relink, unlink, and delete graph elements at runtime.
- Tune four visibly different force parameters from a movable control panel.
- Switch between force and tree views without rebuilding the graph.
- Pan, zoom, drag nodes, and toggle a zoom-aware background grid.
- Customize fonts, type size, node padding, corner radius, colors, and links.
- Use blocking or non-blocking windows from ordinary Python scripts.

[Get started](getting-started.md){ .md-button .md-button--primary }
[Browse the API](reference/api.md){ .md-button }
