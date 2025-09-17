"""Lightweight pygame stub for unit tests."""
from __future__ import annotations

import sys
import types
from typing import Any, Iterable, Tuple


class _Rect:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @center.setter
    def center(self, value: Tuple[int, int]) -> None:
        cx, cy = value
        self.x = cx - self.width // 2
        self.y = cy - self.height // 2

    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        px, py = pos
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height


class _Surface:
    def __init__(self, size: Tuple[int, int], flags: int | None = None) -> None:
        self.width, self.height = size
        self.flags = flags
        self.alpha = 255

    def fill(self, color: Iterable[int]) -> None:
        pass

    def blit(self, source: Any, dest: Any) -> None:
        pass

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_rect(self, **kwargs: Any) -> _Rect:
        rect = _Rect(0, 0, self.width, self.height)
        if "center" in kwargs:
            rect.center = kwargs["center"]
        if "topleft" in kwargs:
            rect.x, rect.y = kwargs["topleft"]
        return rect

    def set_alpha(self, value: int) -> None:
        self.alpha = value

    def convert_alpha(self) -> "_Surface":
        return self


class _Font:
    def __init__(self, _file: Any, size: int) -> None:
        self._size = max(size, 1)

    def render(self, text: str, _antialias: bool, _color: Iterable[int]) -> _Surface:
        width = self._size * max(len(text), 1) // 2
        height = self._size
        return _Surface((width, height))

    def size(self, text: str) -> Tuple[int, int]:
        width = self._size * max(len(text), 1) // 2
        height = self._size
        return width, height


class _Sound:
    def __init__(self, _path: str) -> None:
        self.volume = 1.0

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self, _loops: int = 0) -> None:
        pass


class _Clock:
    def tick(self, _framerate: int) -> int:
        return 16


def install() -> types.ModuleType:
    """Install the pygame stub if the real dependency is unavailable."""
    if "pygame" in sys.modules:
        return sys.modules["pygame"]

    pygame = types.ModuleType("pygame")
    pygame.SRCALPHA = 1
    pygame.QUIT = 12
    pygame.MOUSEBUTTONDOWN = 5
    pygame.MOUSEMOTION = 6
    pygame.KEYDOWN = 2
    pygame.K_LEFT = 1073741904
    pygame.K_RIGHT = 1073741903
    pygame.K_SPACE = 32
    pygame.K_RETURN = 13
    pygame.error = type("error", (Exception,), {})

    pygame.Rect = _Rect
    pygame.Surface = _Surface

    pygame.init = lambda: None
    pygame.quit = lambda: None

    font_module = types.ModuleType("pygame.font")
    font_module.Font = _Font
    font_module.init = staticmethod(lambda: None)
    pygame.font = font_module

    display_module = types.ModuleType("pygame.display")
    display_module.set_mode = lambda size: _Surface(size)
    display_module.set_caption = lambda _title: None
    display_module.flip = lambda: None
    pygame.display = display_module

    mixer_module = types.ModuleType("pygame.mixer")
    mixer_module.Sound = _Sound
    mixer_module.pause = staticmethod(lambda: None)
    mixer_module.unpause = staticmethod(lambda: None)
    pygame.mixer = mixer_module

    draw_module = types.ModuleType("pygame.draw")
    draw_module.rect = staticmethod(lambda *args, **kwargs: None)
    draw_module.circle = staticmethod(lambda *args, **kwargs: None)
    draw_module.line = staticmethod(lambda *args, **kwargs: None)
    pygame.draw = draw_module

    time_module = types.ModuleType("pygame.time")
    time_module.get_ticks = staticmethod(lambda: 0)
    time_module.Clock = _Clock
    pygame.time = time_module

    transform_module = types.ModuleType("pygame.transform")
    transform_module.scale = staticmethod(lambda surface, size: _Surface(size))
    pygame.transform = transform_module

    event_module = types.ModuleType("pygame.event")
    event_module.get = staticmethod(lambda: [])
    pygame.event = event_module

    image_module = types.ModuleType("pygame.image")
    image_module.load = staticmethod(lambda _path: _Surface((100, 100)))
    pygame.image = image_module

    sys.modules["pygame"] = pygame
    sys.modules["pygame.font"] = font_module
    sys.modules["pygame.display"] = display_module
    sys.modules["pygame.mixer"] = mixer_module
    sys.modules["pygame.draw"] = draw_module
    sys.modules["pygame.time"] = time_module
    sys.modules["pygame.transform"] = transform_module
    sys.modules["pygame.event"] = event_module
    sys.modules["pygame.image"] = image_module

    return pygame


__all__ = ["install"]
