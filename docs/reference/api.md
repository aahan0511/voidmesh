# API reference

The supported top-level imports are `Canvas`, `Node`, and `Link`.

```python
from voidmesh import Canvas, Link, Node
```

## `Canvas`

### Constructor

```python
Canvas(
    *,
    title="Voidmesh",
    width=1000,
    height=700,
    background="#090b12",
    center_force=0.12,
    repel_force=4.0,
    link_force=0.35,
    link_distance=150.0,
    damping=0.9,
    layout="force",
    tree_horizontal_spacing=150.0,
    tree_vertical_spacing=110.0,
    grid=False,
    grid_color="#30384a",
    controls=True,
    ui_scale=None,
    node_font="sans",
    node_font_size=15.0,
    node_padding=(12.0, 7.0),
    node_roundness=9.0,
    link_width=1.5,
    fps=60,
)
```

`width` and `height` must be at least 200. `layout` is either `"force"` or
`"tree"`. The legacy `gravity` and `repulsion` constructor names are accepted
for compatibility, but new code should use `center_force` and `repel_force`.

### Graph methods

| Method | Result |
| --- | --- |
| `add_node(value="", **style)` | Adds and returns a `Node` |
| `update_node(node, **changes)` | Updates and returns a `Node` |
| `delete_node(node)` / `remove_node(node)` | Removes a node and attached links |
| `link(source, target, **style)` | Adds and returns a `Link` |
| `update_link(link, **changes)` | Updates and returns a `Link` |
| `unlink(link)` / `delete_link(link)` | Removes a link |
| `unlink(source, target)` | Removes the first link between two nodes |
| `relink(link, source=..., target=...)` | Replaces either endpoint |
| `clear()` | Removes all nodes and links |
| `snapshot()` | Returns detached `(nodes, links)` tuples |

Node/link arguments accept their object or string ID.

### View and configuration methods

| Method | Purpose |
| --- | --- |
| `configure_physics(...)` | Changes live force parameters |
| `configure_style(...)` | Changes font, node geometry, and link width |
| `set_layout("force" | "tree")` | Changes view |
| `toggle_grid(visible=None)` | Sets or toggles the grid and returns its state |

### Window methods

| Method/property | Purpose |
| --- | --- |
| `show(block=True)` / `run(block=True)` | Opens the window |
| `wait()` | Waits for a non-blocking window to close |
| `close()` | Requests window shutdown |
| `is_open` | Whether the renderer is currently active |

## `Node`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `str` | Unique identifier |
| `value` | `object` | Value converted to display text |
| `color` | `str \| tuple` | Tile color |
| `x`, `y` | `float` | World coordinates |
| `position` | `tuple[float, float]` | Read-only coordinate pair |
| `radius` | `float` | Minimum half-size for the tile |
| `fixed` | `bool` | Whether force movement is disabled |
| `font` | `str \| None` | Per-node font override |
| `font_size` | `float \| None` | Per-node size override |

`vx` and `vy` are simulation state and should normally be left to the engine.

## `Link`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `str` | Unique identifier |
| `source`, `target` | `str` | Endpoint node IDs |
| `color` | `str \| tuple` | Line color |
| `width` | `float` | Rendered thickness |
| `length` | `float` | Per-link preferred spring length |
| `elasticity` | `float` | Per-link spring response |
