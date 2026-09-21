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


def test_fixed_nodes_define_the_center_of_force_gravity() -> None:
    fixed_left = Node("left", x=-100, y=30, fixed=True)
    fixed_right = Node("right", x=300, y=90, fixed=True)
    free = Node("free", x=200, y=60)
    nodes = {node.id: node for node in (fixed_left, fixed_right, free)}

    Physics(center_force=1, repel_force=0, link_force=0).step(nodes, [], 1 / 60)

    # The fixed-node centroid is (100, 60), so gravity pulls the free node left.
    assert free.x < 200
    assert free.y == 60


def test_void_center_is_used_without_fixed_nodes() -> None:
    node = Node("free", x=100)

    Physics(center_force=1, repel_force=0, link_force=0).step({"free": node}, [], 1 / 60)

    assert node.x < 100
