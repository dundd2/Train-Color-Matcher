# By dundd2 
# Last update:Feb 2025
# Train-Color-Matcher V1.1

import json  # Used for loading configuration from JSON files
import pygame  # The main Pygame library for game development
import random  # Used for generating random numbers
import os  # Used for handling file paths
import math  # Used for mathematical operations
from typing import List, Dict, Tuple  # Used for type hinting

# Game Constants: Define fixed values used throughout the game
FRAMERATE = 60  # Frames per second for the game
MIN_WINDOW_WIDTH = 800  # Minimum window width
MIN_WINDOW_HEIGHT = 600  # Minimum window height
BUTTON_WIDTH = 200  # Standard button width
BUTTON_HEIGHT = 50  # Standard button height
MUTE_BUTTON_SIZE = 50  # Size of the mute button
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create the display
pygame.display.set_caption(WINDOW_TITLE)  # Set the window title

# Colors: Define RGB color values
RED = (255, 0, 0)  # Red color
BLUE = (0, 0, 255)  # Blue color
GREEN = (0, 255, 0)  # Green color
GRAY = (128, 128, 128)  # Gray color
YELLOW = (255, 255, 0)  # Yellow color

# Theme colors: Define color schemes for light and dark themes
LIGHT_THEME = {
    'background': (245, 245, 245),  # Light theme background color
    'primary': (66, 133, 244),  # Light theme primary color
    'secondary': (52, 168, 83),  # Light theme secondary color
    'accent': (251, 188, 4),  # Light theme accent color
    'error': (234, 67, 53),  # Light theme error color
    'text': (32, 33, 36),  # Light theme text color
    'shadow': (0, 0, 0, 50),  # Light theme shadow color
    'button': (255, 255, 255),  # Light theme button color
    'track': (200, 200, 200),  # Light theme track color
    'rail_color': (100, 100, 100)   # Light theme rail color
}

