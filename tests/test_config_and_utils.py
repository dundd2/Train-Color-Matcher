import os
import sys
import types
import importlib.util
from pathlib import Path
import unittest

# Ensure pygame can initialize in headless test environments and provide a stub when unavailable.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed in CI where pygame is unavailable
    pygame = types.ModuleType("pygame")
    pygame.error = Exception

    class _DummySurface:
        def __init__(self, size=(0, 0), *_args, **_kwargs):
            self._size = size

        def fill(self, *_args, **_kwargs):
            return None

        def blit(self, *_args, **_kwargs):
            return None

        def get_width(self):
            return self._size[0]

        def get_height(self):
            return self._size[1]

        def set_alpha(self, *_args, **_kwargs):
            return None

        def copy(self):
            return _DummySurface(self._size)

    class _DummyFont:
        def __init__(self, *_args, **_kwargs):
            pass

        def size(self, text):
            return (len(text) * 8, 16)

        def render(self, text, *_args, **_kwargs):
            return _DummySurface((len(text) * 8, 16))

    def _noop(*_args, **_kwargs):
        return None

    pygame.mixer = types.SimpleNamespace(pre_init=_noop)
    pygame.init = _noop
    pygame.quit = _noop
    pygame.font = types.SimpleNamespace(init=_noop, Font=_DummyFont)
    pygame.time = types.SimpleNamespace(get_ticks=lambda: 0, Clock=lambda: types.SimpleNamespace(tick=lambda *_args: 16))
    pygame.transform = types.SimpleNamespace(scale=lambda surf, size: _DummySurface(size))
    pygame.event = types.SimpleNamespace(get=lambda: [])

    class _DisplayModule:
        def set_mode(self, size):
            return _DummySurface(size)

        def set_caption(self, *_args, **_kwargs):
            return None

    pygame.display = _DisplayModule()
    pygame.SRCALPHA = 0
    pygame.Surface = _DummySurface

    class _Rect:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

    pygame.Rect = _Rect

    sys.modules["pygame"] = pygame

MODULE_PATH = Path(__file__).resolve().parents[1] / "Train-Color-Matcher.py"
SPEC = importlib.util.spec_from_file_location("train_color_matcher", MODULE_PATH)
train_color_matcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(train_color_matcher)

# Import (or stub) pygame after loading the module to access font helpers in the tests themselves.
import pygame  # type: ignore  # noqa: E402


class ConfigValidatorTests(unittest.TestCase):
    """Unit tests for the configuration validation helpers."""

    def test_validate_color_accepts_rgb_triplets(self):
        self.assertTrue(train_color_matcher.ConfigValidator.validate_color([10, 20, 30]))
        self.assertFalse(train_color_matcher.ConfigValidator.validate_color([10, 20]))
        self.assertFalse(train_color_matcher.ConfigValidator.validate_color([10, 20, 300]))

    def test_validate_window_enforces_minimums(self):
        defaults = train_color_matcher.ConfigValidator.validate_window({})
        result = train_color_matcher.ConfigValidator.validate_window(
            {"window": {"width": 200, "height": 100, "title": 123}}
        )
        self.assertEqual(result["width"], defaults["width"])
        self.assertEqual(result["height"], defaults["height"])
        self.assertEqual(result["title"], defaults["title"])

    def test_validate_colors_falls_back_to_defaults(self):
        defaults = train_color_matcher.ConfigValidator.validate_colors({})
        result = train_color_matcher.ConfigValidator.validate_colors(
            {"colors": {"red": [-10, 0, 0], "green": "invalid"}}
        )
        self.assertEqual(result["red"], defaults["red"])
        self.assertEqual(result["green"], defaults["green"])


class WrapTextTests(unittest.TestCase):
    """Tests for the text wrapping helper used across UI panels."""

    @classmethod
    def setUpClass(cls):
        if hasattr(pygame.font, "init"):
            pygame.font.init()
        cls.font = pygame.font.Font(None, 24)

    def test_wrap_text_respects_width_constraints(self):
        message = "red blue green yellow"
        max_width = self.font.size("red blue")[0] + 4
        lines = train_color_matcher.wrap_text(message, self.font, max_width)
        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(self.font.size(line)[0], max_width)


if __name__ == "__main__":
    unittest.main()
