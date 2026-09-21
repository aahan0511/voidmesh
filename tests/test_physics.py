from voidmesh.models import Link, Node
from voidmesh.physics import Physics


def test_spring_pulls_distant_nodes_together() -> None:
    left = Node("left", x=-100)
    right = Node("right", x=100)
    nodes = {node.id: node for node in (left, right)}
    link = Link("edge", "left", "right", length=50, elasticity=0.1)
    Physics(gravity=0, repulsion=0).step(nodes, [link], 1 / 60)
    assert left.x > -100
    assert right.x < 100


def test_fixed_node_does_not_move() -> None:
    fixed = Node("fixed", x=100, fixed=True, vx=50)
    Physics().step({"fixed": fixed}, [], 1 / 60)
    assert fixed.position == (100, 0)
    assert fixed.vx == 0
