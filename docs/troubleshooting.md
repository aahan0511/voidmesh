# Troubleshooting

## A node does not respond to physics

Check whether it was created with `fixed=True`. Release it with:

```python
canvas.update_node(node, fixed=False)
```

Tree view never runs physics. Select Force in the panel, press `T`, or call
`canvas.set_layout("force")`.

## The script exits and the window disappears

Non-blocking windows do not keep the main script alive on their own. End with
`canvas.wait()` or use blocking `canvas.show()`.

## A font is not used

Fonts are resolved from fonts installed on the operating system. Try a generic
family such as `sans`, `serif`, or `monospace`, or install the requested font.

## UI is too small or too large

Set an explicit scale:

```python
canvas = Canvas(ui_scale=1.5)
```

This changes the control panel and helper text, not graph zoom.

## The window reports an audio error

Voidmesh initializes only pygame's display and font modules and does not use
audio. Ensure the current package version is installed with `uv sync` if an
older checkout still initializes pygame globally.

## The tree has an unexpected parent

The first incoming link added for a node defines its tree parent. Remove and
re-add links in the intended source→target order. Cross-links remain visible
but do not duplicate nodes.

## Colors fail at render time

Use a pygame-compatible named color, a hexadecimal value such as `#8b5cf6`, or
an RGB tuple with integer channels from 0 through 255.
