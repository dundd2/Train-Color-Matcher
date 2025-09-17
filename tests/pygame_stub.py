"""Lightweight pygame stub to support unit tests without native dependencies."""
from __future__ import annotations

import sys
import types
from typing import Any


def _noop(*_args: Any, **_kwargs: Any) -> None:
    """Default no-op callable used for stubbed pygame functions."""
    return None


def setup_pygame_stub() -> None:
    """Install a minimal pygame stub when pygame is unavailable.

    The real pygame module is imported when available. Otherwise this function
    registers a lightweight stub that provides just enough functionality for
    the unit tests and the game's import-time setup.
    """

    try:
        import pygame  # type: ignore  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    pygame = types.ModuleType("pygame")
    pygame.error = Exception

    class _DummySurface:
        def __init__(self, size: tuple[int, int] = (0, 0), *_args: Any, **_kwargs: Any) -> None:
            self._size = size

        def fill(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def blit(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def get_width(self) -> int:
            return self._size[0]

        def get_height(self) -> int:
            return self._size[1]

        def set_alpha(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def copy(self) -> "_DummySurface":
            return _DummySurface(self._size)

    class _DummyFont:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def size(self, text: str) -> tuple[int, int]:
            return (len(text) * 8, 16)

        def render(self, text: str, *_args: Any, **_kwargs: Any) -> _DummySurface:
            return _DummySurface((len(text) * 8, 16))

    def _clock_factory() -> types.SimpleNamespace:
        return types.SimpleNamespace(tick=lambda *_args: 16)

    pygame.mixer = types.SimpleNamespace(pre_init=_noop)
    pygame.init = _noop
    pygame.quit = _noop
    pygame.font = types.SimpleNamespace(init=_noop, Font=_DummyFont)
    pygame.time = types.SimpleNamespace(get_ticks=lambda: 0, Clock=_clock_factory)
    pygame.transform = types.SimpleNamespace(scale=lambda surf, size: _DummySurface(size))
    pygame.event = types.SimpleNamespace(get=lambda: [])

    class _DisplayModule:
        def set_mode(self, size: tuple[int, int]) -> _DummySurface:
            return _DummySurface(size)

        def set_caption(self, *_args: Any, **_kwargs: Any) -> None:
            return None

    pygame.display = _DisplayModule()
    pygame.SRCALPHA = 0
    pygame.Surface = _DummySurface

    class _Rect:
        def __init__(self, x: int, y: int, width: int, height: int) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height

    pygame.Rect = _Rect

    sys.modules["pygame"] = pygame

