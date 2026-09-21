from voidmesh.layout import TreeLayout
from voidmesh.models import Link, Node


def test_tree_layout_places_children_below_parent() -> None:
    nodes = {name: Node(name, value=name) for name in ("root", "left", "right", "leaf")}
    links = [
        Link("a", "root", "left"),
        Link("b", "root", "right"),
        Link("c", "left", "leaf"),
    ]
    TreeLayout().apply(nodes, links)

    assert nodes["root"].y < nodes["left"].y < nodes["leaf"].y
    assert nodes["root"].y < nodes["right"].y
    assert nodes["left"].x != nodes["right"].x


def test_tree_layout_handles_cycles_without_physics() -> None:
    nodes = {name: Node(name) for name in ("a", "b")}
    links = [Link("ab", "a", "b"), Link("ba", "b", "a")]
    TreeLayout().apply(nodes, links)
    assert all(node.vx == node.vy == 0 for node in nodes.values())
