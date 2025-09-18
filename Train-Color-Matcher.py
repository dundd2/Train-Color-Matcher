# -*- coding: cp1252 -*-
# By dundd2 
# Last update:Feb 2025
# Train-Color-Matcher V1.1

import json  # Used for loading configuration from JSON files
import pygame  # The main Pygame library for game development
import random  # Used for generating random numbers
import os  # Used for handling file paths
import math  # Used for mathematical operations
from typing import List, Dict, Tuple  # Used for type hinting
import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API", category=UserWarning)


# Game Constants: Define fixed values used throughout the game
FRAMERATE = 60  # Frames per second for the game
MIN_WINDOW_WIDTH = 800  # Minimum window width
MIN_WINDOW_HEIGHT = 600  # Minimum window height
BUTTON_WIDTH = 200  # Standard button width
BUTTON_HEIGHT = 50  # Standard button height
MUTE_BUTTON_SIZE = 50  # Size of the mute button
MUTE_BUTTON_LABEL_ON = "ON"  # Label when sound is enabled
MUTE_BUTTON_LABEL_OFF = "OFF"  # Label when sound is muted
TRAIN_SPACING = 80  # Spacing between trains
RAILROAD_TIE_SPACING = 30  # Spacing between railroad ties
RAILROAD_HEIGHT = 240  # Height of the railroad
RAIL_THICKNESS = 5  # Thickness of the rails
PARTICLE_COUNT = 20  # Number of particles in visual effects
EXPLOSION_PARTICLE_COUNT = 30  # Number of particles in explosions
COMBO_BASE_FONT_SIZE = 48  # Base font size for combo messages
COMBO_SUPER_THRESHOLD = 5  # Combo count to trigger "SUPER" message
TRANSITION_SPEED = 500  # Speed of theme transitions
TREE_COUNT = 5  # Number of trees in the background
CLOUD_COUNT = 3  # Number of clouds in the background
STAR_COUNT = 50  # Number of stars in the background
BUILDING_COUNT = 6  # Number of skyline buildings
HOUSE_COUNT = 4  # Number of houses in the background
UI_PADDING = 20  # Padding for UI elements
UI_LINE_HEIGHT = 40  # Line height for UI elements
INSTRUCTION_HEIGHT = 60  # Height of the instruction text background
GLOW_MAX = 100  # Maximum glow radius for buttons
GLOW_MIN = 20  # Minimum glow radius for buttons

# Particle Physics: Define ranges and values for particle behavior
PARTICLE_SIZE_RANGE = (4, 8)  # Range of particle sizes
PARTICLE_VELOCITY_RANGE = (-30, 30)  # Range of particle velocities
PARTICLE_GRAVITY = 15  # Gravity applied to particles
PARTICLE_ALPHA_DECAY_RANGE = (0.5, 1.5)  # Range of alpha decay rates for particles

# Smoke Particle Settings: Define behavior for smoke particles
SMOKE_VELOCITY_X = (-5, 5)  # X velocity range for smoke particles
SMOKE_VELOCITY_Y = (-10, -5)  # Y velocity range for smoke particles
SMOKE_GRAVITY = 2  # Gravity applied to smoke particles
SMOKE_EMISSION_CHANCE = 0.3  # Chance for smoke emission

# Star Settings: Define properties for stars in the background
STAR_SIZE_RANGE = (1, 3)  # Range of star sizes
STAR_BRIGHTNESS_RANGE = (150, 255)  # Range of star brightness

# Cloud Settings: Define properties for clouds in the background
CLOUD_VELOCITY_RANGE = (0.5, 1.5)  # Range of cloud velocities
CLOUD_HEIGHT_RANGE = (50, 150)  # Range of cloud heights
CLOUD_SEGMENT_SIZES = [20, 25, 20]  # Sizes of cloud segments

# Initialize Pygame and fonts module
pygame.init()  # Initialize Pygame
pygame.font.init()  # Initialize the font module

DISPLAY_FLAGS = getattr(pygame, "RESIZABLE", 0)


def set_window_mode(size: Tuple[int, int]) -> pygame.Surface:
    """Set the display mode while tolerating limited pygame stubs used in tests."""
    try:
        return pygame.display.set_mode(size, DISPLAY_FLAGS)
    except TypeError:
        return pygame.display.set_mode(size)

# Configuration validation class: Validates configuration settings
class ConfigValidator:
    # Validates a color value
    @staticmethod
    def validate_color(color):
        if not isinstance(color, list) or len(color) != 3:
            return False
        return all(isinstance(v, int) and 0 <= v <= 255 for v in color)

    # Validates window settings
    @staticmethod
    def validate_window(config):
        window = config.get('window', {})
        defaults = {'width': 1280, 'height': 720, 'title': 'Train Color Matching Game'}
        
        width = window.get('width', defaults['width'])
        height = window.get('height', defaults['height'])
        title = window.get('title', defaults['title'])

        if not isinstance(width, int) or width < 800:
            width = defaults['width']
        if not isinstance(height, int) or height < 600:
            height = defaults['height']
        if not isinstance(title, str):
            title = defaults['title']

        return {'width': width, 'height': height, 'title': title}

    # Validates color settings
    @staticmethod
    def validate_colors(config):
        colors = config.get('colors', {})
        defaults = {
            'white': [255, 255, 255],
            'black': [0, 0, 0],
            'red': [255, 0, 0],
            'blue': [0, 0, 255],
            'green': [0, 255, 0],
            'gray': [128, 128, 128],
            'yellow': [255, 255, 0]
        }

        validated = {}
        for color_name, default_value in defaults.items():
            color = colors.get(color_name, default_value)
            if not ConfigValidator.validate_color(color):
                color = default_value
            validated[color_name] = color

        return validated

    # Validates game settings
    @staticmethod
    def validate_game_settings(config):
        game = config.get('game', {})
        defaults = {
            'initial_train_speed': 5,
            'initial_max_trains': 10,
            'level_up_threshold': 5,
            'max_trains_cap': 15
        }

        validated = {}
        for key, default_value in defaults.items():
            value = game.get(key, default_value)
            if not isinstance(value, (int, float)) or value <= 0:
                value = default_value
            validated[key] = value

        return validated

    # Validates train settings
    @staticmethod
    def validate_train_settings(config):
        train = config.get('train', {})
        defaults = {
            'width': 60,
            'height': 30,
            'wheel_radius': 5
        }

        validated = {}
        for key, default_value in defaults.items():
            value = train.get(key, default_value)
            if not isinstance(value, (int, float)) or value <= 0:
                value = default_value
            validated[key] = value

        return validated

    # Validates parallax settings
    @staticmethod
    def validate_parallax(config):
        parallax = config.get('parallax', {})
        defaults = {
            'cloud_speed': 10,
            'tree_speed': 30,
            'cloud_offset_y': 100,
            'tree_offset_y': 200
        }

        validated = {}
        for key, default_value in defaults.items():
            value = parallax.get(key, default_value)
            if not isinstance(value, (int, float)):
                value = default_value
            validated[key] = value

        return validated

    # Validates the entire configuration
    @staticmethod
    def validate_config(config):
        if not isinstance(config, dict):
            config = {}

        return {
            'window': ConfigValidator.validate_window(config),
            'colors': ConfigValidator.validate_colors(config),
            'game': ConfigValidator.validate_game_settings(config),
            'train': ConfigValidator.validate_train_settings(config),
            'parallax': ConfigValidator.validate_parallax(config)
        }

def wrap_text(text: str, font, max_width: int) -> List[str]:
    """Wraps *text* into lines that do not exceed *max_width* pixels."""
    if font is None:
        raise ValueError("A font instance is required for text wrapping")
    if max_width <= 0:
        raise ValueError("Maximum width must be a positive integer")

    if not text:
        return []

    words = text.split()
    if not words:
        return []

    lines: List[str] = []
    current_line = words[0]

    for word in words[1:]:
        candidate = f"{current_line} {word}"
        width, _ = font.size(candidate)
        if width <= max_width or not current_line:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def calculate_accuracy(correct_attempts: int, total_attempts: int) -> float:
    """Return the hit accuracy as a percentage.

    Args:
        correct_attempts: Number of successful matches.
        total_attempts: Total number of attempts made.

    Returns:
        A percentage in the range 0-100 representing the success rate.

    Raises:
        ValueError: If the provided counts are negative or inconsistent.
    """

    if correct_attempts < 0 or total_attempts < 0:
        raise ValueError("Attempt counts must be non-negative")
    if correct_attempts > total_attempts:
        raise ValueError("Correct attempts cannot exceed total attempts")

    if total_attempts == 0:
        return 0.0

    return (correct_attempts / total_attempts) * 100.0

# Load and validate configuration from JSON file
def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}")
        print("Using default configuration...")
        config = {}
    
    return ConfigValidator.validate_config(config)

# Load configuration
CONFIG = load_config()

# Initialize constants from config
WIDTH = CONFIG["window"]["width"]  # Window width
HEIGHT = CONFIG["window"]["height"]  # Window height
WINDOW_TITLE = CONFIG["window"]["title"]  # Window title

# Colors from config
WHITE = tuple(CONFIG["colors"]["white"])  # White color
BLACK = tuple(CONFIG["colors"]["black"])  # Black color

# Asset directories
ASSETS_DIR = "assets"  # Assets directory
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")  # Fonts directory
SOUNDS_DIR = os.path.join(ASSETS_DIR, "music")  # Sounds directory
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")  # Images directory

# Set up the display
screen = set_window_mode((WIDTH, HEIGHT))  # Create the display
pygame.display.set_caption(WINDOW_TITLE)  # Set the window title

# Colors: Define RGB color values
RED = (255, 0, 0)  # Red color
BLUE = (0, 0, 255)  # Blue color
GREEN = (0, 255, 0)  # Green color
GRAY = (128, 128, 128)  # Gray color
YELLOW = (255, 255, 0)  # Yellow color

# Theme colors: Define color schemes for light and dark themes
LIGHT_THEME = {
    'name': 'LIGHT',
    'background': (245, 245, 245),  # Light theme background color
    'primary': (66, 133, 244),  # Light theme primary color
    'secondary': (52, 168, 83),  # Light theme secondary color
    'accent': (251, 188, 4),  # Light theme accent color
    'error': (234, 67, 53),  # Light theme error color
    'text': (32, 33, 36),  # Light theme text color
    'shadow': (0, 0, 0, 50),  # Light theme shadow color
    'button': (255, 255, 255),  # Light theme button color
    'track': (200, 200, 200),  # Light theme track color
    'rail_color': (100, 100, 100),   # Light theme rail color
    'canvas_fill': (255, 255, 255, 180),
    'canvas_border': (255, 255, 255, 220),
    'night_mode': False
}

