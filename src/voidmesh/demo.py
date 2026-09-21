"""The bundled ``voidmesh-demo`` example."""

from .canvas import Canvas


def main() -> None:
    canvas = Canvas(title="Voidmesh — live graph")
    center = canvas.add_node("Voidmesh", color="#f8fafc", radius=14, fixed=True)
    ideas = [
        ("Nodes", "#a78bfa"),
        ("Links", "#38bdf8"),
        ("Physics", "#34d399"),
        ("Live", "#fb7185"),
        ("Python", "#fbbf24"),
    ]
    for label, color in ideas:
        node = canvas.add_node(label, color=color)
        canvas.link(center, node, color=color, length=145)
    canvas.show()


if __name__ == "__main__":
    main()
