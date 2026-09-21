# Getting started

## Requirements

Voidmesh requires Python 3.14 and uses `pygame-ce` for its desktop renderer.
The project is managed entirely with `uv`.

## Install from PyPI

Once a release has been published:

```console
uv add voidmesh
```

To work from this repository:

```console
git clone <repository-url>
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
