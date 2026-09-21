from types import SimpleNamespace

import pytest

from voidmesh import Canvas
from voidmesh.renderer import Renderer


def test_graph_lifecycle() -> None:
    canvas = Canvas()
    alpha = canvas.add_node("alpha", node_id="a", color="#fff", position=(1, 2))
    beta = canvas.add_node("beta", node_id="b")
    link = canvas.link(alpha, beta, link_id="a-b", color="red")

    canvas.update_node(alpha, value="changed", color="blue", position=(3, 4))
    canvas.update_link(link, length=42, elasticity=0.1)

    assert alpha.value == "changed"
    assert alpha.position == (3, 4)
    assert link.length == 42
    assert canvas.unlink(alpha, beta) is link
    assert not canvas.links


def test_relink_and_cascade_delete() -> None:
    canvas = Canvas()
    one = canvas.add_node(node_id="one")
    two = canvas.add_node(node_id="two")
    three = canvas.add_node(node_id="three")
    link = canvas.link(one, two)

    canvas.relink(link, target=three)
    assert (link.source, link.target) == ("one", "three")
    canvas.delete_node(three)
    assert link.id not in canvas.links


def test_ids_and_input_are_validated() -> None:
    canvas = Canvas()
    canvas.add_node(node_id="same")
    with pytest.raises(ValueError, match="already exists"):
        canvas.add_node(node_id="same")
    with pytest.raises(KeyError, match="unknown node"):
        canvas.link("same", "missing")
    with pytest.raises(TypeError, match="unknown node properties"):
        canvas.update_node("same", mystery=True)


def test_snapshot_is_detached() -> None:
    canvas = Canvas()
    original = canvas.add_node("before")
    nodes, _ = canvas.snapshot()
    nodes[0].value = "after"
    assert original.value == "before"


def test_live_physics_and_grid_configuration() -> None:
    canvas = Canvas(grid=False)
    canvas.configure_physics(
        center_force=0.2,
        repel_force=7,
        link_force=0.4,
        link_distance=180,
        damping=0.91,
    )
    assert canvas.physics.center_force == 0.2
    assert canvas.physics.repel_force == 7
    assert canvas.physics.link_force == 0.4
    assert canvas.physics.link_distance == 180
    assert canvas.physics.damping == 0.91
    assert canvas.toggle_grid() is True
    assert canvas.toggle_grid(False) is False


def test_original_physics_names_remain_compatible() -> None:
    canvas = Canvas(gravity=0.0175, repulsion=1100)
    assert canvas.physics.center_force * 0.12 == pytest.approx(0.0175)
    assert canvas.physics.repel_force * 900 == pytest.approx(1100)


def test_ui_scale_must_be_positive() -> None:
    with pytest.raises(ValueError, match="ui_scale"):
        Canvas(ui_scale=0)


def test_tree_view_and_style_configuration() -> None:
    canvas = Canvas(layout="tree", link_width=2)
    root = canvas.add_node("root", font="serif", font_size=18)
    child = canvas.add_node("child")
    link = canvas.link(root, child)
    canvas.set_layout("tree")
    canvas.configure_style(
        node_font="monospace",
        node_font_size=17,
        node_padding=(16, 9),
        node_roundness=12,
        link_width=3,
    )
    assert child.y > root.y
    assert root.font == "serif"
    assert canvas.node_font == "monospace"
    assert link.width == 3


def test_zoom_has_no_artificial_bounds() -> None:
    canvas = Canvas(controls=False)
    renderer = Renderer(canvas)
    screen = __import__("pygame").Surface((800, 600))

    renderer.zoom = 10_000
    renderer._zoom_at(100, (400, 300), screen)
    assert renderer.zoom > 3.5
    renderer.zoom = 0.001
    renderer._zoom_at(-100, (400, 300), screen)
    assert renderer.zoom < 0.25


def test_window_close_stops_processing_events(monkeypatch: pytest.MonkeyPatch) -> None:
    pygame = __import__("pygame")
    canvas = Canvas(controls=False)
    renderer = Renderer(canvas)
    renderer.running = True
    screen = pygame.Surface((800, 600))
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [SimpleNamespace(type=pygame.QUIT), SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_g)],
    )

    renderer._events(screen)

    assert renderer.running is False
    assert canvas.grid is False
