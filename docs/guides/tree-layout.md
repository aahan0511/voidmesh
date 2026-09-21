# Tree layout

Tree view is deterministic and does not run physics. It interprets every link
as `source → target`, where source is a parent and target is a child.

```python
from voidmesh import Canvas

canvas = Canvas(
    layout="tree",
    tree_horizontal_spacing=170,
    tree_vertical_spacing=120,
)

root = canvas.add_node("Company")
engineering = canvas.add_node("Engineering")
design = canvas.add_node("Design")
canvas.link(root, engineering)
canvas.link(root, design)
canvas.link(engineering, canvas.add_node("Platform"))
canvas.link(engineering, canvas.add_node("Product"))
canvas.show()
```

The layout:

- finds nodes without parents and treats them as roots;
- supports multiple disconnected trees as a forest;
- sizes horizontal slots using label length;
- centers parents over their children;
- tolerates cycles without hanging;
- resets node velocity because no simulation is active.

If multiple links try to assign different parents to one node, the first link
added defines its tree parent. All links remain visible.

Switch views at runtime through the panel, with `T`, or from Python:

```python
canvas.set_layout("tree")
canvas.set_layout("force")
```

Tree positions are recomputed when the graph is rendered, so dragging a tree
node is temporary. Switch to force view when free positioning is desired.
