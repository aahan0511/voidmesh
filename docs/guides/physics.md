# Force physics

Force view combines four effects. The controls are intentionally broad enough
to produce visibly different behavior.

| Setting | Effect | Typical direction |
| --- | --- | --- |
| `center_force` | Pulls every free node toward the canvas origin | Higher makes a tighter cluster |
| `repel_force` | Pushes every pair of nodes apart | Higher spreads dense graphs |
| `link_force` | Multiplies the spring force of every link | Higher makes links react faster |
| `link_distance` | Scales every link's preferred length | Higher creates more space |
| `damping` | Retains velocity between frames | Lower settles sooner; higher feels lively |

Configure these values when creating the canvas:

```python
canvas = Canvas(
    center_force=0.08,
    repel_force=7,
    link_force=0.55,
    link_distance=190,
    damping=0.92,
)
```

Or update a running simulation:

```python
canvas.configure_physics(
    center_force=0.2,
    repel_force=12,
    link_force=1.2,
    link_distance=240,
    damping=0.86,
)
```

The movable **Controls** panel changes the first four values directly. Its
sliders range from nearly disabled to deliberately strong.

## Per-link behavior

`Canvas.link()` also accepts `length` and `elasticity`. Global link distance
scales each link's individual length, and global link force multiplies each
link's elasticity.

```python
soft = canvas.link(a, b, length=100, elasticity=0.015)
firm = canvas.link(b, c, length=200, elasticity=0.08)
```

## Fixed nodes

A fixed node does not receive gravity, repulsion, or spring motion:

```python
anchor = canvas.add_node("Anchor", fixed=True)
canvas.update_node(anchor, fixed=False)  # Release it later.
```

If a node seems not to obey the controls, check its `fixed` property first.
