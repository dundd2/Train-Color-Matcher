import os
import sys
from pathlib import Path
import unittest

# Ensure pygame can initialize in headless test environments.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

for path in (TESTS_DIR, PROJECT_ROOT):
    string_path = str(path)
    if string_path not in sys.path:
        sys.path.insert(0, string_path)

from pygame_stub import setup_pygame_stub

setup_pygame_stub()

import pygame  # type: ignore  # noqa: E402
import train_color_matcher  # noqa: E402


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

        valid_config = {"window": {"width": 1024, "height": 768, "title": "My Game"}}
        valid_result = train_color_matcher.ConfigValidator.validate_window(valid_config)
        self.assertEqual(valid_result["width"], 1024)
        self.assertEqual(valid_result["height"], 768)
        self.assertEqual(valid_result["title"], "My Game")

    def test_validate_colors_falls_back_to_defaults(self):
        defaults = train_color_matcher.ConfigValidator.validate_colors({})
        result = train_color_matcher.ConfigValidator.validate_colors(
            {"colors": {"red": [-10, 0, 0], "green": "invalid"}}
        )
        self.assertEqual(result["red"], defaults["red"])
        self.assertEqual(result["green"], defaults["green"])

        valid_colors = {"colors": {"red": [1, 2, 3], "yellow": [10, 20, 30]}}
        valid_result = train_color_matcher.ConfigValidator.validate_colors(valid_colors)
        self.assertEqual(valid_result["red"], [1, 2, 3])
        self.assertEqual(valid_result["yellow"], [10, 20, 30])


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
        self.assertEqual(lines, ["red blue", "green", "yellow"])


if __name__ == "__main__":
    unittest.main()