DARK_THEME = {
    'background': (30, 30, 30),  # Dark theme background color
    'primary': (138, 180, 248),  # Dark theme primary color
    'secondary': (129, 201, 149),  # Dark theme secondary color
    'accent': (253, 214, 99),  # Dark theme accent color
    'error': (242, 139, 130),  # Dark theme error color
    'text': (232, 234, 237),  # Dark theme text color
    'shadow': (0, 0, 0, 80),  # Dark theme shadow color
    'button': (70, 70, 70),  # Dark theme button color
    'track': (70, 70, 70),  # Dark theme track color
    'rail_color': (200, 200, 200)   # Dark theme rail color
}

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
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)  # Create a rectangle
        self.text = text  # Text
        self.color = color  # Color
        self.font = pygame.font.Font(FONT_PATH, 36)  # Font

    # Draws the button
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)  # Draw the rectangle
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Draw the border
        text_surface = self.font.render(self.text, True, BLACK)  # Render the text
        text_rect = text_surface.get_rect(center=self.rect.center)  # Get the text rectangle
        screen.blit(text_surface, text_rect)  # Blit the text to the screen

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
        self.smoke_particles = []  # Smoke particles
        self.renderer = TrainRenderer(self)  # Train renderer

    # Draws the train
    def draw(self, screen, is_dark_mode=False):
        self.renderer.draw(screen, is_dark_mode)  # Draw the train

    # Moves the train
    def move(self):
        if self.moving:  # If the train is moving
            if self.move_direction == "left":  # If the train is moving left
                self.x -= 5  # Move left
            elif self.move_direction == "right":  # If the train is moving right
                self.x += 5  # Move right

            self.emit_smoke()  # Emit smoke

            for particle in self.smoke_particles:  # Update the smoke particles
                particle.update(0.1)  # Update the particle

            self.smoke_particles = [p for p in self.smoke_particles if p.lifetime > 0]  # Remove dead particles

            if self.x + self.width < 0 or self.x > WIDTH:  # If the train is out of bounds
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
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))  # Get the text rectangle
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
        self.state = MENU  # Set the initial state to MENU
        self.reset_game()  # Reset the game
        self.create_buttons()  # Create buttons
        self.high_score = 0  # Initialize high score
        self.sound_manager = SoundManager()  # Initialize sound manager
        self.messages = []  # Initialize messages
        self.mute_button = Button(WIDTH - 60, 10, 50, 50, "🔊", WHITE)  # Create mute button
        self.background = pygame.Surface((WIDTH, HEIGHT))  # Create background surface
        self.create_background()  # Create background
        self.current_train_index = 0  # Initialize current train index
        self.explosion_particles = []  # Initialize explosion particles
        self.level = 1  # Initialize level
        self.level_up_threshold = CONFIG['game']['level_up_threshold']  # Set level up threshold
        self.train_speed = CONFIG['game']['initial_train_speed']  # Set initial train speed
        self.max_trains = CONFIG['game']['initial_max_trains']  # Set initial max trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # Set train positions
        self.font = pygame.font.Font(FONT_PATH, 36)  # Set font
        self.parallax_layers = [
            ParallaxLayer(os.path.join(IMAGES_DIR, "cloud_layer.png"), 10),
            ParallaxLayer(os.path.join(IMAGES_DIR, "tree_layer.png"), 30)
        ]
        self.combo_count = 0  # Initialize combo count
        self.combo_message = None  # Initialize combo message

    # Creates the background
    def create_background(self):
        self.background.fill(self.theme['background'])  # Fill the background
        for x in range(0, WIDTH, 30):  # Draw the track
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 235), (WIDTH, 235), 5)  # Draw the rails
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 265), (WIDTH, 265), 5)

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
        self.train_speed = 5  # Initialize train speed
        self.max_trains = 10  # Initialize max trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # Set train positions
        self.initialize_trains()  # Initialize trains
        self.last_time = pygame.time.get_ticks()  # Set last time
        self.combo_count = 0  # Initialize combo count
        self.combo_message = None  # Initialize combo message

    # Creates buttons
    def create_buttons(self):
        self.start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game", self.theme['primary'])  # Create start button
        self.quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Quit", self.theme['error'])  # Create quit button
        self.play_again_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Play Again", self.theme['primary'])  # Create play again button

    # Initializes trains
    def initialize_trains(self):
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # Set train positions
        self.track_trains = []  # Initialize track trains
        for i in range(self.max_trains):  # Create track trains
            color = random.choice(TRAIN_COLORS)  # Choose a random color
            x = self.train_positions[i]  # Set X position
            self.track_trains.append(Train(x, 200, color))  # Add train

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
        
        screen.blit(progress_text, (10, 10))  # Blit progress text
        screen.blit(score_text, (10, 40))  # Blit score text
        screen.blit(level_text, (10, 70))  # Blit level text
        
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
        
        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//4))  # Blit game over text
        screen.blit(score_text, (WIDTH//2 - 150, HEIGHT//3))  # Blit score text
        
        self.play_again_button.draw(screen)  # Draw play again button

    # Handles click events
    def handle_click(self, pos):
        if self.mute_button.is_clicked(pos):  # If the mute button is clicked
            self.sound_manager.muted = not self.sound_manager.muted  # Toggle mute state
            self.mute_button.text = "🔊" if not self.sound_manager.muted else "🔈"  # Update mute button text
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
                    selection_train.y < pos[1] < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    
                    if self.current_train_index < len(self.track_trains):  # If there are remaining track trains
                        current_train = self.track_trains[self.current_train_index]
                        
                        if selection_train.color == current_train.color:  # If the colors match
                            self.sound_manager.play('correct')  # Play correct sound
                            self.create_explosion(current_train.x, current_train.y, current_train.color)  # Create explosion
                            current_train.moving = True  # Set train to moving
                            current_train.move_direction = "left"  # Set move direction to left
                            self.score += 1  # Increment score
                            self.add_message("Correct!", self.theme['secondary'])  # Add correct message
                            self.current_train_index += 1  # Increment current train index
                            self.combo_count += 1  # Increment combo count
                            self.update_combo_message()  # Update combo message
                            self.sound_manager.play('item_pickup')  # Play item pickup sound
                            if self.current_train_index >= len(self.track_trains):  # If all track trains are matched
                                self.all_trains_moving = True  # Set all trains moving state to True
                        else:
                            self.sound_manager.play('wrong')  # Play wrong sound
                            self.add_message("Wrong Color!", self.theme['error'])  # Add wrong color message
                            self.combo_count = 0  # Reset combo count
                            self.combo_message = None  # Reset combo message
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
        self.max_trains += 2  # Increment max trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # Set train positions
        self.initialize_trains()  # Initialize trains
        self.sound_manager.play('victory')  # Play victory sound
        self.max_trains = min(self.max_trains, 15)  # Cap max trains

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
        if self.x > WIDTH:  # If the cloud is out of bounds
            self.x = -100  # Reset X position

    # Draws the cloud
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 20)  # Draw the first segment
        pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 10), 25)  # Draw the second segment
        pygame.draw.circle(screen, WHITE, (self.x + 40, self.y), 20)  # Draw the third segment

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