DARK_THEME = {
    'name': 'DARK',
    'background': (30, 30, 30),  # Dark theme background color
    'primary': (138, 180, 248),  # Dark theme primary color
    'secondary': (129, 201, 149),  # Dark theme secondary color
    'accent': (253, 214, 99),  # Dark theme accent color
    'error': (242, 139, 130),  # Dark theme error color
    'text': (232, 234, 237),  # Dark theme text color
    'shadow': (0, 0, 0, 80),  # Dark theme shadow color
    'button': (70, 70, 70),  # Dark theme button color
    'track': (70, 70, 70),  # Dark theme track color
    'rail_color': (200, 200, 200),   # Dark theme rail color
    'canvas_fill': (30, 30, 30, 200),
    'canvas_border': (80, 80, 80, 220),
    'night_mode': True
}

LIQUID_GLASS_THEME = {
    'name': 'GLASS',
    'background': (22, 35, 55),
    'background_gradient': ((41, 73, 110), (9, 20, 38)),
    'primary': (64, 156, 255),
    'secondary': (102, 237, 249),
    'accent': (255, 176, 79),
    'error': (255, 99, 132),
    'text': (230, 245, 255),
    'shadow': (15, 28, 55, 130),
    'button': (28, 51, 82),
    'track': (52, 89, 126),
    'rail_color': (195, 220, 255),
    'canvas_fill': (255, 255, 255, 90),
    'canvas_border': (255, 255, 255, 140),
    'glass_highlight': (255, 255, 255, 60),
    'night_mode': True
}


