"""Run with: uv run python examples/tree_view.py"""

from voidmesh import Canvas

canvas = Canvas(
    title="Voidmesh tree view",
    layout="tree",
    grid=True,
    node_font="dejavusans",
    node_font_size=16,
    link_width=2.0,
)

root = canvas.add_node("Project", color="#f8fafc")
src = canvas.add_node("src", color="#a78bfa")
tests = canvas.add_node("tests", color="#38bdf8")
docs = canvas.add_node("docs", color="#34d399")
canvas.link(root, src)
canvas.link(root, tests)
canvas.link(root, docs)

for name in ("canvas.py", "renderer.py", "layout.py"):
    canvas.link(src, canvas.add_node(name, color="#c4b5fd"))
for name in ("test_canvas.py", "test_layout.py"):
    canvas.link(tests, canvas.add_node(name, color="#7dd3fc"))

canvas.show()
