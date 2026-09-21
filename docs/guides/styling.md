# Styling

## Canvas-wide style

```python
canvas = Canvas(
    background="#080a10",
    grid=True,
    grid_color="#30384a",
    node_font="DejaVu Sans",
    node_font_size=17,
    node_padding=(16, 9),
    node_roundness=12,
    link_width=2.5,
    ui_scale=1.25,
)
```

Font names are system font family names resolved by pygame. If a requested font
is unavailable, pygame selects a fallback.

Change style while the window is running:

```python
canvas.configure_style(
    node_font="monospace",
    node_font_size=18,
    node_padding=(18, 10),
    node_roundness=6,
    link_width=3,
)
```

Changing `link_width` through `configure_style()` updates existing links and
becomes the default for new links.

## Per-node style

```python
title = canvas.add_node(
    "Important",
    color="#fbbf24",
    font="serif",
    font_size=22,
)
canvas.update_node(title, color="#fb7185", font_size=20)
```

Node text color automatically switches between light and dark for contrast.

## Per-link style

```python
edge = canvas.link(a, b, color="#8b5cf6", width=4)
canvas.update_link(edge, color="#22d3ee", width=2)
```

Colors may be CSS-style names, hexadecimal strings, or `(red, green, blue)`
tuples.

## UI and graph scaling

Graph zoom changes nodes, labels, links, and the grid. UI scaling controls the
panel and helper text independently. By default the UI follows window size;
set `ui_scale` to a positive number for an explicit HiDPI scale.

All text is rendered again at its target size instead of bitmap-stretched, so
it remains crisp while zooming or resizing.
