"""Run with: uv run python examples/live_changes.py"""

import time

from voidmesh import Canvas

canvas = Canvas(title="Voidmesh live changes")
root = canvas.add_node("Start", color="#f8fafc")
canvas.show(block=False)

colors = ("#a78bfa", "#38bdf8", "#34d399", "#fb7185")
previous = root
for number, color in enumerate(colors, start=1):
    node = canvas.add_node(f"Node {number}", color=color)
    canvas.link(previous, node, color=color)
    previous = node
    time.sleep(0.7)

canvas.update_node(root, value="Updated!", color="#fbbf24")
canvas.wait()