def draw_vertical_gradient(surface: pygame.Surface, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]) -> None:
    """Render a vertical gradient on *surface* from *top_color* to *bottom_color*."""
    height = surface.get_height()
    width = surface.get_width()
    if height <= 1:
        surface.fill(top_color)
        return

    for y in range(height):
        ratio = y / (height - 1)
        color = tuple(
            int(top_color[i] + (bottom_color[i] - top_color[i]) * ratio)
            for i in range(3)
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def draw_glass_panel(surface: pygame.Surface, rect: pygame.Rect, theme: Dict[str, Tuple[int, int, int]]) -> None:
    """Draw a frosted glass style panel using the active *theme*."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    fill_color = theme.get('canvas_fill', (255, 255, 255, 160))
    border_color = theme.get('canvas_border', (255, 255, 255, 200))
    pygame.draw.rect(panel, fill_color, panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, border_color, panel.get_rect(), width=2, border_radius=18)

    highlight_alpha = theme.get('glass_highlight')
    if highlight_alpha and rect.width > 24:
        highlight = pygame.Surface((rect.width - 24, 12), pygame.SRCALPHA)
        highlight.fill(highlight_alpha)
        panel.blit(highlight, (12, 12))

    surface.blit(panel, rect.topleft)

# Game states: Define possible game states
MENU = "menu"  # Menu game state
PLAYING = "playing"  # Playing game state
GAME_OVER = "game_over"  # Game over game state

# Train colors: Define available train colors
TRAIN_COLORS = [RED, BLUE, GREEN]  # List of train colors

# Font settings: Define font path
FONT_PATH = os.path.join(FONTS_DIR, "RobotoCondensed-Italic-VariableFont_wght.ttf")  # Font path

# Initialize the font: Load the font or use a default font
try:
    game_font = pygame.font.Font(FONT_PATH, 36)  # Load the font
except:
    print("Warning: Custom font not found. Using system default.")  # Print a warning if the font is not found
    game_font = pygame.font.Font(None, 36)  # Use a default font

# Sound manager class to handle game sounds
class SoundManager:
    # Initializes the sound manager
    def __init__(self):
        try:
            self.sounds = {
                'correct': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'General_sound_effect.mp3')),  # Correct sound
                'wrong': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Suspenseful Music.mp3')),  # Wrong sound
                'click': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Button sounds.mp3')),  # Click sound
                'game_over': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Cutscene Music.mp3')),  # Game over sound
                'background': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Menu Music.mp3')),  # Background music
                'button_hover': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'UI opening sounds.mp3')),  # Button hover sound
                'level_up': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'MC Level Up.mp3')),  # Level up sound
                'victory': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Victory Music.mp3')),  # Victory sound
                'item_pickup': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Item Pickup.mp3')),  # Item pickup sound
                'confirmation': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Confirmation Sounds (in UI).mp3'))  # Confirmation sound
            }
            self.sounds['background'].set_volume(0.5)  # Set background music volume
            self.sounds['background'].play(-1)  # Play background music on loop
        except:
            print("Warning: Sound files not found. Running without sound.")  # Print a warning if sound files are not found
            self.sounds = {}  # Initialize an empty sound dictionary
        self.muted = False  # Initialize muted state

    # Plays a sound
    def play(self, sound_name):
        if not self.muted and sound_name in self.sounds:  # Check if not muted and sound exists
            try:
                self.sounds[sound_name].play()  # Play the sound
            except:
                pass

    # Toggles mute state
    def toggle_mute(self):
        self.muted = not self.muted  # Toggle muted state
        if self.muted:
            pygame.mixer.pause()  # Pause all sounds
        else:
            pygame.mixer.unpause()  # Unpause all sounds

# Particle class for visual effects
class Particle:
    # Initializes a particle
    def __init__(self, x, y, color):
        self.x = x  # X position
        self.y = y  # Y position
        self.color = color  # Color
        self.size = random.randint(*PARTICLE_SIZE_RANGE)  # Random size
        self.lifetime = 1.0  # Lifetime
        self.velocity = [
            random.uniform(*PARTICLE_VELOCITY_RANGE),  # Random X velocity
            random.uniform(*PARTICLE_VELOCITY_RANGE)   # Random Y velocity
        ]
        self.gravity = PARTICLE_GRAVITY  # Gravity
        self.alpha_decay = random.uniform(*PARTICLE_ALPHA_DECAY_RANGE)  # Alpha decay rate
        self.original_size = self.size  # Store original size

    # Updates the particle
    def update(self, dt):
        self.x += self.velocity[0] * dt  # Update X position
        self.y += self.velocity[1] * dt  # Update Y position
        self.velocity[1] += self.gravity * dt  # Apply gravity
        self.lifetime -= dt * 2  # Reduce lifetime
        self.size = max(0, self.original_size * self.lifetime)  # Scale size over lifetime

    # Draws the particle
    def draw(self, screen):
        alpha = int(255 * self.lifetime)  # Calculate alpha value
        if (alpha > 0):
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)  # Create a surface
            pygame.draw.circle(surface, (*self.color, alpha), (self.size, self.size), self.size)  # Draw a circle
            screen.blit(surface, (self.x - self.size, self.y - self.size))  # Blit the surface to the screen

# Smoke particle class for train smoke effects
class SmokeParticle(Particle):
    # Initializes a smoke particle
    def __init__(self, x, y, color):
        super().__init__(x, y, color)  # Call superclass constructor
        self.velocity = [
            random.uniform(*SMOKE_VELOCITY_X),  # Random X velocity
            random.uniform(*SMOKE_VELOCITY_Y)   # Random Y velocity
        ]
        self.gravity = SMOKE_GRAVITY  # Gravity
        self.original_size = self.size  # Store original size

    # Updates the smoke particle
    def update(self, dt):
        self.x += self.velocity[0] * dt  # Update X position
        self.y += self.velocity[1] * dt  # Update Y position
        self.velocity[1] += self.gravity * dt  # Apply gravity
        self.lifetime -= dt  # Reduce lifetime
        self.size = max(0, self.original_size * self.lifetime)  # Scale size over lifetime

    # Draws the smoke particle
    def draw(self, screen):
        alpha = int(255 * self.lifetime)  # Calculate alpha value
        if alpha > 0:
            size = int(self.size)  # Get integer size
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)  # Create a surface
            pygame.draw.circle(surface, (*self.color, alpha), (size, size), size)  # Draw a circle
            screen.blit(surface, (self.x - size, self.y - size))  # Blit the surface to the screen

# Explosion particle class for visual effects
class ExplosionParticle(Particle):
    # Initializes an explosion particle
    def __init__(self, x, y, color):
        super().__init__(x, y, color)  # Call superclass constructor
        self.lifetime = random.uniform(0.3, 0.7)  # Random lifetime
        self.velocity = [random.uniform(-100, 100), random.uniform(-100, 100)]  # Random velocity
        self.gravity = 50  # Gravity

    # Updates the explosion particle
    def update(self, dt):
        super().update(dt)  # Call superclass update method

# Button class for UI elements
class Button:
    # Initializes a button
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)  # Create a rectangle
        self.text = text  # Text
        self.color = color  # Color
        self.text_color = text_color  # Text color
        self.font = pygame.font.Font(FONT_PATH, 36)  # Font

    # Draws the button
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)  # Draw the rectangle
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Draw the border
        text_surface = self.font.render(self.text, True, self.text_color)  # Render the text
        text_rect = text_surface.get_rect(center=self.rect.center)  # Get the text rectangle
        screen.blit(text_surface, text_rect)  # Blit the text to the screen

    def set_colors(self, color, text_color=None):
        self.color = color
        if text_color is not None:
            self.text_color = text_color

    # Checks if the button is clicked
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)  # Check if the mouse position is inside the rectangle

# Modern button class with hover effects and particles
class ModernButton(Button):
    # Initializes a modern button
    def __init__(self, x, y, width, height, text, color, theme, sound_manager):
        super().__init__(x, y, width, height, text, color)  # Call superclass constructor
        self.hover = False  # Hover state
        self.original_y = y  # Original Y position
        self.animation_offset = 0  # Animation offset
        self.particles = []  # Particles
        self.theme = theme  # Theme
        self.glow_radius = 0  # Glow radius
        self.glow_direction = 1  # Glow direction
        self.sound_manager = sound_manager  # Sound manager
        self.font = pygame.font.Font(FONT_PATH, 36)  # Font
        self.base_color = color  # Preserve the intended color

    # Draws the modern button
    def draw(self, screen):
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)  # Create a surface for the shadow
        pygame.draw.rect(shadow_surface, self.theme['shadow'], 
                        (0, 0, self.rect.width, self.rect.height), border_radius=10)  # Draw the shadow
        screen.blit(shadow_surface, (self.rect.x, self.rect.y + 5))  # Blit the shadow to the screen

        hover_offset = 3 if self.hover else 0  # Hover offset

        if self.hover:
            glow_color = (255, 255, 255, int(self.glow_radius))  # Glow color
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)  # Create a surface for the glow
            pygame.draw.rect(glow_surface, glow_color, (0, 0, self.rect.width + 20, self.rect.height + 20), border_radius=10)  # Draw the glow
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - hover_offset - self.animation_offset - 10))  # Blit the glow to the screen

        pygame.draw.rect(screen, self.color, 
                        (self.rect.x, self.rect.y - hover_offset - self.animation_offset, 
                         self.rect.width, self.rect.height), 
                        border_radius=10)  # Draw the rectangle

        text_surface = self.font.render(self.text, True, self.theme['text'])  # Render the text
        text_rect = text_surface.get_rect(center=self.rect.center)  # Get the text rectangle
        text_rect.y -= hover_offset + self.animation_offset  # Adjust the text position
        screen.blit(text_surface, text_rect)  # Blit the text to the screen

        for particle in self.particles:  # Draw the particles
            particle.draw(screen)

    def set_color(self, color):
        self.base_color = color
        self.color = color

    def apply_theme(self, theme):
        self.theme = theme

    def apply_layout(self, x, y, width=None, height=None):
        width = width if width is not None else self.rect.width
        height = height if height is not None else self.rect.height
        self.rect = pygame.Rect(x, y, width, height)
        self.original_y = y

    # Updates the modern button
    def update(self, dt):
        if self.hover:  # If the button is hovered
            self.animation_offset = math.sin(pygame.time.get_ticks() / 200) * 2  # Calculate the animation offset
            self.glow_radius += 5 * self.glow_direction  # Update the glow radius
            if self.glow_radius > GLOW_MAX:  # If the glow radius is too big
                self.glow_direction = -1  # Reverse the glow direction
            elif self.glow_radius < GLOW_MIN:  # If the glow radius is too small
                self.glow_direction = 1  # Reverse the glow direction
        else:
            self.glow_radius = 0  # Reset the glow radius
            self.glow_direction = 1  # Reset the glow direction

        self.particles = [p for p in self.particles if p.lifetime > 0]  # Remove dead particles
        for particle in self.particles:  # Update the particles
            particle.update(dt)

    # Handles hover events
    def handle_hover(self, pos):
        is_hovering = self.rect.collidepoint(pos)  # Check if the mouse is hovering over the button
        if is_hovering and not self.hover:  # If the button is hovered and was not previously hovered
            self.sound_manager.play('button_hover')  # Play the button hover sound
        self.hover = is_hovering  # Set the hover state

    # Creates particles
    def create_particles(self):
        for _ in range(PARTICLE_COUNT):  # Create particles
            self.particles.append(Particle(
                self.rect.centerx,   # X position
                self.rect.centery,   # Y position
                self.color   # Color
            ))

# Train renderer class to handle train drawing
class TrainRenderer:
    # Initializes the train renderer
    def __init__(self, train):
        self.train = train  # Train

    # Draws the train
    def draw(self, screen, is_dark_mode=False):
        pygame.draw.rect(screen, self.train.color, 
            (self.train.x, self.train.y, 
             CONFIG["train"]["width"], CONFIG["train"]["height"]), 
            border_radius=5)  # Draw the train body
        
        pygame.draw.rect(screen, (50, 50, 50), 
            (self.train.x + 10, self.train.y - 10, 10, 10))  # Draw the train chimney
        
        window_color = (255, 255, 200) if is_dark_mode else (200, 200, 200)  # Window color
        if is_dark_mode:  # If dark mode is enabled
            for window_x in [self.train.x + 25, self.train.x + 45]:  # For each window
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)  # Create a surface for the glow
                pygame.draw.circle(glow_surf, (255, 255, 0, 100), (10, 10), 8)  # Draw the glow
                screen.blit(glow_surf, (window_x - 5, self.train.y))  # Blit the glow to the screen
        
        pygame.draw.rect(screen, window_color, (self.train.x + 25, self.train.y + 5, 10, 10))  # Draw the first window
        pygame.draw.rect(screen, window_color, (self.train.x + 45, self.train.y + 5, 10, 10))  # Draw the second window
        
        pygame.draw.circle(screen, BLACK, (self.train.x + 15, self.train.y + 30), 5)  # Draw the first wheel
        pygame.draw.circle(screen, BLACK, (self.train.x + 45, self.train.y + 30), 5)  # Draw the second wheel

        for particle in self.train.smoke_particles:  # Draw the smoke particles
            particle.draw(screen)

# Train class to handle train behavior
class Train:
    # Initializes a train
    def __init__(self, x, y, color):
        self.x = x  # X position
        self.y = y  # Y position
        self.color = color  # Color
        self.width = CONFIG["train"]["width"]  # Width
        self.height = CONFIG["train"]["height"]  # Height
        self.moving = False  # Moving state
        self.move_direction = "left"  # Move direction
        self.speed = CONFIG['game']['initial_train_speed']  # Movement speed
        self.smoke_particles = []  # Smoke particles
        self.renderer = TrainRenderer(self)  # Train renderer
        self.bounds_width = WIDTH  # Default movement bounds

    # Draws the train
    def draw(self, screen, is_dark_mode=False):
        self.renderer.draw(screen, is_dark_mode)  # Draw the train

    # Moves the train
    def move(self):
        if self.moving:  # If the train is moving
            step = self.speed  # Movement step for this frame
            if self.move_direction == "left":  # If the train is moving left
                self.x -= step  # Move left
            elif self.move_direction == "right":  # If the train is moving right
                self.x += step  # Move right

            self.emit_smoke()  # Emit smoke

            for particle in self.smoke_particles:  # Update the smoke particles
                particle.update(0.1)  # Update the particle

            self.smoke_particles = [p for p in self.smoke_particles if p.lifetime > 0]  # Remove dead particles

            bounds = getattr(self, 'bounds_width', WIDTH)
            if self.x + self.width < 0 or self.x > bounds:  # If the train is out of bounds
                self.moving = False  # Stop moving
        return self.moving  # Return the moving state

    # Emits smoke
    def emit_smoke(self):
        if random.random() < SMOKE_EMISSION_CHANCE:  # If the smoke emission chance is met
            self.smoke_particles.append(SmokeParticle(self.x + 10, self.y - 10, GRAY))  # Add a smoke particle

# Message class for displaying messages on the screen
class Message:
    # Initializes a message
    def __init__(self, text, color, duration=1.0):
        self.text = text  # Text
        self.color = color  # Color
        self.duration = duration  # Duration
        self.start_time = pygame.time.get_ticks()  # Start time
        self.font = pygame.font.Font(FONT_PATH, 48)  # Font
        self.alpha = 255  # Alpha value
        
    # Checks if the message should be removed
    def should_remove(self):
        return self.alpha <= 0  # Return True if the alpha value is less than or equal to 0

    # Draws the message
    def draw(self, screen):
        if self.alpha > 0:  # If the alpha value is greater than 0
            text_surface = self.font.render(self.text, True, self.color)  # Render the text
            text_surface.set_alpha(self.alpha)  # Set the alpha value
            surface = pygame.display.get_surface()
            width = surface.get_width() if surface else WIDTH
            height = surface.get_height() if surface else HEIGHT
            text_rect = text_surface.get_rect(center=(width // 2, height // 2))  # Get the text rectangle
            screen.blit(text_surface, text_rect)  # Blit the text to the screen

    # Updates the message
    def update(self, dt):
        self.alpha -= 255 * dt  # Reduce the alpha value

# Parallax layer class for creating parallax scrolling effects
class ParallaxLayer:
    # Initializes a parallax layer
    def __init__(self, image_path, speed, offset_y=0):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()  # Load the image
            self.valid = True  # Set valid to True
        except (pygame.error, FileNotFoundError) as e:  # If the image is not found
            print(f"Warning: Could not load image {image_path}: {e}")  # Print a warning
            self.image = pygame.Surface((800, 200))  # Create a fallback surface
            self.image.fill((200, 200, 200))  # Fill the surface with gray
            self.valid = False  # Set valid to False
        
        self.x = 0  # X position
        self.offset_y = offset_y  # Store the vertical offset
        self.y = HEIGHT - self.image.get_height() + offset_y  # Y position
        self.speed = speed  # Speed

    # Updates the parallax layer
    def update(self, dt):
        if not self.valid:  # If the layer is not valid
            return  # Return
        self.x -= self.speed * dt  # Update the X position
        if (self.x <= -self.image.get_width()):  # If the layer is out of bounds
            self.x = 0  # Reset the X position

    # Draws the parallax layer
    def draw(self, screen):
        if not self.valid:  # If the layer is not valid
            return  # Return
        screen.blit(self.image, (self.x, self.y))  # Blit the image to the screen
        screen.blit(self.image, (self.x + self.image.get_width(), self.y))  # Blit the image to the screen

# Game class to handle game logic
class Game:
    # Initializes the game
    def __init__(self):
        game_settings = CONFIG['game']  # Cache game configuration for reuse
        self.level_up_threshold = game_settings['level_up_threshold']  # Set level up threshold
        self.base_train_speed = game_settings['initial_train_speed']  # Store base train speed from config
        self.base_max_trains = game_settings['initial_max_trains']  # Store base max trains from config
        self.max_trains_cap = game_settings.get('max_trains_cap', 15)  # Store configured train cap
        self.train_spacing = game_settings.get('train_spacing', TRAIN_SPACING)  # Spacing between trains

        if not hasattr(self, 'theme'):
            self.theme = LIGHT_THEME  # Fallback theme if none is provided

        self.window_width = WIDTH
        self.window_height = HEIGHT

        self.state = MENU  # Set the initial state to MENU
        self.high_score = 0  # Initialize high score
        self.sound_manager = SoundManager()  # Initialize sound manager
        self.messages = []  # Initialize messages
        self.mute_button = Button(
            UI_PADDING,
            UI_PADDING,
            MUTE_BUTTON_SIZE,
            MUTE_BUTTON_SIZE,
            MUTE_BUTTON_LABEL_OFF if self.sound_manager.muted else MUTE_BUTTON_LABEL_ON,
            self.theme['button'],
            self.theme['text']
        )  # Create mute button
        self.background = pygame.Surface((self.window_width, self.window_height))  # Create background surface

        self.train_speed = self.base_train_speed  # Set initial train speed
        self.max_trains = self.base_max_trains  # Set initial max trains
        self.train_positions = []  # Placeholder before game reset
        self.explosion_particles = []  # Initialize explosion particles
        self.combo_count = 0  # Initialize combo count
        self.combo_message = None  # Initialize combo message
        self.correct_matches = 0  # Track number of correct selections
        self.incorrect_matches = 0  # Track number of incorrect selections
        self.max_combo = 0  # Track best combo streak

        self.reset_game()  # Reset the game
        self.create_buttons()  # Create buttons
        self.create_background()  # Create background
        self.current_train_index = 0  # Initialize current train index

        self.font = pygame.font.Font(FONT_PATH, 36)  # Set font
        self.parallax_layers = [
            ParallaxLayer(os.path.join(IMAGES_DIR, "cloud_layer.png"), 10),
            ParallaxLayer(os.path.join(IMAGES_DIR, "tree_layer.png"), 30)
        ]

    # Creates the background
    def create_background(self):
        self.background = pygame.Surface((self.window_width, self.window_height))
        self.background.fill(self.theme['background'])  # Fill the background
        for x in range(0, self.window_width, 30):  # Draw the track
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 235), (self.window_width, 235), 5)  # Draw the rails
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 265), (self.window_width, 265), 5)

    # Adds a message
    def add_message(self, text, color, duration=1.0):
        self.messages = [msg for msg in self.messages if not msg.should_remove()]  # Remove old messages
        self.messages.append(Message(text, color, duration))  # Add new message

    # Resets the game
    def reset_game(self):
        self.track_trains = []  # Initialize track trains
        self.selection_trains = []  # Initialize selection trains
        self.score = 0  # Initialize score
        self.current_train_index = 0  # Initialize current train index
        self.all_trains_moving = False  # Initialize all trains moving state
        self.explosion_particles = []  # Initialize explosion particles
        self.level = 1  # Initialize level
        self.train_speed = self.base_train_speed  # Initialize train speed from config
        self.max_trains = self.base_max_trains  # Initialize max trains from config
        self.train_positions = [i * self.train_spacing for i in range(self.max_trains)]  # Set train positions
        self.initialize_trains()  # Initialize trains
        self.last_time = pygame.time.get_ticks()  # Set last time
        self.combo_count = 0  # Initialize combo count
        self.combo_message = None  # Initialize combo message
        self.correct_matches = 0  # Reset correct match counter
        self.incorrect_matches = 0  # Reset incorrect match counter
        self.max_combo = 0  # Reset best combo streak

    # Creates buttons
    def create_buttons(self):
        self.start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game", self.theme['primary'])  # Create start button
        self.quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Quit", self.theme['error'])  # Create quit button
        self.play_again_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Play Again", self.theme['primary'])  # Create play again button

    # Initializes trains
    def initialize_trains(self):
        self.train_positions = [i * self.train_spacing for i in range(self.max_trains)]  # Set train positions
        self.track_trains = []  # Initialize track trains
        for i in range(self.max_trains):  # Create track trains
            color = random.choice(TRAIN_COLORS)  # Choose a random color
            x = self.train_positions[i]  # Set X position
            train = Train(x, 200, color)  # Create the train
            train.speed = self.train_speed  # Apply the current game speed
            self.track_trains.append(train)  # Add train

        self.selection_trains = []  # Initialize selection trains
        for i, color in enumerate(TRAIN_COLORS):  # Create selection trains
            self.selection_trains.append(Train(250 + i * 100, 400, color))  # Add train

    # Draws the game
    def draw(self, screen):
        screen.fill(self.theme['background'])  # Fill the screen
        
        if self.state == MENU:  # If the state is MENU
            self.draw_menu(screen)  # Draw the menu
        elif self.state == PLAYING:  # If the state is PLAYING
            self.draw_game(screen)  # Draw the game
        elif self.state == GAME_OVER:  # If the state is GAME_OVER
            self.draw_game_over(screen)  # Draw the game over screen

    # Draws the menu
    def draw_menu(self, screen):
        title_font = pygame.font.Font(FONT_PATH, 64)  # Set title font
        title_text = title_font.render("Train Color Matcher", True, self.theme['text'])  # Render title text
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))  # Get title rectangle
        screen.blit(title_text, title_rect)  # Blit title text
        
        self.start_button.draw(screen)  # Draw start button
        self.quit_button.draw(screen)  # Draw quit button

        version_font = pygame.font.Font(FONT_PATH, 16)  # Set version font
        version_text = version_font.render("v1.1 | Built by dundd - Feb 2025", True, self.theme['text'])  # Render version text
        version_rect = version_text.get_rect(bottomleft=(10, HEIGHT - 10))  # Get version rectangle
        screen.blit(version_text, version_rect)  # Blit version text

    # Draws the game
    def draw_game(self, screen):
        for layer in self.parallax_layers:  # Draw parallax layers
            layer.draw(screen)
        
        screen.blit(self.background, (0, 0))  # Blit background
        
        for i, train in enumerate(self.track_trains):  # Draw track trains
            if not train.moving:
                train.draw(screen)
        for train in self.selection_trains:  # Draw selection trains
            train.draw(screen)

        for message in self.messages:  # Draw messages
            message.draw(screen)

        font = pygame.font.Font(FONT_PATH, 36)  # Set font
        
        remaining_trains = len(self.track_trains) - self.current_train_index  # Calculate remaining trains
        progress_text = font.render(f'Remaining Trains: {remaining_trains}', True, self.theme['text'])  # Render progress text
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])  # Render score text
        level_text = font.render(f'Level: {self.level}', True, self.theme['text'])  # Render level text
        accuracy = calculate_accuracy(
            self.correct_matches,
            self.correct_matches + self.incorrect_matches
        )
        accuracy_text = font.render(f'Accuracy: {accuracy:.0f}%', True, self.theme['text'])  # Render accuracy text
        combo_text = font.render(
            f'Combo: x{self.combo_count} (Best x{self.max_combo})',
            True,
            self.theme['text']
        )  # Render combo text

        screen.blit(progress_text, (10, 10))  # Blit progress text
        screen.blit(score_text, (10, 40))  # Blit score text
        screen.blit(level_text, (10, 70))  # Blit level text
        screen.blit(accuracy_text, (10, 100))  # Blit accuracy text
        screen.blit(combo_text, (10, 130))  # Blit combo text

        self.mute_button.draw(screen)  # Draw mute button

        for particle in self.explosion_particles:  # Draw explosion particles
            particle.draw(screen)

        if self.combo_message:  # Draw combo message
            self.combo_message.draw(screen)

    # Draws the game over screen
    def draw_game_over(self, screen):
        font = pygame.font.Font(FONT_PATH, 64)  # Set font
        game_over_text = font.render("Game Over!", True, self.theme['text'])  # Render game over text
        score_text = font.render(f"Final Score: {self.score}", True, self.theme['text'])  # Render score text
        accuracy = calculate_accuracy(
            self.correct_matches,
            self.correct_matches + self.incorrect_matches
        )
        accuracy_text = font.render(f"Accuracy: {accuracy:.0f}%", True, self.theme['text'])  # Render accuracy text
        best_combo_text = font.render(f"Best Combo: x{self.max_combo}", True, self.theme['text'])  # Render combo text

        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//4))  # Blit game over text
        screen.blit(score_text, (WIDTH//2 - 150, HEIGHT//3))  # Blit score text
        screen.blit(accuracy_text, (WIDTH//2 - 150, HEIGHT//3 + 70))  # Blit accuracy text
        screen.blit(best_combo_text, (WIDTH//2 - 150, HEIGHT//3 + 140))  # Blit best combo text

        self.play_again_button.draw(screen)  # Draw play again button

    # Handles click events
    def handle_click(self, pos):
        if self.mute_button.is_clicked(pos):  # If the mute button is clicked
            self.sound_manager.muted = not self.sound_manager.muted  # Toggle mute state
            self.update_mute_button_label()  # Refresh mute button label
            return True

        if self.state == MENU:  # If the state is MENU
            if self.start_button.is_clicked(pos):  # If the start button is clicked
                self.start_button.create_particles()  # Create particles
                self.sound_manager.play('click')  # Play click sound
                self.state = PLAYING  # Set state to PLAYING
                self.reset_game()  # Reset the game
            elif self.quit_button.is_clicked(pos):  # If the quit button is clicked
                return False
                
        elif self.state == PLAYING:  # If the state is PLAYING
            clicked = False
            for selection_train in self.selection_trains:  # Check if a selection train is clicked
                if (selection_train.x < pos[0] < selection_train.x + selection_train.width and
                    selection_train.y < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    
                    if self.current_train_index < len(self.track_trains):  # If there are remaining track trains
                        current_train = self.track_trains[self.current_train_index]
                        
                        if selection_train.color == current_train.color:  # If the colors match
                            self.sound_manager.play('correct')  # Play correct sound
                            self.create_explosion(current_train.x, current_train.y, current_train.color)  # Create explosion
                            current_train.moving = True  # Set train to moving
                            current_train.move_direction = "left"  # Set move direction to left
                            current_train.speed = self.train_speed  # Move using the configured speed
                            self.score += 1  # Increment score
                            self.add_message("Correct!", self.theme['secondary'])  # Add correct message
                            self.current_train_index += 1  # Increment current train index
                            self.combo_count += 1  # Increment combo count
                            self.correct_matches += 1  # Increment correct counter
                            self.max_combo = max(self.max_combo, self.combo_count)  # Update best combo
                            self.update_combo_message()  # Update combo message
                            self.sound_manager.play('item_pickup')  # Play item pickup sound
                            if self.current_train_index >= len(self.track_trains):  # If all track trains are matched
                                self.all_trains_moving = True  # Set all trains moving state to True
                        else:
                            self.sound_manager.play('wrong')  # Play wrong sound
                            self.add_message("Wrong Color!", self.theme['error'])  # Add wrong color message
                            self.combo_count = 0  # Reset combo count
                            self.combo_message = None  # Reset combo message
                            self.incorrect_matches += 1  # Increment incorrect counter
            if not clicked:
                self.add_message("Please click on a train!", self.theme['accent'], 0.5)  # Add click on train message

        elif self.state == GAME_OVER:  # If the state is GAME_OVER
            if self.play_again_button.is_clicked(pos):  # If the play again button is clicked
                self.sound_manager.play('click')  # Play click sound
                self.state = PLAYING  # Set state to PLAYING
                self.reset_game()  # Reset the game
            elif self.quit_button.is_clicked(pos):  # If the quit button is clicked
                return False
        return True

    # Updates the game
    def update(self):
        if self.state == PLAYING:  # If the state is PLAYING
            current_time = pygame.time.get_ticks()  # Get current time
            dt = (current_time - self.last_time) / 1000.0  # Calculate delta time
            self.last_time = current_time  # Update last time

            for layer in self.parallax_layers:  # Update parallax layers
                layer.update(dt)

            for train in self.track_trains:  # Update track trains
                if train.moving:
                    train.move()

            if self.all_trains_moving and all(not train.moving for train in self.track_trains):  # If all trains are moving and stopped
                self.state = GAME_OVER  # Set state to GAME_OVER
                self.high_score = max(self.high_score, self.score)  # Update high score
                self.sound_manager.play('game_over')  # Play game over sound

            if self.score >= self.level * self.level_up_threshold:  # If the score meets the level up threshold
                self.level_up()  # Level up

            for message in self.messages:  # Update messages
                message.update(dt)
            self.messages = [msg for msg in self.messages if not msg.should_remove()]  # Remove old messages

            for particle in self.explosion_particles:  # Update explosion particles
                particle.update(dt)
            self.explosion_particles = [p for p in self.explosion_particles if p.lifetime > 0]  # Remove old particles

            if self.combo_message:  # Update combo message
                self.combo_message.update(dt)
                if self.combo_message.should_remove():
                    self.combo_message = None

    # Levels up the game
    def level_up(self):
        self.level += 1  # Increment level
        self.sound_manager.play('level_up')  # Play level up sound
        self.add_message(f"Level Up! {self.level}", self.theme['primary'], 1.5)  # Add level up message
        self.train_speed += 1  # Increment train speed
        self.max_trains = min(self.max_trains + 2, self.max_trains_cap)  # Increment max trains with cap
        self.initialize_trains()  # Initialize trains
        self.sound_manager.play('victory')  # Play victory sound

    # Creates an explosion
    def create_explosion(self, x, y, color):
        for _ in range(30):  # Create explosion particles
            self.explosion_particles.append(ExplosionParticle(x, y, color))

    # Updates the combo message
    def update_combo_message(self):
        if (self.combo_count > 1):  # If the combo count is greater than 1
            text = f"COMBO x{self.combo_count}!"  # Set combo text
            if self.combo_count >= 5:  # If the combo count is greater than or equal to 5
                text += " SUPER!"  # Add SUPER to the text
            color = (255, 215, 0) if self.combo_count >= 5 else self.theme['accent']  # Set combo color
            self.combo_message = ComboMessage(text, color, 1.5, 48 + min(self.combo_count * 4, 32))  # Create combo message
            self.sound_manager.play('level_up')  # Play level up sound

# Tree class for drawing trees in the background
class Tree:
    # Initializes a tree
    def __init__(self, x, y):
        self.x = x  # X position
        self.y = y  # Y position

    # Draws the tree
    def draw(self, screen):
        pygame.draw.rect(screen, (139, 69, 19), (self.x, self.y, 20, 40))  # Draw the trunk
        pygame.draw.circle(screen, (34, 139, 34), (self.x + 10, self.y), 30)  # Draw the leaves

# Cloud class for drawing clouds in the background
class Cloud:
    # Initializes a cloud
    def __init__(self, x, y):
        self.x = x  # X position
        self.y = y  # Y position
        self.velocity = random.uniform(0.5, 1.5)  # Set velocity

    # Updates the cloud
    def update(self, dt):
        self.x += self.velocity * dt  # Update X position
        surface = pygame.display.get_surface()
        limit = surface.get_width() if surface else WIDTH
        if self.x > limit + 100:  # If the cloud is out of bounds
            self.x = -100  # Reset X position

    # Draws the cloud
    def draw(self, screen):
        base_x = int(self.x)
        base_y = int(self.y)
        pygame.draw.circle(screen, WHITE, (base_x, base_y), 20)  # Draw the first segment
        pygame.draw.circle(screen, WHITE, (base_x + 20, base_y + 10), 25)  # Draw the second segment
        pygame.draw.circle(screen, WHITE, (base_x + 40, base_y), 20)  # Draw the third segment

# Star class for drawing stars in the background
class Star:
    # Initializes a star
    def __init__(self, x, y):
        self.x = x  # X position
        self.y = y  # Y position
        self.size = random.randint(1, 3)  # Set size
        self.brightness = random.randint(150, 255)  # Set brightness

    # Draws the star
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)  # Set color
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)  # Draw the star

# Building and house background elements
class Building:
    def __init__(self, width_ratio: float, height_ratio: float, x_ratio: float):
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.x_ratio = x_ratio
        self.day_color = random.choice([(205, 210, 224), (190, 198, 214), (220, 206, 188), (210, 202, 195)])
        self.night_color = random.choice([(70, 78, 100), (60, 68, 92), (82, 90, 120), (74, 84, 112)])
        self.day_window_color = (245, 248, 252)
        self.night_window_color = (255, 214, 120)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.window_rects: List[pygame.Rect] = []

    def reposition(self, window_width: int, window_height: int, base_y: int) -> None:
        width = max(60, int(window_width * self.width_ratio))
        height = max(120, int(window_height * self.height_ratio))
        center_x = int(window_width * self.x_ratio)
        left = max(UI_PADDING, center_x - width // 2)
        left = min(left, window_width - UI_PADDING - width)
        self.rect = pygame.Rect(left, base_y - height, width, height)
        self._rebuild_windows()

    def _rebuild_windows(self) -> None:
        self.window_rects.clear()
        cols = max(2, self.rect.width // 40)
        rows = max(2, self.rect.height // 50)
        padding_x = 8
        padding_y = 12
        available_width = self.rect.width - padding_x * (cols + 1)
        available_height = self.rect.height - padding_y * (rows + 1)
        if available_width <= 0 or available_height <= 0:
            return
        window_width = available_width / cols
        window_height = available_height / rows
        if window_width < 6 or window_height < 6:
            return
        for row in range(rows):
            for col in range(cols):
                x = int(self.rect.left + padding_x * (col + 1) + window_width * col)
                y = int(self.rect.top + padding_y * (row + 1) + window_height * row)
                self.window_rects.append(pygame.Rect(x, y, int(window_width), int(window_height)))

    def draw(self, screen: pygame.Surface, night_mode: bool) -> None:
        color = self.night_color if night_mode else self.day_color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        outline_color = (0, 0, 0, 30) if night_mode else (0, 0, 0, 40)
        try:
            pygame.draw.rect(screen, outline_color, self.rect, width=1, border_radius=6)
        except TypeError:
            pygame.draw.rect(screen, (40, 40, 40), self.rect, width=1, border_radius=6)
        window_color = self.night_window_color if night_mode else self.day_window_color
        for window in self.window_rects:
            pygame.draw.rect(screen, window_color, window, border_radius=2)


class House:
    def __init__(self, width_ratio: float, height_ratio: float, x_ratio: float):
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.x_ratio = x_ratio
        self.roof_ratio = random.uniform(0.35, 0.5)
        self.day_body_color = random.choice([(232, 219, 202), (224, 210, 198), (236, 226, 210)])
        self.night_body_color = random.choice([(90, 82, 100), (98, 90, 112), (82, 74, 96)])
        self.day_roof_color = random.choice([(180, 90, 90), (160, 102, 82), (188, 120, 96)])
        self.night_roof_color = random.choice([(120, 60, 70), (110, 70, 80), (100, 64, 74)])
        self.window_day_color = (250, 250, 240)
        self.window_night_color = (255, 220, 150)
        self.body_rect = pygame.Rect(0, 0, 0, 0)
        self.roof_points: List[Tuple[int, int]] = []
        self.window_rects: List[pygame.Rect] = []
        self.door_rect = pygame.Rect(0, 0, 0, 0)

    def reposition(self, window_width: int, window_height: int, base_y: int) -> None:
        width = max(50, int(window_width * self.width_ratio))
        height = max(60, int(window_height * self.height_ratio))
        center_x = int(window_width * self.x_ratio)
        left = max(UI_PADDING, center_x - width // 2)
        left = min(left, window_width - UI_PADDING - width)
        body_height = max(30, int(height * (1 - self.roof_ratio)))
        self.body_rect = pygame.Rect(left, base_y - body_height, width, body_height)
        roof_height = max(14, int(height * self.roof_ratio))
        roof_top = self.body_rect.top - roof_height
        self.roof_points = [
            (self.body_rect.centerx, roof_top),
            (self.body_rect.right + 6, self.body_rect.top),
            (self.body_rect.left - 6, self.body_rect.top)
        ]
        door_width = max(12, width // 6)
        door_height = max(26, body_height - 12)
        door_x = self.body_rect.centerx - door_width // 2
        door_y = self.body_rect.bottom - door_height
        self.door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        window_size = max(10, width // 7)
        window_y = self.body_rect.top + max(6, body_height // 4)
        window_offset = max(8, width // 5)
        left_window_x = self.body_rect.left + window_offset - window_size // 2
        right_window_x = self.body_rect.right - window_offset - window_size // 2
        self.window_rects = [
            pygame.Rect(left_window_x, window_y, window_size, window_size),
            pygame.Rect(right_window_x, window_y, window_size, window_size)
        ]

    def draw(self, screen: pygame.Surface, night_mode: bool) -> None:
        body_color = self.night_body_color if night_mode else self.day_body_color
        roof_color = self.night_roof_color if night_mode else self.day_roof_color
        window_color = self.window_night_color if night_mode else self.window_day_color
        door_color = (90, 70, 60) if night_mode else (130, 100, 90)
        pygame.draw.rect(screen, body_color, self.body_rect, border_radius=6)
        pygame.draw.polygon(screen, roof_color, self.roof_points)
        pygame.draw.rect(screen, door_color, self.door_rect, border_radius=3)
        for window in self.window_rects:
            pygame.draw.rect(screen, window_color, window, border_radius=2)



# Modern game class with additional features
class ModernGame(Game):
    """Modern presentation of the game with responsive layouts and dynamic themes."""

    def __init__(self):
        self.themes = [LIGHT_THEME, DARK_THEME, LIQUID_GLASS_THEME]
        self.theme_index = 0
        self.pending_theme_index = None
        self.theme = self.themes[self.theme_index]
        self.window_width = WIDTH
        self.window_height = HEIGHT
        self.layout: Dict[str, pygame.Rect] = {}
        self.instruction_text = "Match the trains starting from the left!"
        self.motivation_quote = "Stay fluid and focused?�the right color keeps the cargo on track."
        self.timeline_entries: List[Dict[str, object]] = []
        self.timeline_content_height = 0
        self.scroll_offset = 0
        self.selected_train_index = 0
        self.transitioning = False
        self.transition_alpha = 0
        self.track_origin_x = UI_PADDING * 2
        self.selection_origin_x = UI_PADDING * 2
        self.track_y = int(self.window_height * 0.35)
        self.selection_y = int(self.window_height * 0.72)
        self.selection_spacing = TRAIN_SPACING
        self.dark_mode = False  # Legacy toggle for night elements
        self.recalculate_layout(self.window_width, self.window_height)
        super().__init__()

        self.theme_button = ModernButton(
            self.layout['theme_button'].x,
            self.layout['theme_button'].y,
            self.layout['theme_button'].width,
            self.layout['theme_button'].height,
            self.next_theme_label(),
            self.theme['button'],
            self.theme,
            self.sound_manager
        )
        self.create_modern_buttons()

        self.hud_font = pygame.font.Font(FONT_PATH, 32)
        self.quote_font = pygame.font.Font(FONT_PATH, 24)
        self.timeline_font = pygame.font.Font(FONT_PATH, 24)
        self.instruction_font = pygame.font.Font(FONT_PATH, 30)

        self.recalculate_layout(self.window_width, self.window_height)
        self.refresh_button_palette()

        self.trees = [Tree(random.randint(50, self.window_width - 50), self.window_height - 100) for _ in range(TREE_COUNT)]
        self.clouds = [Cloud(random.randint(0, self.window_width), random.randint(*CLOUD_HEIGHT_RANGE)) for _ in range(CLOUD_COUNT)]
        self.stars = [Star(random.randint(0, self.window_width), random.randint(0, self.window_height // 2)) for _ in range(STAR_COUNT)]
        self.generate_structures()

        try:
            self.parallax_layers = [
                ParallaxLayer(
                    os.path.join(IMAGES_DIR, "cloud_layer.png"),
                    CONFIG["parallax"]["cloud_speed"],
                    CONFIG["parallax"]["cloud_offset_y"]
                ),
                ParallaxLayer(
                    os.path.join(IMAGES_DIR, "tree_layer.png"),
                    CONFIG["parallax"]["tree_speed"],
                    CONFIG["parallax"]["tree_offset_y"]
                )
            ]
        except KeyError as e:
            print(f"Warning: Missing parallax configuration: {e}")
            self.parallax_layers = []

    def create_buttons(self):
        """Override base button creation to use the modern components."""
        # Buttons are created after initialization in create_modern_buttons.
        pass

    def recalculate_layout(self, width: int, height: int) -> None:
        width = max(width, MIN_WINDOW_WIDTH)
        height = max(height, MIN_WINDOW_HEIGHT)
        self.window_width = width
        self.window_height = height

        max_trains = getattr(self, 'max_trains', CONFIG['game']['initial_max_trains'])
        spacing_min = CONFIG['train']['width'] + 40
        available_track_width = max(width - UI_PADDING * 4, spacing_min)
        self.train_spacing = max(spacing_min, available_track_width // max(1, max_trains))
        self.track_origin_x = UI_PADDING * 2
        self.track_y = int(height * 0.35)

        self.selection_y = int(height * 0.72)
        self.selection_spacing = max(spacing_min, int(width * 0.18))
        total_selection_span = self.selection_spacing * (len(TRAIN_COLORS) - 1)
        self.selection_origin_x = int(width // 2 - total_selection_span / 2 - CONFIG['train']['width'] / 2)

        hud_width = max(400, int(width * 0.32))
        hud_height = max(240, int(height * 0.4))
        hud_rect = pygame.Rect(
            width - hud_width - UI_PADDING,
            UI_PADDING,
            hud_width,
            min(hud_height, height - UI_PADDING * 2 - 120)
        )
        instruction_width = min(int(width * 0.6), width - UI_PADDING * 2)
        instruction_rect = pygame.Rect(
            width // 2 - instruction_width // 2,
            height - 90,
            instruction_width,
            70
        )

        theme_button_width = 120
        theme_button_height = 44
        button_offset = 16
        theme_button_left = max(UI_PADDING, hud_rect.left - theme_button_width - button_offset)
        theme_button_rect = pygame.Rect(
            theme_button_left,
            hud_rect.top + button_offset,
            theme_button_width,
            theme_button_height
        )
        mute_x = theme_button_rect.left + (theme_button_rect.width - MUTE_BUTTON_SIZE) // 2
        mute_rect = pygame.Rect(
            mute_x,
            theme_button_rect.bottom + 10,
            MUTE_BUTTON_SIZE,
            MUTE_BUTTON_SIZE
        )

        menu_panel_width = min(int(width * 0.6), width - UI_PADDING * 2)
        menu_panel_rect = pygame.Rect(
            width // 2 - menu_panel_width // 2,
            int(height * 0.18),
            menu_panel_width,
            int(height * 0.5)
        )
        button_width = min(360, max(260, int(menu_panel_rect.width * 0.65)))
        button_height = 60
        start_rect = pygame.Rect(
            width // 2 - button_width // 2,
            menu_panel_rect.bottom - button_height * 2 - 30,
            button_width,
            button_height
        )
        quit_rect = pygame.Rect(
            start_rect.x,
            start_rect.bottom + 20,
            button_width,
            button_height
        )
        play_again_rect = pygame.Rect(start_rect)

        stats_lines = self._build_stats_lines()
        wrap_width = max(220, hud_rect.width - 40)
        if hasattr(self, 'instruction_font'):
            self.instruction_lines = wrap_text(
                self.instruction_text,
                self.instruction_font,
                max(120, instruction_rect.width - 40)
            )
        else:
            self.instruction_lines = [self.instruction_text]

        if hasattr(self, 'quote_font'):
            menu_wrap_width = max(220, menu_panel_rect.width - 80)
            hud_quote_wrap = min(240, max(200, hud_rect.width - 200))
            self.menu_quote_lines = wrap_text(self.motivation_quote, self.quote_font, menu_wrap_width)
            self.default_hud_quote_lines = wrap_text(self.motivation_quote, self.quote_font, hud_quote_wrap)
        else:
            self.menu_quote_lines = [self.motivation_quote]
            self.default_hud_quote_lines = [self.motivation_quote]

        heading_top = hud_rect.top + 16
        available_width = hud_rect.width - 40
        column_gap = 24
        timeline_min_width = 120
        text_padding = 8
        stats_width = 0
        if hasattr(self, 'timeline_font'):
            stats_width = max((self.timeline_font.size(line)[0] for line in stats_lines), default=0)
        quote_width = 0
        if hasattr(self, 'quote_font') and self.default_hud_quote_lines:
            quote_width = max((self.quote_font.size(line)[0] for line in self.default_hud_quote_lines), default=0)
        heading_width = self.hud_font.size("Mission Stats")[0] if hasattr(self, 'hud_font') else 0
        base_stats_width = max(stats_width, quote_width, heading_width)
        desired_stats_width = max(200, base_stats_width + text_padding)
        can_two_column = available_width >= timeline_min_width + column_gap + desired_stats_width

        if can_two_column:
            stats_column_width = min(desired_stats_width, available_width - timeline_min_width - column_gap)
            timeline_width = available_width - stats_column_width - column_gap
            timeline_height = max(120, hud_rect.height - 32)
            stats_left = hud_rect.left + 20
            stats_right = stats_left + stats_column_width
            timeline_left = max(stats_right + column_gap, hud_rect.right - 20 - timeline_width)
            timeline_right_limit = hud_rect.right - 20
            timeline_width = min(timeline_width, max(timeline_min_width, timeline_right_limit - timeline_left))
            timeline_rect = pygame.Rect(
                timeline_left,
                heading_top,
                timeline_width,
                timeline_height
            )
            if timeline_rect.width < timeline_min_width:
                can_two_column = False
            else:
                if timeline_rect.bottom > hud_rect.bottom - 16:
                    timeline_rect.height = max(96, hud_rect.bottom - 16 - timeline_rect.top)
                self.layout['scroll_rect'] = timeline_rect
                if hasattr(self, 'timeline_font'):
                    self.timeline_wrap_width = max(120, timeline_rect.width - 32)
        if not can_two_column:
            scroll_rect = self._compute_scroll_rect(hud_rect, stats_lines, self.default_hud_quote_lines)
            self.layout['scroll_rect'] = scroll_rect
            if hasattr(self, 'timeline_font'):
                self.timeline_wrap_width = max(120, scroll_rect.width - 32)

        self.layout['hud_two_column'] = can_two_column

        self.layout['hud_rect'] = hud_rect
        self.layout['instruction_rect'] = instruction_rect
        self.layout['theme_button'] = theme_button_rect
        self.layout['mute_button'] = mute_rect
        self.layout['menu_panel'] = menu_panel_rect
        self.layout['start_button'] = start_rect
        self.layout['quit_button'] = quit_rect
        self.layout['play_again_button'] = play_again_rect

        if hasattr(self, 'mute_button'):
            self.mute_button.rect = pygame.Rect(mute_rect)
            self.mute_button.set_colors(self.theme['button'], self.theme['text'])

        if hasattr(self, 'theme_button'):
            self.theme_button.apply_layout(
                theme_button_rect.x,
                theme_button_rect.y,
                theme_button_rect.width,
                theme_button_rect.height
            )

        if hasattr(self, 'start_button'):
            self.update_button_layout()

        if hasattr(self, 'track_trains'):
            for index, train in enumerate(self.track_trains):
                train.x = self.track_origin_x + index * self.train_spacing
                train.y = self.track_y
                train.bounds_width = self.window_width
        if hasattr(self, 'selection_trains'):
            for index, train in enumerate(self.selection_trains):
                train.x = self.selection_origin_x + index * self.selection_spacing
                train.y = self.selection_y
                train.bounds_width = self.window_width


        if hasattr(self, 'buildings'):
            self.update_structures_layout()

    def update_button_layout(self) -> None:
        start_rect = self.layout['start_button']
        quit_rect = self.layout['quit_button']
        play_again_rect = self.layout['play_again_button']
        self.start_button.apply_layout(start_rect.x, start_rect.y, start_rect.width, start_rect.height)
        self.quit_button.apply_layout(quit_rect.x, quit_rect.y, quit_rect.width, quit_rect.height)
        self.play_again_button.apply_layout(play_again_rect.x, play_again_rect.y, play_again_rect.width, play_again_rect.height)

    def refresh_button_palette(self) -> None:
        self.start_button.set_color(self.theme['primary'])
        self.start_button.apply_theme(self.theme)
        self.quit_button.set_color(self.theme['error'])
        self.quit_button.apply_theme(self.theme)
        self.play_again_button.set_color(self.theme['primary'])
        self.play_again_button.apply_theme(self.theme)
        self.theme_button.set_color(self.theme['button'])
        self.theme_button.apply_theme(self.theme)
        self.theme_button.text = self.next_theme_label()
        if hasattr(self, 'mute_button'):
            self.mute_button.set_colors(self.theme['button'], self.theme['text'])
            self.update_mute_button_label()

    def update_mute_button_label(self) -> None:
        if hasattr(self, 'mute_button'):
            self.mute_button.text = MUTE_BUTTON_LABEL_OFF if self.sound_manager.muted else MUTE_BUTTON_LABEL_ON

    def generate_structures(self) -> None:
        self.buildings = []
        if BUILDING_COUNT > 0:
            slot_size = 1.0 / BUILDING_COUNT
            for index in range(BUILDING_COUNT):
                width_ratio = random.uniform(0.06, 0.11)
                height_ratio = random.uniform(0.22, 0.34)
                center_ratio = index * slot_size + random.uniform(0.2, 0.8) * slot_size
                center_ratio = max(0.05, min(0.95, center_ratio))
                self.buildings.append(Building(width_ratio, height_ratio, center_ratio))

        self.houses = []
        if HOUSE_COUNT > 0:
            slot_size = 1.0 / HOUSE_COUNT
            for index in range(HOUSE_COUNT):
                width_ratio = random.uniform(0.05, 0.09)
                height_ratio = random.uniform(0.14, 0.2)
                center_ratio = index * slot_size + random.uniform(0.2, 0.8) * slot_size
                center_ratio = max(0.05, min(0.95, center_ratio))
                self.houses.append(House(width_ratio, height_ratio, center_ratio))

        self.update_structures_layout()

    def update_structures_layout(self) -> None:
        if not hasattr(self, 'buildings'):
            return

        skyline_upper_bound = self.track_y - 50
        skyline_target = int(self.track_y - self.window_height * 0.18)
        if skyline_upper_bound <= 40:
            skyline_base = max(20, skyline_upper_bound)
        else:
            skyline_base = max(40, min(skyline_target, skyline_upper_bound))

        suburb_target = int(self.track_y - self.window_height * 0.08)
        suburb_upper_bound = self.track_y - 20
        suburb_base = min(suburb_target, suburb_upper_bound)
        suburb_base = max(skyline_base + 36, suburb_base)
        if suburb_base <= skyline_base:
            suburb_base = skyline_base + 24

        for building in self.buildings:
            building.reposition(self.window_width, self.window_height, skyline_base)

        for house in getattr(self, 'houses', []):
            house.reposition(self.window_width, self.window_height, suburb_base)

    def _build_stats_lines(self) -> List[str]:
        score = getattr(self, 'score', 0)
        high_score = getattr(self, 'high_score', 0)
        current_index = getattr(self, 'current_train_index', 0)
        track_trains = getattr(self, 'track_trains', [])
        remaining = max(0, len(track_trains) - current_index)
        level = getattr(self, 'level', 1)
        correct = getattr(self, 'correct_matches', 0)
        incorrect = getattr(self, 'incorrect_matches', 0)
        accuracy = calculate_accuracy(correct, correct + incorrect)
        combo = getattr(self, 'combo_count', 0)
        best_combo = getattr(self, 'max_combo', 0)
        return [
            f"Score: {score}",
            f"High Score: {high_score}",
            f"Remaining: {remaining}",
            f"Level: {level}",
            f"Accuracy: {accuracy:.0f}%",
            f"Combo: x{combo} (Best x{best_combo})"
        ]

    def _compute_scroll_rect(self, hud_rect: pygame.Rect, stats_lines: List[str], quote_lines: List[str]) -> pygame.Rect:
        heading_height = self.hud_font.get_linesize() if hasattr(self, 'hud_font') else UI_LINE_HEIGHT
        stats_line_height = self.timeline_font.get_linesize() if hasattr(self, 'timeline_font') else UI_LINE_HEIGHT
        quote_line_height = self.quote_font.get_linesize() if hasattr(self, 'quote_font') else int(UI_LINE_HEIGHT * 0.9)
        content_top = hud_rect.top + 16 + heading_height + 16
        content_top += len(stats_lines) * stats_line_height
        if quote_lines:
            content_top += 12 + len(quote_lines) * quote_line_height
        timeline_top = content_top + 12
        inner_padding = 16
        min_height = max(96, stats_line_height * 4)
        available_height = hud_rect.bottom - inner_padding - timeline_top
        if available_height < min_height:
            timeline_top = max(hud_rect.top + heading_height + 32, hud_rect.bottom - inner_padding - min_height)
            available_height = hud_rect.bottom - inner_padding - timeline_top
        scroll_height = max(min_height, available_height)
        scroll_width = max(80, hud_rect.width - inner_padding * 2)
        return pygame.Rect(
            hud_rect.left + inner_padding,
            timeline_top,
            scroll_width,
            scroll_height
        )

    def next_theme_label(self) -> str:
        return self.themes[(self.theme_index + 1) % len(self.themes)]['name']

    @property
    def uses_night_sky(self) -> bool:
        return bool(self.theme.get('night_mode', False))

    def create_modern_buttons(self):
        start_rect = self.layout['start_button']
        quit_rect = self.layout['quit_button']
        play_again_rect = self.layout['play_again_button']
        self.start_button = ModernButton(start_rect.x, start_rect.y, start_rect.width, start_rect.height, "Start Game", self.theme['primary'], self.theme, self.sound_manager)
        self.quit_button = ModernButton(quit_rect.x, quit_rect.y, quit_rect.width, quit_rect.height, "Quit", self.theme['error'], self.theme, self.sound_manager)
        self.play_again_button = ModernButton(play_again_rect.x, play_again_rect.y, play_again_rect.width, play_again_rect.height, "Play Again", self.theme['primary'], self.theme, self.sound_manager)

    def initialize_trains(self):
        self.track_trains = []
        for index in range(self.max_trains):
            color = random.choice(TRAIN_COLORS)
            x = self.track_origin_x + index * self.train_spacing
            train = Train(x, self.track_y, color)
            train.speed = self.train_speed
            train.bounds_width = self.window_width
            self.track_trains.append(train)

        self.selection_trains = []
        for index, color in enumerate(TRAIN_COLORS):
            x = self.selection_origin_x + index * self.selection_spacing
            train = Train(x, self.selection_y, color)
            train.bounds_width = self.window_width
            self.selection_trains.append(train)

    def add_message(self, text, color, duration=1.0):
        super().add_message(text, color, duration)
        self.timeline_entries.append({
            'time': pygame.time.get_ticks(),
            'text': text,
            'color': tuple(color)
        })
        self.timeline_entries = self.timeline_entries[-16:]
        self.scroll_offset = self.timeline_content_height + 100

    def handle_keyboard_input(self, event):
        if self.state == PLAYING:
            if event.key == pygame.K_LEFT:
                self.selected_train_index = (self.selected_train_index - 1) % len(self.selection_trains)
            elif event.key == pygame.K_RIGHT:
                self.selected_train_index = (self.selected_train_index + 1) % len(self.selection_trains)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.match_train()

    def match_train(self):
        if self.current_train_index < len(self.track_trains):
            selected_train = self.selection_trains[self.selected_train_index]
            current_train = self.track_trains[self.current_train_index]
            if selected_train.color == current_train.color:
                self.sound_manager.play('correct')
                self.create_explosion(current_train.x, current_train.y, current_train.color)
                current_train.moving = True
                current_train.move_direction = "left"
                current_train.speed = self.train_speed
                self.score += 1
                self.add_message("Correct!", self.theme['secondary'])
                self.current_train_index += 1
                self.combo_count += 1
                self.correct_matches += 1
                self.max_combo = max(self.max_combo, self.combo_count)
                self.update_combo_message()
                self.sound_manager.play('item_pickup')
                if self.current_train_index >= len(self.track_trains):
                    self.all_trains_moving = True
            else:
                self.sound_manager.play('wrong')
                self.add_message("Wrong Color!", self.theme['error'])
                self.combo_count = 0
                self.combo_message = None
                self.incorrect_matches += 1
        else:
            self.add_message("No more trains to match!", self.theme['accent'], 0.5)

    def start_transition(self):
        self.transitioning = True
        self.transition_alpha = 0

    def toggle_theme(self):
        self.pending_theme_index = (self.theme_index + 1) % len(self.themes)
        self.start_transition()

    def create_background(self):
        self.background = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        gradient = self.theme.get('background_gradient')
        if gradient:
            draw_vertical_gradient(self.background, gradient[0], gradient[1])
        else:
            self.background.fill(self.theme['background'])

        rail_color = self.theme.get('rail_color', self.theme['text'])
        for x in range(self.track_origin_x - 20, self.window_width, 40):
            pygame.draw.rect(self.background, self.theme['track'], (x, self.track_y + 30, 20, 20), border_radius=4)

        pygame.draw.line(self.background, rail_color, (0, self.track_y + 25), (self.window_width, self.track_y + 25), 5)
        pygame.draw.line(self.background, rail_color, (0, self.track_y + 55), (self.window_width, self.track_y + 55), 5)

    def draw_menu(self, screen):
        screen.blit(self.background, (0, 0))
        if self.uses_night_sky:
            for star in self.stars:
                star.draw(screen)
        for layer in self.parallax_layers:
            layer.draw(screen)
        for building in getattr(self, 'buildings', []):
            building.draw(screen, self.uses_night_sky)
        for house in getattr(self, 'houses', []):
            house.draw(screen, self.uses_night_sky)
        for tree in self.trees:
            tree.draw(screen)
        for cloud in self.clouds:
            cloud.draw(screen)

        menu_panel = self.layout['menu_panel']
        draw_glass_panel(screen, menu_panel, self.theme)

        title_font = pygame.font.Font(FONT_PATH, 64)
        title_surface = title_font.render("Train Color Matcher", True, self.theme['text'])
        title_rect = title_surface.get_rect(center=(menu_panel.centerx, menu_panel.top + 80))
        screen.blit(title_surface, title_rect)

        quote_y = title_rect.bottom + 20
        for line in self.menu_quote_lines:
            line_surface = self.quote_font.render(line, True, self.theme['secondary'])
            screen.blit(line_surface, (menu_panel.left + 40, quote_y))
            quote_y += self.quote_font.get_linesize()

        self.start_button.draw(screen)
        self.quit_button.draw(screen)
        self.theme_button.draw(screen)
        self.mute_button.draw(screen)

        version_font = pygame.font.Font(FONT_PATH, 18)
        version_surface = version_font.render("v1.1 | Built by dundd - Feb 2025", True, self.theme['text'])
        screen.blit(version_surface, (UI_PADDING, self.window_height - UI_PADDING - version_surface.get_height()))

    def draw_game(self, screen):
        screen.blit(self.background, (0, 0))
        if self.uses_night_sky:
            for star in self.stars:
                star.draw(screen)
        for layer in self.parallax_layers:
            layer.draw(screen)
        for building in getattr(self, 'buildings', []):
            building.draw(screen, self.uses_night_sky)
        for house in getattr(self, 'houses', []):
            house.draw(screen, self.uses_night_sky)
        for tree in self.trees:
            tree.draw(screen)
        for cloud in self.clouds:
            cloud.draw(screen)

        for train in self.track_trains:
            train.draw(screen, self.uses_night_sky)
        for train in self.selection_trains:
            train.draw(screen, self.uses_night_sky)

        selection_train = self.selection_trains[self.selected_train_index]
        highlight_rect = pygame.Rect(selection_train.x - 8, selection_train.y - 8, selection_train.width + 16, selection_train.height + 16)
        pygame.draw.rect(screen, self.theme['accent'], highlight_rect, width=3, border_radius=10)

        for message in self.messages:
            message.draw(screen)

        self.draw_hud(screen)
        self.draw_instruction_panel(screen)

        self.mute_button.draw(screen)
        self.theme_button.draw(screen)

        if self.combo_message:
            self.combo_message.draw(screen)

        if self.transitioning:
            target_theme = self.themes[self.pending_theme_index] if self.pending_theme_index is not None else self.theme
            overlay_color = target_theme.get('background')
            gradient = target_theme.get('background_gradient')
            if gradient:
                overlay_color = gradient[0]
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((*overlay_color, 255))
            overlay.set_alpha(min(255, int(self.transition_alpha)))
            screen.blit(overlay, (0, 0))

    def draw_game_over(self, screen):
        self.draw_game(screen)
        panel = self.layout['menu_panel']
        draw_glass_panel(screen, panel, self.theme)

        font = pygame.font.Font(FONT_PATH, 48)
        game_over_surface = font.render("Game Over!", True, self.theme['text'])
        screen.blit(game_over_surface, game_over_surface.get_rect(center=(panel.centerx, panel.top + 70)))

        score_lines = [
            f"Final Score: {self.score}",
            f"Accuracy: {calculate_accuracy(self.correct_matches, self.correct_matches + self.incorrect_matches):.0f}%",
            f"Best Combo: x{self.max_combo}"
        ]
        stat_y = panel.top + 140
        for line in score_lines:
            stat_surface = self.timeline_font.render(line, True, self.theme['text'])
            screen.blit(stat_surface, (panel.left + 40, stat_y))
            stat_y += self.timeline_font.get_linesize() + 4

        self.play_again_button.draw(screen)
        self.quit_button.draw(screen)

    def draw_hud(self, screen):
        hud_rect = self.layout['hud_rect']
        draw_glass_panel(screen, hud_rect, self.theme)

        stats_lines = self._build_stats_lines()
        stats_font = self.timeline_font
        heading_surface = self.hud_font.render("Mission Stats", True, self.theme['text'])
        heading_y = hud_rect.top + 16

        quote_lines = list(self.quote_lines) if getattr(self, 'quote_lines', None) else []

        text_padding = 8
        stats_width = max((stats_font.size(line)[0] for line in stats_lines), default=0)
        quote_width = max((self.quote_font.size(line)[0] for line in quote_lines), default=0) if quote_lines else 0
        heading_width = heading_surface.get_width()
        base_text_width = max(stats_width, quote_width, heading_width)
        text_column_width = base_text_width + text_padding

        available_width = hud_rect.width - 40
        timeline_min_width = 180
        column_gap = 24
        two_column = available_width >= timeline_min_width + column_gap + text_column_width

        timeline_rect = None
        if two_column:
            timeline_width = max(timeline_min_width, available_width - column_gap - text_column_width)
            timeline_height = max(120, hud_rect.height - 32)
            text_left = hud_rect.left + 20
            text_right = text_left + text_column_width
            timeline_right_limit = hud_rect.right - 20
            timeline_left = max(text_right + column_gap, timeline_right_limit - timeline_width)
            timeline_width = max(timeline_min_width, timeline_right_limit - timeline_left)
            if timeline_width < timeline_min_width:
                two_column = False
            else:
                timeline_rect = pygame.Rect(timeline_left, heading_y, timeline_width, timeline_height)
                if timeline_rect.bottom > hud_rect.bottom - 16:
                    timeline_rect.height = max(96, hud_rect.bottom - 16 - timeline_rect.top)
                self.layout['scroll_rect'] = timeline_rect
                if hasattr(self, 'timeline_font'):
                    self.timeline_wrap_width = max(120, timeline_rect.width - 32)

        if not two_column:
            timeline_rect = self._compute_scroll_rect(hud_rect, stats_lines, quote_lines)
            self.layout['scroll_rect'] = timeline_rect
            if hasattr(self, 'timeline_font'):
                self.timeline_wrap_width = max(120, timeline_rect.width - 32)

        heading_pos = (hud_rect.left + 20, heading_y)
        screen.blit(heading_surface, heading_pos)

        y = heading_pos[1] + heading_surface.get_height() + 16
        for line in stats_lines:
            line_surface = stats_font.render(line, True, self.theme['text'])
            screen.blit(line_surface, (heading_pos[0], y))
            y += stats_font.get_linesize()

        if quote_lines:
            y += 12
            for line in quote_lines:
                quote_surface = self.quote_font.render(line, True, self.theme['secondary'])
                screen.blit(quote_surface, (heading_pos[0], y))
                y += self.quote_font.get_linesize()

        self.layout['hud_two_column'] = two_column

        self.draw_timeline(screen)

    def draw_timeline(self, screen):
        scroll_rect = self.layout['scroll_rect']
        draw_glass_panel(screen, scroll_rect, self.theme)
        line_height = self.timeline_font.get_linesize()
        wrap_width = getattr(self, 'timeline_wrap_width', scroll_rect.width - 32)

        cached_lines = []
        total_height = 0
        for entry in self.timeline_entries:
            lines = wrap_text(entry['text'], self.timeline_font, wrap_width)
            cached_lines.append((entry, lines))
            total_height += len(lines) * line_height + 10

        self.timeline_content_height = total_height
        max_offset = max(0, total_height - scroll_rect.height + 16)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))

        clip_rect = scroll_rect.inflate(-12, -12)
        screen.set_clip(clip_rect)
        y = clip_rect.top - self.scroll_offset
        base_time = cached_lines[0][0]['time'] if cached_lines else 0
        for entry, lines in cached_lines:
            timestamp = (entry['time'] - base_time) / 1000.0
            time_surface = self.timeline_font.render(f"{timestamp:>5.1f}s", True, self.theme['accent'])
            screen.blit(time_surface, (clip_rect.left, y))
            y += line_height
            for line in lines:
                line_surface = self.timeline_font.render(line, True, entry['color'])
                screen.blit(line_surface, (clip_rect.left, y))
                y += line_height
            y += 6
        screen.set_clip(None)

    def draw_instruction_panel(self, screen):
        instruction_rect = self.layout['instruction_rect']
        draw_glass_panel(screen, instruction_rect, self.theme)
        if not self.instruction_lines:
            self.instruction_lines = [self.instruction_text]
        line_height = self.instruction_font.get_linesize()
        total_height = len(self.instruction_lines) * line_height
        start_y = instruction_rect.centery - total_height // 2
        for idx, line in enumerate(self.instruction_lines):
            line_surface = self.instruction_font.render(line, True, self.theme['text'])
            screen.blit(line_surface, (instruction_rect.left + 20, start_y + idx * line_height))

    def handle_click(self, pos):
        if self.mute_button.is_clicked(pos):
            self.sound_manager.muted = not self.sound_manager.muted
            self.update_mute_button_label()
            return True

        if self.theme_button.is_clicked(pos):
            self.toggle_theme()
            self.sound_manager.play('click')
            return True

        if self.state == MENU:
            if self.start_button.is_clicked(pos):
                self.start_button.create_particles()
                self.sound_manager.play('click')
                self.state = PLAYING
                self.reset_game()
            elif self.quit_button.is_clicked(pos):
                return False

        elif self.state == PLAYING:
            clicked = False
            for index, selection_train in enumerate(self.selection_trains):
                if selection_train.x <= pos[0] <= selection_train.x + selection_train.width and selection_train.y <= pos[1] <= selection_train.y + selection_train.height:
                    clicked = True
                    self.selected_train_index = index
                    self.match_train()
                    break
            if not clicked:
                self.add_message("Please click on a train!", self.theme['accent'], 0.5)

        elif self.state == GAME_OVER:
            if self.play_again_button.is_clicked(pos):
                self.sound_manager.play('click')
                self.state = PLAYING
                self.reset_game()
            elif self.quit_button.is_clicked(pos):
                return False
        return True

    def update(self, dt: float) -> None:
        Game.update(self)
        for cloud in self.clouds:
            cloud.update(dt)
        for button in [self.start_button, self.quit_button, self.play_again_button, self.theme_button]:
            button.update(dt)
        if self.transitioning:
            self.transition_alpha += TRANSITION_SPEED * dt
            if self.transition_alpha >= 255:
                self.complete_transition()

    def complete_transition(self):
        if self.pending_theme_index is None:
            self.transitioning = False
            self.transition_alpha = 0
            return
        self.theme_index = self.pending_theme_index
        self.pending_theme_index = None
        self.theme = self.themes[self.theme_index]
        self.dark_mode = self.uses_night_sky
        self.refresh_button_palette()
        self.recalculate_layout(self.window_width, self.window_height)
        self.create_background()
        self.transitioning = False
        self.transition_alpha = 0

    def handle_resize(self, width: int, height: int) -> None:
        old_width = getattr(self, 'window_width', width)
        old_height = getattr(self, 'window_height', height)
        self.recalculate_layout(width, height)
        self.background = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.create_background()
        for layer in self.parallax_layers:
            if hasattr(layer, 'image'):
                layer.y = self.window_height - layer.image.get_height() + getattr(layer, 'offset_y', 0)
        if old_width and old_height:
            ratio_x = self.window_width / max(old_width, 1)
            ratio_y = self.window_height / max(old_height, 1)
            for tree in self.trees:
                tree.x = int(tree.x * ratio_x)
                tree.y = self.window_height - 100
            for cloud in self.clouds:
                cloud.x = cloud.x * ratio_x
                cloud.y = min(self.window_height - 50, max(0, cloud.y * ratio_y))
            if self.uses_night_sky:
                for star in self.stars:
                    star.x = int(star.x * ratio_x)
                    star.y = int(star.y * ratio_y)

        self.update_structures_layout()

    def handle_scroll(self, amount: int) -> None:
        max_offset = max(0, self.timeline_content_height - self.layout['scroll_rect'].height + 16)
        self.scroll_offset = max(0, min(self.scroll_offset - amount * 24, max_offset))

    def level_up(self):
        super().level_up()
        self.recalculate_layout(self.window_width, self.window_height)
        self.create_background()

# Combo message class for displaying combo messages
class ComboMessage(Message):
    # Initializes a combo message
    def __init__(self, text, color, duration=1.0, font_size=48):
        super().__init__(text, color, duration)  # Call superclass constructor
        try:
            self.font = pygame.font.Font(FONT_PATH, font_size)  # Set font
        except:
            print(f"Warning: Could not load font {FONT_PATH}, using system default")  # Print warning if font is not found
            self.font = pygame.font.Font(None, font_size)  # Use default font
        self.start_time = pygame.time.get_ticks()  # Set start time
        self.initial_font_size = font_size  # Set initial font size
        self.scale = 1.0  # Set scale
        surface = pygame.display.get_surface()
        width = surface.get_width() if surface else WIDTH
        height = surface.get_height() if surface else HEIGHT
        self.position = (width // 2, height // 3)  # Set position
        self.color = color  # Set color

    # Updates the combo message
    def update(self, dt):
        current_time = pygame.time.get_ticks()  # Get current time
        age = (current_time - self.start_time) / 1000.0  # Calculate age
        
        self.scale = 1.0 + 0.2 * abs(math.sin(age * 10))  # Update scale
        
        self.alpha = max(0, 255 * (1.0 - age / self.duration))  # Update alpha

    # Draws the combo message
    def draw(self, screen):
        if self.alpha > 0:  # If alpha is greater than 0
            base_surface = self.font.render(self.text, True, self.color)  # Render text
            scaled_size = (int(base_surface.get_width() * self.scale),
                         int(base_surface.get_height() * self.scale))  # Calculate scaled size
            
            scaled_surface = pygame.transform.scale(base_surface, scaled_size)  # Scale surface
            scaled_surface.set_alpha(self.alpha)  # Set alpha
            
            pos = (self.position[0] - scaled_size[0]//2,
                  self.position[1] - scaled_size[1]//2)  # Calculate position
            
            screen.blit(scaled_surface, pos)  # Blit surface

# Main function to run the game
def main():
    global WIDTH, HEIGHT
    pygame.init()  # Initialize Pygame
    game = ModernGame()  # Create game instance
    clock = pygame.time.Clock()  # Create clock
    screen = set_window_mode((WIDTH, HEIGHT))  # Create display
    pygame.display.set_caption(WINDOW_TITLE)  # Set window title
    
    running = True  # Set running state
    while running:
        dt = clock.tick(FRAMERATE) / 1000.0  # Calculate delta time
        
        for event in pygame.event.get():  # Handle events
            if event.type == pygame.QUIT:  # If quit event
                running = False
            elif event.type == pygame.VIDEORESIZE:
                new_width = max(event.w, MIN_WINDOW_WIDTH)
                new_height = max(event.h, MIN_WINDOW_HEIGHT)
                screen = set_window_mode((new_width, new_height))
                game.handle_resize(new_width, new_height)
                WIDTH, HEIGHT = new_width, new_height
            elif event.type == pygame.MOUSEBUTTONDOWN:  # If mouse button down event
                if not game.handle_click(event.pos):  # Handle click
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                game.handle_scroll(event.y)
            elif event.type == pygame.MOUSEMOTION:  # If mouse motion event
                hover_targets = [game.theme_button, game.start_button, game.quit_button, game.play_again_button]
                for button in hover_targets:
                    button.handle_hover(event.pos)  # Handle hover
            elif event.type == pygame.KEYDOWN:  # If key down event
                game.handle_keyboard_input(event)  # Handle keyboard input
        
        game.update(dt)  # Update game
        game.draw(screen)  # Draw game
        pygame.display.flip()  # Flip display

# Run the game
if __name__ == '__main__':
    try:
        main()  # Run main function
    except Exception as e:
        print(f"Error occurred: {e}")  # Print error
    finally:
        pygame.quit()  # Quit Pygame

