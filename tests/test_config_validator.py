"""Tests for configuration validation and utility helpers."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

from tests.pygame_stub import install as install_pygame_stub


install_pygame_stub()

MODULE_PATH = Path(__file__).resolve().parents[1] / "Train-Color-Matcher.py"
SPEC = importlib.util.spec_from_file_location("train_color_matcher", MODULE_PATH)
train_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(train_module)

ConfigValidator = train_module.ConfigValidator
wrap_text = train_module.wrap_text
calculate_accuracy = train_module.calculate_accuracy
pygame = sys.modules["pygame"]


class ValidateColorTests(unittest.TestCase):
    def test_invalid_color_types(self) -> None:
        self.assertFalse(ConfigValidator.validate_color("not-a-color"))
        self.assertFalse(ConfigValidator.validate_color([255, 255]))
        self.assertFalse(ConfigValidator.validate_color([255, -1, 0]))

    def test_valid_color(self) -> None:
        self.assertTrue(ConfigValidator.validate_color([0, 128, 255]))


class WindowValidationTests(unittest.TestCase):
    def test_window_defaults_apply_for_invalid_values(self) -> None:
        config = {"window": {"width": "wide", "height": 100, "title": 123}}
        validated = ConfigValidator.validate_window(config)
        self.assertEqual(validated["width"], 1280)
        self.assertEqual(validated["height"], 720)
        self.assertEqual(validated["title"], "Train Color Matching Game")

    def test_window_preserves_valid_values(self) -> None:
        config = {"window": {"width": 1366, "height": 768, "title": "Custom"}}
        validated = ConfigValidator.validate_window(config)
        self.assertEqual(validated["width"], 1366)
        self.assertEqual(validated["height"], 768)
        self.assertEqual(validated["title"], "Custom")


class PaletteValidationTests(unittest.TestCase):
    def test_invalid_palette_values_fallback_to_defaults(self) -> None:
        config = {
            "colors": {
                "white": [240, 240, 240],
                "red": [300, 0, 0],
                "blue": "nope",
                "green": [0, 255],
            }
        }
        validated = ConfigValidator.validate_colors(config)
        self.assertEqual(validated["white"], [240, 240, 240])
        self.assertEqual(validated["red"], [255, 0, 0])
        self.assertEqual(validated["blue"], [0, 0, 255])
        self.assertEqual(validated["green"], [0, 255, 0])
        self.assertEqual(validated["gray"], [128, 128, 128])


class WrapTextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.font = pygame.font.Font(None, 16)

    def test_empty_text_returns_no_lines(self) -> None:
        self.assertEqual(wrap_text("", self.font, 120), [])

    def test_text_fits_on_single_line(self) -> None:
        text = "color matcher"
        width = self.font.size(text)[0] + 5
        self.assertEqual(wrap_text(text, self.font, width), [text])

    def test_text_wraps_when_exceeding_width(self) -> None:
        text = "color matching game"
        max_width = self.font.size("color matching")[0] - 1
        self.assertEqual(wrap_text(text, self.font, max_width), ["color", "matching game"])

    def test_invalid_width_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            wrap_text("sample", self.font, 0)


class AccuracyHelperTests(unittest.TestCase):
    def test_no_attempts_returns_zero(self) -> None:
        self.assertEqual(calculate_accuracy(0, 0), 0.0)

    def test_basic_percentage(self) -> None:
        self.assertAlmostEqual(calculate_accuracy(3, 4), 75.0)

    def test_invalid_values_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            calculate_accuracy(-1, 2)
        with self.assertRaises(ValueError):
            calculate_accuracy(5, 4)


if __name__ == "__main__":
    unittest.main()
