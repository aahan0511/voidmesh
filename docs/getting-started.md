# Getting started

## Requirements

Voidmesh supports Python 3.12 and later and uses `pygame-ce` for its desktop
renderer.

## Install from PyPI

With `uv`:

```console
uv add voidmesh
```

Or with `pip`:

```console
python -m pip install voidmesh
```

To work from this repository:

```console
git clone https://github.com/aahan0511/voidmesh.git
cd voidmesh
uv sync
```

## Create a graph

```python
from voidmesh import Canvas

canvas = Canvas(title="First graph", width=1000, height=700)
hello = canvas.add_node("Hello", color="#a78bfa")
world = canvas.add_node("World", color="#38bdf8")
canvas.link(hello, world, color="#64748b")
canvas.show()
```

`show()` blocks until the window closes. Use non-blocking mode when code needs
to keep modifying the graph:

```python
canvas.show(block=False)
canvas.update_node(hello, value="Updated")
canvas.wait()
```

`wait()` keeps the script alive until the user closes the window.

## Mouse and keyboard controls

| Input | Action |
| --- | --- |
| Left-drag a node | Move the node |
| Right- or middle-drag | Pan the canvas |
| Mouse wheel | Zoom around the cursor |
| `G` | Toggle the grid |
| `F` | Hide or show the controls |
| `T` | Switch force/tree view |
| `Esc` | Close the window |

Drag the **Controls** panel by its heading. Click its chevron to collapse it.

## Run the bundled examples

```console
uv run voidmesh-demo
uv run python examples/live_changes.py
uv run python examples/tree_view.py
```