# Modern game class with additional features
class ModernGame(Game):
    # Initializes the modern game
    def __init__(self):
        self.theme = LIGHT_THEME  # Set theme to light theme
        super().__init__()  # Call superclass constructor
        self.dark_mode = False  # Set dark mode to False
        self.theme = LIGHT_THEME  # Set theme to light theme
        self.transition_alpha = 255  # Set transition alpha
        self.particles = []  # Initialize particles
        self.create_modern_buttons()  # Create modern buttons
        self.theme_button = ModernButton(WIDTH - 100, 10, 80, 40, "DARK", self.theme['button'], self.theme, self.sound_manager)  # Create theme button
        self.all_trains_moving = False  # Set all trains moving state to False
        self.instruction_text = "Match the trains starting from the left!"  # Set instruction text
        self.instruction_font = pygame.font.Font(FONT_PATH, 36)  # Set instruction font
        self.trees = [Tree(random.randint(50, WIDTH - 50), HEIGHT - 100) for _ in range(TREE_COUNT)]  # Create trees
        self.clouds = [Cloud(random.randint(0, WIDTH), random.randint(*CLOUD_HEIGHT_RANGE)) for _ in range(CLOUD_COUNT)]  # Create clouds
        self.stars = [Star(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)) for _ in range(STAR_COUNT)]  # Create stars
        self.transitioning = False  # Set transitioning state to False
        self.transition_alpha = 0  # Set transition alpha
        self.selected_train_index = 0  # Set selected train index
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

    # Handles keyboard input
    def handle_keyboard_input(self, event):
        if self.state == PLAYING:  # If the state is PLAYING
            if event.key == pygame.K_LEFT:  # If the left arrow key is pressed
                self.selected_train_index = (self.selected_train_index - 1) % len(self.selection_trains)  # Decrement selected train index
            elif event.key == pygame.K_RIGHT:  # If the right arrow key is pressed
                self.selected_train_index = (self.selected_train_index + 1) % len(self.selection_trains)  # Increment selected train index
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:  # If the space or enter key is pressed
                self.match_train()  # Match train

    # Matches the selected train with the current track train
    def match_train(self):
        if self.current_train_index < len(self.track_trains):  # If there are remaining track trains
            selected_train = self.selection_trains[self.selected_train_index]  # Get selected train
            current_train = self.track_trains[self.current_train_index]  # Get current track train

            if selected_train.color == current_train.color:  # If the colors match
                self.sound_manager.play('correct')  # Play correct sound
                current_train.moving = True  # Set train to moving
                current_train.move_direction = "left"  # Set move direction to left
                self.score += 1  # Increment score
                self.add_message("Correct!", self.theme['secondary'])  # Add correct message
                self.current_train_index += 1  # Increment current train index

                if self.current_train_index >= len(self.track_trains):  # If all track trains are matched
                    self.all_trains_moving = True  # Set all trains moving state to True
            else:
                self.sound_manager.play('wrong')  # Play wrong sound
                self.add_message("Wrong Color!", self.theme['error'])  # Add wrong color message
        else:
            self.add_message("No more trains to match!", self.theme['accent'], 0.5)  # Add no more trains message

    # Starts the theme transition
    def start_transition(self):
        self.transitioning = True  # Set transitioning state to True
        self.transition_alpha = 0  # Set transition alpha

    # Toggles the theme
    def toggle_theme(self):
        self.start_transition()  # Start transition

    # Creates the background
    def create_background(self):
        self.background.fill(self.theme['background'])  # Fill the background
        for x in range(0, WIDTH, 30):  # Draw the track
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['text'], (0, 235), (WIDTH, 235), 5)  # Draw the rails
        pygame.draw.line(self.background, self.theme['text'], (0, 265), (WIDTH, 265), 5)

    # Draws the game
    def draw_game(self, screen):
        screen.blit(self.background, (0, 0))  # Blit background
        
        if self.dark_mode:  # If dark mode is enabled
            for star in self.stars:  # Draw stars
                star.draw(screen)

        for tree in self.trees:  # Draw trees
            tree.draw(screen)

        for cloud in self.clouds:  # Draw clouds
            cloud.draw(screen)
        
        for train in self.track_trains + self.selection_trains:  # Draw trains
            train.draw(screen, self.dark_mode)

        selection_train = self.selection_trains[self.selected_train_index]  # Get selected train
        pygame.draw.rect(screen, YELLOW, (selection_train.x - 5, selection_train.y - 5,
                                            selection_train.width + 10, selection_train.height + 10), 3)  # Draw selection rectangle

        for message in self.messages:  # Draw messages
            message.draw(screen)

        font = pygame.font.Font(None, 36)  # Set font
        
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])  # Render score text
        remaining_trains = len(self.track_trains) - self.current_train_index  # Calculate remaining trains
        progress_text = font.render(f'Remaining: {remaining_trains}', True, self.theme['text'])  # Render progress text
        high_score_text = font.render(f'High Score: {self.high_score}', True, self.theme['text'])  # Render high score text
        
        screen.blit(score_text, (20, 20))  # Blit score text
        screen.blit(progress_text, (20, 60))  # Blit progress text
        screen.blit(high_score_text, (20, 100))  # Blit high score text
        
        instruction_surface = self.instruction_font.render(
            self.instruction_text, True, self.theme['text'])  # Render instruction text
        instruction_bg = pygame.Surface((instruction_surface.get_width() + 20, 40))  # Create instruction background
        instruction_bg.fill(self.theme['button'])  # Fill instruction background
        instruction_bg.set_alpha(200)  # Set instruction background alpha
        screen.blit(instruction_bg, 
                   (WIDTH//2 - instruction_bg.get_width()//2, HEIGHT - 60))  # Blit instruction background
        screen.blit(instruction_surface, 
                   (WIDTH//2 - instruction_surface.get_width()//2, HEIGHT - 50))  # Blit instruction text
        
        self.mute_button.draw(screen)  # Draw mute button
        self.theme_button.draw(screen)  # Draw theme button

        if self.transitioning:  # If transitioning
            transition_surface = pygame.Surface((WIDTH, HEIGHT))  # Create transition surface
            transition_surface.fill(self.theme['background'])  # Fill transition surface
            transition_surface.set_alpha(self.transition_alpha)  # Set transition surface alpha
            screen.blit(transition_surface, (0, 0))  # Blit transition surface

    # Handles click events
    def handle_click(self, pos):
        if self.theme_button.is_clicked(pos):  # If the theme button is clicked
            self.toggle_theme()  # Toggle theme
            self.sound_manager.play('click')  # Play click sound
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
            for i, selection_train in enumerate(self.selection_trains):  # Check if a selection train is clicked
                if (selection_train.x < pos[0] < selection_train.x + selection_train.width and
                    selection_train.y < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    self.selected_train_index = i  # Set selected train index
                    self.match_train()  # Match train
                    break
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
    def update(self, dt: float) -> None:
        super().update()  # Call superclass update method
        for cloud in self.clouds:  # Update clouds
            cloud.update(dt)

        for button in [self.start_button, self.quit_button, self.play_again_button, self.theme_button]:  # Update buttons
            button.update(dt)

        if self.transitioning:  # If transitioning
            self.transition_alpha += TRANSITION_SPEED * dt  # Update transition alpha
            if self.transition_alpha >= 255:  # If transition is complete
                self.complete_transition()  # Complete transition

        for train in self.track_trains:  # Update track trains
            train.move()

        for message in self.messages:  # Update messages
            message.update(dt)
        self.messages = [msg for msg in self.messages if not msg.should_remove()]  # Remove old messages

    # Creates modern buttons
    def create_modern_buttons(self):
        self.start_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50,
            "Start Game", self.theme['primary'], self.theme, self.sound_manager
        )
        self.quit_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50,
            "Quit", self.theme['error'], self.theme, self.sound_manager
        )
        self.play_again_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50,
            "Play Again", self.theme['primary'], self.theme, self.sound_manager
        )

    def complete_transition(self):
        """Completes the theme transition by switching themes and resetting transition state."""
        self.dark_mode = not self.dark_mode
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.theme_button.text = "LIGHT" if self.dark_mode else "DARK"
        self.theme_button.color = self.theme['button']
        self.create_background()
        self.transitioning = False
        self.transition_alpha = 0

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
        self.position = (WIDTH//2, HEIGHT//3)  # Set position
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
    pygame.init()  # Initialize Pygame
    game = ModernGame()  # Create game instance
    clock = pygame.time.Clock()  # Create clock
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create display
    pygame.display.set_caption(WINDOW_TITLE)  # Set window title
    
    running = True  # Set running state
    while running:
        dt = clock.tick(FRAMERATE) / 1000.0  # Calculate delta time
        
        for event in pygame.event.get():  # Handle events
            if event.type == pygame.QUIT:  # If quit event
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:  # If mouse button down event
                if not game.handle_click(event.pos):  # Handle click
                    running = False
            elif event.type == pygame.MOUSEMOTION:  # If mouse motion event
                for button in [game.theme_button, game.start_button, 
                             game.quit_button, game.play_again_button]:
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
