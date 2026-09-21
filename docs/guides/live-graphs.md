# Live graphs

## Nodes

`add_node()` returns a `Node`. Keep that object or use its string ID in later
operations.

```python
alice = canvas.add_node(
    "Alice",
    node_id="alice",
    color="#fb7185",
    position=(-100, 0),
    font="serif",
    font_size=18,
)

canvas.update_node(
    alice,
    value="Alice Smith",
    color="#f43f5e",
    position=(-120, 20),
)
```

Set `fixed=True` only when a node must ignore physics. A fixed node can still be
dragged, but it returns to its pinned state afterward.

## Links

Links accept `Node` objects or node IDs:

```python
bob = canvas.add_node("Bob", node_id="bob")
relationship = canvas.link(
    "alice",
    bob,
    color="#94a3b8",
    width=2.5,
    length=180,
    elasticity=0.04,
)

canvas.update_link(relationship, color="#38bdf8", width=3)
```

In tree view, source is the parent and target is the child. In force view links
behave visually as undirected springs.

## Remove and reconnect

```python
canvas.relink(relationship, source=bob, target=alice)
canvas.unlink(relationship)

replacement = canvas.link(alice, bob)
canvas.unlink(alice, bob)  # Removes the first link between the pair.
canvas.delete_node(alice)  # Also removes every attached link.
canvas.clear()
```

## Thread-safe live changes

Canvas mutation methods use a shared lock with the renderer. Prefer those
methods over assigning directly to `canvas.nodes` or `canvas.links` while a
window is open.

```python
import time
from voidmesh import Canvas

canvas = Canvas()
root = canvas.add_node("Start")
canvas.show(block=False)

for number in range(5):
    child = canvas.add_node(f"Item {number}")
    canvas.link(root, child)
    time.sleep(0.4)

canvas.wait()
```

Use `snapshot()` when another part of the program needs detached copies of the
current nodes and links.
