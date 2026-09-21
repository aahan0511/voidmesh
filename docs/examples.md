# Examples

## Bundled demo

```console
uv run voidmesh-demo
```

Displays a small force graph using the default controls.

## Live changes

```console
uv run python examples/live_changes.py
```

Opens a non-blocking window, adds nodes over time, and changes the root value
and color while the renderer is active.

## Systematic tree

```console
uv run python examples/tree_view.py
```

Displays a project structure in deterministic tree view with custom font and
link styling.

## Context manager

For short-lived tasks, a canvas can manage its own non-blocking window:

```python
import time
from voidmesh import Canvas

with Canvas() as canvas:
    first = canvas.add_node("First")
    second = canvas.add_node("Second")
    canvas.link(first, second)
    time.sleep(3)
```

Leaving the block closes the window.
