"""Pygame renderer and interaction layer."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .canvas import Canvas
    from .models import Color, Node


@dataclass(frozen=True, slots=True)
class SliderSpec:
    label: str
    attribute: str
    minimum: float
    maximum: float
    decimals: int


SLIDERS = (
    SliderSpec("Center force", "center_force", 0.0, 1.0, 2),
    SliderSpec("Repel force", "repel_force", 0.0, 20.0, 2),
    SliderSpec("Link force", "link_force", 0.0, 2.0, 2),
    SliderSpec("Link distance", "link_distance", 30.0, 400.0, 0),
)


class ControlPanel:
    """Small immediate-mode controls for the live simulation."""

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.collapsed = False
        self.active_slider: int | None = None
        self.dragging = False
        self.position = pygame.Vector2(14, 14)
        self.drag_offset = pygame.Vector2()
        self._font_key = 0
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None

    def bounds(self, screen: pygame.Surface) -> pygame.Rect:
        scale = self.scale(screen)
        width = round(280 * scale)
        height = round((44 if self.collapsed else 398) * scale)
        x = max(0, min(round(self.position.x), screen.get_width() - width))
        y = max(0, min(round(self.position.y), screen.get_height() - height))
        self.position.update(x, y)
        return pygame.Rect(x, y, width, height)

    def scale(self, screen: pygame.Surface) -> float:
        if self.canvas.ui_scale is not None:
            requested = self.canvas.ui_scale
        else:
            requested = min(
                screen.get_width() / self.canvas.width,
                screen.get_height() / self.canvas.height,
            )
            requested = max(0.75, min(2.0, requested))
        return min(requested, (screen.get_width() - 12) / 280)

    def contains(self, point: tuple[int, int], screen: pygame.Surface) -> bool:
        return self.bounds(screen).collidepoint(point)

    def handle(self, event: pygame.event.Event, screen: pygame.Surface) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.contains(event.pos, screen):
                return False
            if self._chevron_rect(screen).collidepoint(event.pos):
                self.collapsed = not self.collapsed
                self.active_slider = None
                return True
            if self._header_rect(screen).collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = pygame.Vector2(event.pos) - self.position
                return True
            if self.collapsed:
                return True
            for index in range(len(SLIDERS)):
                if self._slider_hit_rect(index, screen).collidepoint(event.pos):
                    self.active_slider = index
                    self._set_slider(index, event.pos[0], screen)
                    return True
            if self._force_view_rect(screen).collidepoint(event.pos):
                self.canvas.set_layout("force")
                return True
            if self._tree_view_rect(screen).collidepoint(event.pos):
                self.canvas.set_layout("tree")
                return True
            if self._grid_rect(screen).collidepoint(event.pos):
                self.canvas.toggle_grid()
            return True

        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                bounds = self.bounds(screen)
                requested = pygame.Vector2(event.pos) - self.drag_offset
                requested.x = max(0, min(requested.x, screen.get_width() - bounds.width))
                requested.y = max(0, min(requested.y, screen.get_height() - bounds.height))
                self.position = requested
                return True
            if self.active_slider is not None:
                self._set_slider(self.active_slider, event.pos[0], screen)
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_active = self.active_slider is not None or self.dragging
            self.active_slider = None
            self.dragging = False
            return was_active or self.contains(event.pos, screen)
        if event.type == pygame.MOUSEWHEEL:
            return self.contains(pygame.mouse.get_pos(), screen)
        return False

    def draw(self, screen: pygame.Surface) -> None:
        bounds = self.bounds(screen)
        scale = self.scale(screen)
        font, small_font = self._fonts(scale)
        surface = pygame.Surface(bounds.size, pygame.SRCALPHA)
        radius = round(8 * scale)
        pygame.draw.rect(surface, (24, 27, 36, 238), surface.get_rect(), border_radius=radius)
        pygame.draw.rect(
            surface, (62, 68, 82, 190), surface.get_rect(), 1, border_radius=radius
        )
        icon_center = pygame.Vector2(round(19 * scale), round(21 * scale))
        icon_size = max(3, round(5 * scale))
        if self.collapsed:
            points = [
                (icon_center.x - icon_size / 2, icon_center.y - icon_size),
                (icon_center.x + icon_size / 2, icon_center.y),
                (icon_center.x - icon_size / 2, icon_center.y + icon_size),
            ]
        else:
            points = [
                (icon_center.x - icon_size, icon_center.y - icon_size / 2),
                (icon_center.x, icon_center.y + icon_size / 2),
                (icon_center.x + icon_size, icon_center.y - icon_size / 2),
            ]
        pygame.draw.lines(surface, (148, 163, 184), False, points, max(1, round(2 * scale)))
        title = font.render("Controls", True, (226, 232, 240))
        surface.blit(title, (round(34 * scale), round(11 * scale)))

        if not self.collapsed:
            for index, spec in enumerate(SLIDERS):
                top = round((51 + index * 65) * scale)
                value = float(getattr(self.canvas.physics, spec.attribute))
                label = font.render(spec.label, True, (203, 213, 225))
                shown = f"{value:.{spec.decimals}f}"
                value_label = small_font.render(shown, True, (148, 163, 184))
                surface.blit(label, (round(13 * scale), top))
                surface.blit(value_label, (round(13 * scale), top + round(30 * scale)))

                track_left = round(61 * scale)
                track_right = round(262 * scale)
                track_y = top + round(36 * scale)
                ratio = (value - spec.minimum) / (spec.maximum - spec.minimum)
                knob_x = round(track_left + ratio * (track_right - track_left))
                pygame.draw.line(
                    surface,
                    (64, 68, 78),
                    (track_left, track_y),
                    (track_right, track_y),
                    max(2, round(5 * scale)),
                )
                pygame.draw.line(
                    surface,
                    (139, 92, 246),
                    (track_left, track_y),
                    (knob_x, track_y),
                    max(2, round(5 * scale)),
                )
                pygame.draw.circle(
                    surface, (248, 250, 252), (knob_x, track_y), round(10 * scale)
                )
                pygame.draw.circle(
                    surface,
                    (203, 213, 225),
                    (knob_x, track_y),
                    round(10 * scale),
                    max(1, round(scale)),
                )

            view_y = round(318 * scale)
            label = font.render("View", True, (203, 213, 225))
            surface.blit(label, (round(13 * scale), view_y + round(4 * scale)))
            force_button = pygame.Rect(
                round(105 * scale), view_y, round(74 * scale), round(27 * scale)
            )
            tree_button = pygame.Rect(
                round(182 * scale), view_y, round(82 * scale), round(27 * scale)
            )
            self._draw_view_button(surface, font, force_button, "Force", "force")
            self._draw_view_button(surface, font, tree_button, "Tree", "tree")

            grid_y = round(362 * scale)
            label = font.render("Background grid", True, (203, 213, 225))
            surface.blit(label, (round(13 * scale), grid_y))
            toggle = pygame.Rect(
                round(227 * scale),
                grid_y - round(scale),
                round(37 * scale),
                round(21 * scale),
            )
            toggle_color = (139, 92, 246) if self.canvas.grid else (64, 68, 78)
            pygame.draw.rect(surface, toggle_color, toggle, border_radius=round(11 * scale))
            offset = round(10 * scale)
            knob_x = toggle.right - offset if self.canvas.grid else toggle.left + offset
            pygame.draw.circle(
                surface, (248, 250, 252), (knob_x, toggle.centery), round(8 * scale)
            )

        screen.blit(surface, bounds.topleft)

    def _draw_view_button(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        rect: pygame.Rect,
        label: str,
        layout: str,
    ) -> None:
        selected = self.canvas.layout == layout
        color = (139, 92, 246) if selected else (48, 53, 65)
        pygame.draw.rect(surface, color, rect, border_radius=max(3, rect.height // 4))
        text_color = (248, 250, 252) if selected else (148, 163, 184)
        text = font.render(label, True, text_color)
        surface.blit(text, text.get_rect(center=rect.center))

    def _fonts(self, scale: float) -> tuple[pygame.font.Font, pygame.font.Font]:
        key = round(scale * 100)
        if self._font is None or self._small_font is None or key != self._font_key:
            self._font_key = key
            self._font = pygame.font.SysFont("sans", max(10, round(15 * scale)))
            self._small_font = pygame.font.SysFont("sans", max(8, round(12 * scale)))
        return self._font, self._small_font

    def _set_slider(self, index: int, mouse_x: int, screen: pygame.Surface) -> None:
        spec = SLIDERS[index]
        track = self._slider_track(index, screen)
        ratio = max(0.0, min(1.0, (mouse_x - track.left) / track.width))
        value = spec.minimum + ratio * (spec.maximum - spec.minimum)
        setattr(self.canvas.physics, spec.attribute, value)

    def _header_rect(self, screen: pygame.Surface) -> pygame.Rect:
        bounds = self.bounds(screen)
        return pygame.Rect(bounds.x, bounds.y, bounds.width, round(42 * self.scale(screen)))

    def _chevron_rect(self, screen: pygame.Surface) -> pygame.Rect:
        header = self._header_rect(screen)
        return pygame.Rect(header.x, header.y, round(38 * self.scale(screen)), header.height)

    def _slider_track(self, index: int, screen: pygame.Surface) -> pygame.Rect:
        bounds = self.bounds(screen)
        scale = self.scale(screen)
        return pygame.Rect(
            bounds.x + round(61 * scale),
            bounds.y + round((87 + index * 65) * scale),
            round(201 * scale),
            1,
        )

    def _slider_hit_rect(self, index: int, screen: pygame.Surface) -> pygame.Rect:
        scale = self.scale(screen)
        return self._slider_track(index, screen).inflate(round(16 * scale), round(26 * scale))

    def _grid_rect(self, screen: pygame.Surface) -> pygame.Rect:
        bounds = self.bounds(screen)
        scale = self.scale(screen)
        return pygame.Rect(
            bounds.x, bounds.y + round(353 * scale), bounds.width, round(39 * scale)
        )

    def _force_view_rect(self, screen: pygame.Surface) -> pygame.Rect:
        bounds = self.bounds(screen)
        scale = self.scale(screen)
        return pygame.Rect(
            bounds.x + round(105 * scale),
            bounds.y + round(318 * scale),
            round(74 * scale),
            round(27 * scale),
        )

    def _tree_view_rect(self, screen: pygame.Surface) -> pygame.Rect:
        bounds = self.bounds(screen)
        scale = self.scale(screen)
        return pygame.Rect(
            bounds.x + round(182 * scale),
            bounds.y + round(318 * scale),
            round(82 * scale),
            round(27 * scale),
        )


class Renderer:
    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.running = False
        self.zoom = 1.0
        self.pan = pygame.Vector2()
        self.dragged: Node | None = None
        self.drag_was_fixed = False
        self.panning = False
        self.panel = ControlPanel(canvas)
        self._font_cache: dict[tuple[str, int], pygame.font.Font] = {}

    def run(self) -> None:
        # Initializing all pygame modules also opens audio, which this visual-only
        # library does not need and which can fail on otherwise valid desktops.
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption(self.canvas.title)
        screen = pygame.display.set_mode(
            (self.canvas.width, self.canvas.height), pygame.RESIZABLE
        )
        clock = pygame.time.Clock()
        self.running = True
        self.canvas._ready.set()
        try:
            while self.running:
                dt = clock.tick(self.canvas.fps) / 1000.0
                self._events(screen)
                if not self.running:
                    break
                with self.canvas._locked_graph() as (nodes, links):
                    if self.canvas.layout == "force":
                        self.canvas.physics.step(nodes, links.values(), dt)
                    else:
                        self.canvas.tree_layout.apply(nodes, links.values())
                    self._draw(screen, nodes, links)
                pygame.display.flip()
        finally:
            self.running = False
            pygame.display.quit()
            pygame.font.quit()

    def stop(self) -> None:
        self.running = False

    def _events(self, screen: pygame.Surface) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                self.canvas.toggle_grid()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.canvas.controls = not self.canvas.controls
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                next_layout = "tree" if self.canvas.layout == "force" else "force"
                self.canvas.set_layout(next_layout)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.canvas.export_png()
            elif self.canvas.controls and self.panel.handle(event, screen):
                continue
            elif event.type == pygame.MOUSEWHEEL:
                self._zoom_at(event.y, pygame.mouse.get_pos(), screen)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._start_drag(event.pos, screen)
                elif event.button in (2, 3):
                    self.panning = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragged is not None:
                    self.dragged.fixed = self.drag_was_fixed
                    self.dragged = None
                elif event.button in (2, 3):
                    self.panning = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragged is not None:
                    point = self._from_screen(event.pos, screen)
                    self.dragged.x, self.dragged.y = point.x, point.y
                    self.dragged.vx = self.dragged.vy = 0.0
                elif self.panning:
                    self.pan += pygame.Vector2(event.rel)

    def _zoom_at(
        self, amount: int, point: tuple[int, int], screen: pygame.Surface
    ) -> None:
        before = self._from_screen(point, screen)
        # Do not impose a view limit: large graphs need both deep zoom-out and
        # close inspection. ``min`` only avoids an eventual zero from
        # floating-point underflow, which would make coordinate conversion undefined.
        self.zoom = max(sys.float_info.min, self.zoom * (1.12**amount))
        after = self._from_screen(point, screen)
        self.pan += (after - before) * self.zoom

    def _start_drag(self, point: tuple[int, int], screen: pygame.Surface) -> None:
        with self.canvas._locked_graph() as (nodes, _):
            for node in reversed(tuple(nodes.values())):
                if (
                    self._node_rect(node, screen, self._font_for_node(node))
                    .inflate(10, 10)
                    .collidepoint(point)
                ):
                    self.dragged = node
                    self.drag_was_fixed = node.fixed
                    node.fixed = True
                    return

    def export_png(self, path: Path, *, width: int, height: int) -> None:
        """Render the current graph camera to an image without window chrome."""
        surface = pygame.Surface((width, height))
        scale = min(width / self.canvas.width, height / self.canvas.height)
        previous_zoom = self.zoom
        previous_pan = self.pan.copy()
        try:
            self.zoom *= scale
            self.pan *= scale
            with self.canvas._locked_graph() as (nodes, links):
                self._draw(surface, nodes, links, include_interface=False)
            pygame.image.save(surface, str(path))
        finally:
            self.zoom = previous_zoom
            self.pan = previous_pan

    def _draw(self, screen, nodes, links, *, include_interface: bool = True) -> None:
        screen.fill(_color(self.canvas.background))
        if self.canvas.grid:
            self._draw_grid(screen)
        for link in links.values():
            source = nodes.get(link.source)
            target = nodes.get(link.target)
            if source is None or target is None:
                continue
            source_center = self._to_screen(source.position, screen)
            target_center = self._to_screen(target.position, screen)
            source_rect = self._node_rect(source, screen, self._font_for_node(source))
            target_rect = self._node_rect(target, screen, self._font_for_node(target))
            start = self._edge_point(source_rect, target_center)
            end = self._edge_point(target_rect, source_center)
            pygame.draw.aaline(screen, _color(link.color), start, end)
            if link.width * self.zoom >= 2:
                pygame.draw.line(
                    screen,
                    _color(link.color),
                    start,
                    end,
                    max(1, round(link.width * self.zoom)),
                )

        mouse = pygame.mouse.get_pos()
        hovered = None
        for node in nodes.values():
            node_font = self._font_for_node(node)
            rect = self._node_rect(node, screen, node_font)
            corner = max(0, round(self.canvas.node_roundness * self.zoom))
            if rect.inflate(8, 8).collidepoint(mouse):
                hovered = node
                pygame.draw.rect(
                    screen, _color(node.color), rect.inflate(8, 8), 1, border_radius=corner + 3
                )
            shadow = rect.move(round(2 * self.zoom), round(3 * self.zoom))
            pygame.draw.rect(screen, (3, 4, 8), shadow, border_radius=corner)
            fill = _color(node.color)
            pygame.draw.rect(screen, fill, rect, border_radius=corner)
            pygame.draw.rect(screen, fill.lerp(pygame.Color("white"), 0.22), rect, 1, corner)
            if self.zoom >= 0.38:
                label = node_font.render(str(node.value), True, _text_color(fill))
                screen.blit(label, label.get_rect(center=rect.center))

        if not include_interface:
            return

        ui_scale = self.panel.scale(screen)
        helper_font = self._font("sans", max(8, round(12 * ui_scale)))
        margin = round(16 * ui_scale)
        hint = "drag nodes  •  wheel zoom  •  right-drag pan  •  E export  •  G grid  •  T view"
        hint_surface = helper_font.render(hint, True, (100, 116, 139))
        screen.blit(
            hint_surface, (margin, screen.get_height() - hint_surface.get_height() - margin)
        )
        if hovered is not None and hovered.value != hovered.id:
            id_surface = helper_font.render(hovered.id, True, (148, 163, 184))
            screen.blit(id_surface, (margin, margin))
        if self.canvas.controls:
            self.panel.draw(screen)

    def _font_for_node(self, node: Node) -> pygame.font.Font:
        family = node.font or self.canvas.node_font
        base_size = node.font_size or self.canvas.node_font_size
        return self._font(family, max(7, min(120, round(base_size * self.zoom))))

    def _font(self, family: str, size: int) -> pygame.font.Font:
        key = family, size
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont(family, size)
        return self._font_cache[key]

    def _node_rect(
        self, node: Node, screen: pygame.Surface, font: pygame.font.Font
    ) -> pygame.Rect:
        label_width, label_height = font.size(str(node.value))
        padding_x, padding_y = self.canvas.node_padding
        width = max(
            round(node.radius * 2 * self.zoom),
            label_width + round(padding_x * 2 * self.zoom),
        )
        height = max(
            round(node.radius * 2 * self.zoom),
            label_height + round(padding_y * 2 * self.zoom),
        )
        width = max(4, width)
        height = max(4, height)
        return pygame.Rect((0, 0), (width, height)).move(
            pygame.Vector2(self._to_screen(node.position, screen))
            - pygame.Vector2(width / 2, height / 2)
        )

    @staticmethod
    def _edge_point(rect: pygame.Rect, toward: tuple[int, int]) -> tuple[int, int]:
        center = pygame.Vector2(rect.center)
        direction = pygame.Vector2(toward) - center
        if direction.length_squared() == 0:
            return rect.center
        scale = 1.0 / max(
            abs(direction.x) / max(rect.width / 2, 1),
            abs(direction.y) / max(rect.height / 2, 1),
        )
        point = center + direction * scale
        return round(point.x), round(point.y)

    def _draw_grid(self, screen: pygame.Surface) -> None:
        spacing = 40.0 * self.zoom
        while spacing < 28:
            spacing *= 2
        while spacing > 80:
            spacing /= 2
        center_x = screen.get_width() / 2 + self.pan.x
        center_y = screen.get_height() / 2 + self.pan.y
        x = center_x % spacing
        y = center_y % spacing
        color = _color(self.canvas.grid_color)
        axis_color = color.lerp(pygame.Color("#94a3b8"), 0.32)
        while x < screen.get_width():
            pygame.draw.line(screen, color, (round(x), 0), (round(x), screen.get_height()))
            x += spacing
        while y < screen.get_height():
            pygame.draw.line(screen, color, (0, round(y)), (screen.get_width(), round(y)))
            y += spacing
        pygame.draw.line(
            screen,
            axis_color,
            (round(center_x), 0),
            (round(center_x), screen.get_height()),
        )
        pygame.draw.line(
            screen,
            axis_color,
            (0, round(center_y)),
            (screen.get_width(), round(center_y)),
        )

    def _to_screen(self, point, screen: pygame.Surface) -> tuple[int, int]:
        center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        result = pygame.Vector2(point) * self.zoom + center + self.pan
        return round(result.x), round(result.y)

    def _from_screen(self, point, screen: pygame.Surface) -> pygame.Vector2:
        center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        return (pygame.Vector2(point) - center - self.pan) / self.zoom


def _color(value: Color) -> pygame.Color:
    try:
        return pygame.Color(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"invalid color {value!r}") from error


def _text_color(background: pygame.Color) -> pygame.Color:
    luminance = 0.2126 * background.r + 0.7152 * background.g + 0.0722 * background.b
    return pygame.Color("#111827" if luminance > 155 else "#f8fafc")
