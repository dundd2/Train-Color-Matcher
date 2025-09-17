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

# Initialize audio mixer before the rest of Pygame bootstraps to avoid stutter
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
except pygame.error as error:
    print(f"Warning: Unable to pre-initialize audio mixer: {error}")

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
PURPLE = (155, 89, 182)  # Purple color
ORANGE = (255, 140, 0)  # Orange color
CYAN = (0, 188, 212)  # Cyan color

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

# Color identifiers used for accessibility overlays
COLOR_IDENTIFIERS = {
    RED: {"label": "R", "symbol": "⬤"},
    BLUE: {"label": "B", "symbol": "■"},
    GREEN: {"label": "G", "symbol": "▲"},
    YELLOW: {"label": "Y", "symbol": "★"},
    PURPLE: {"label": "P", "symbol": "◆"},
    ORANGE: {"label": "O", "symbol": "⬟"},
    CYAN: {"label": "C", "symbol": "✦"},
}

# Train colors: Define the global pool of available train colors
TRAIN_COLORS = list(COLOR_IDENTIFIERS.keys())

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Simple word-wrapping helper for rendering multi-line strings."""
    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    current_line = words[0]
    for word in words[1:]:
        test_line = f"{current_line} {word}"
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# Multilingual text catalog for UI and feedback messages
LANGUAGE_PACKS = {
    "en": {
        "title": "Train Color Matcher",
        "start": "Start Game",
        "quit": "Quit",
        "play_again": "Play Again",
        "settings": "Settings",
        "mode": "Mode",
        "mode_campaign": "Campaign",
        "mode_endless": "Endless",
        "mode_switch_warning": "Switched to {mode} mode. Routes have been reset.",
        "language": "Language",
        "color_mode": "Color Icons",
        "color_mode_on": "Symbols On",
        "color_mode_off": "Symbols Off",
        "difficulty": "Difficulty",
        "difficulty_standard": "Standard",
        "difficulty_relaxed": "Relaxed",
        "difficulty_expert": "Expert",
        "instruction_base": "Match the trains starting from the left!",
        "message_correct": "Correct!",
        "message_wrong": "Wrong Color!",
        "message_click_train": "Please click on a train!",
        "message_no_trains": "No more trains to match!",
        "score": "Score",
        "remaining": "Remaining",
        "mistakes": "Mistakes",
        "level_label": "Level",
        "high_score": "High Score",
        "new_level": "Level {level} - {name}",
        "game_over": "Game Over!",
        "final_score": "Final Score: {score}",
        "reason_victory": "Amazing! You completed every route!",
        "reason_mistakes": "The station closed after too many mix-ups.",
        "reason_quit": "Come back soon for more rail puzzles!",
        "level_rookie": "Rookie Rails",
        "level_rookie_desc": "Match the primary engines to depart the station.",
        "level_sunset": "Sunset Shuffle",
        "level_sunset_desc": "Yellow coaches join the rush hour lineup!",
        "level_twilight": "Twilight Tracks",
        "level_twilight_desc": "Purple night trains tighten the timing.",
        "level_aurora": "Aurora Express",
        "level_aurora_desc": "Every color sprints across dazzling rails.",
        "level_blizzard": "Blizzard Belt",
        "level_blizzard_desc": "Snow squalls veil the rails. Follow the glows carefully.",
        "level_mirage": "Mirage Metro",
        "level_mirage_desc": "Signals surge in waves—stay alert for rapid departures.",
        "level_endless": "Endless Stage {stage}",
        "level_endless_desc": "Infinite dispatch! Each wave crowds the platform with faster trains.",
        "settings_title": "Game Settings",
        "language_cycle": "Switch Language",
        "difficulty_cycle": "Toggle Difficulty",
        "symbols_cycle": "Toggle Symbols",
        "mode_cycle": "Toggle Mode",
        "victory_banner": "All routes cleared!",
        "mistake_recovered": "Signal restored! Mistake forgiven.",
        "modifiers_title": "Route Conditions",
        "modifier_dense_fog": "Track Fog",
        "modifier_dense_fog_desc": "Low-lying fog obscures engines as they depart.",
        "modifier_express_signals": "Express Signals",
        "modifier_express_signals_desc": "Dispatch surges periodically accelerate outgoing trains.",
        "combo_meter_label": "Signal Bonus",
        "zen_mode": "Zen Mode",
        "zen_mode_on": "Zen On",
        "zen_mode_off": "Zen Off",
        "zen_hint": "Relaxed play with limitless retries.",
        "zen_reminder": "Zen active — enjoy the ride!",
        "express_start": "Express signals! Departures speed up!",
        "express_end": "Signals stable. Pace returning to normal.",
    },
    "es": {
        "title": "Emparejador de Trenes",
        "start": "Comenzar",
        "quit": "Salir",
        "play_again": "Jugar de Nuevo",
        "settings": "Configuración",
        "mode": "Modo",
        "mode_campaign": "Campaña",
        "mode_endless": "Infinito",
        "mode_switch_warning": "Modo cambiado a {mode}. Las rutas se reinician.",
        "language": "Idioma",
        "color_mode": "Iconos de Color",
        "color_mode_on": "Símbolos Activados",
        "color_mode_off": "Símbolos Desactivados",
        "difficulty": "Dificultad",
        "difficulty_standard": "Normal",
        "difficulty_relaxed": "Relajado",
        "difficulty_expert": "Experto",
        "instruction_base": "¡Empareja los trenes comenzando desde la izquierda!",
        "message_correct": "¡Correcto!",
        "message_wrong": "¡Color incorrecto!",
        "message_click_train": "¡Haz clic en un tren!",
        "message_no_trains": "¡No quedan trenes!",
        "score": "Puntuación",
        "remaining": "Restantes",
        "mistakes": "Errores",
        "level_label": "Nivel",
        "high_score": "Récord",
        "new_level": "Nivel {level} - {name}",
        "game_over": "¡Fin del Juego!",
        "final_score": "Puntuación Final: {score}",
        "reason_victory": "¡Increíble! ¡Completaste todas las rutas!",
        "reason_mistakes": "La estación cerró tras demasiados errores.",
        "reason_quit": "¡Vuelve pronto para más rompecabezas!",
        "level_rookie": "Rieles Novatos",
        "level_rookie_desc": "Empareja los trenes primarios para salir de la estación.",
        "level_sunset": "Mezcla del Atardecer",
        "level_sunset_desc": "¡Los coches amarillos se unen a la hora pico!",
        "level_twilight": "Vías del Crepúsculo",
        "level_twilight_desc": "Los trenes morados nocturnos ajustan el ritmo.",
        "level_aurora": "Expreso Aurora",
        "level_aurora_desc": "Cada color corre por rieles brillantes.",
        "level_blizzard": "Corredor Nevado",
        "level_blizzard_desc": "Las ventiscas cubren los rieles. Sigue los destellos con cuidado.",
        "level_mirage": "Metro Espejismo",
        "level_mirage_desc": "Las señales suben en oleadas: ¡atento a las salidas rápidas!",
        "level_endless": "Etapa Infinita {stage}",
        "level_endless_desc": "¡Despacho infinito! Cada oleada llena el andén con trenes más veloces.",
        "settings_title": "Configuración del Juego",
        "language_cycle": "Cambiar Idioma",
        "difficulty_cycle": "Cambiar Dificultad",
        "symbols_cycle": "Alternar Símbolos",
        "mode_cycle": "Cambiar Modo",
        "victory_banner": "¡Todas las rutas completas!",
        "mistake_recovered": "¡Señal restablecida! Error perdonado.",
        "modifiers_title": "Condiciones de Ruta",
        "modifier_dense_fog": "Niebla en la Vía",
        "modifier_dense_fog_desc": "La niebla baja oculta las locomotoras al partir.",
        "modifier_express_signals": "Señales Exprés",
        "modifier_express_signals_desc": "Los despachos en oleadas aceleran los trenes periódicamente.",
        "combo_meter_label": "Bono de Señal",
        "zen_mode": "Modo Zen",
        "zen_mode_on": "Zen Activado",
        "zen_mode_off": "Zen Desactivado",
        "zen_hint": "Juego relajado con intentos infinitos.",
        "zen_reminder": "Modo Zen activo: ¡disfruta del viaje!",
        "express_start": "¡Señales exprés! ¡Las salidas se aceleran!",
        "express_end": "Señales estables. El ritmo vuelve a la normalidad.",
    },
    "fr": {
        "title": "Match des Trains",
        "start": "Jouer",
        "quit": "Quitter",
        "play_again": "Rejouer",
        "settings": "Options",
        "mode": "Mode",
        "mode_campaign": "Campagne",
        "mode_endless": "Infini",
        "mode_switch_warning": "Mode changé pour {mode}. Les parcours sont réinitialisés.",
        "language": "Langue",
        "color_mode": "Symboles",
        "color_mode_on": "Symboles Activés",
        "color_mode_off": "Symboles Désactivés",
        "difficulty": "Difficulté",
        "difficulty_standard": "Classique",
        "difficulty_relaxed": "Détendu",
        "difficulty_expert": "Expert",
        "instruction_base": "Associez les trains en partant de la gauche !",
        "message_correct": "Bravo !",
        "message_wrong": "Mauvaise couleur !",
        "message_click_train": "Cliquez sur un train !",
        "message_no_trains": "Plus de trains à associer !",
        "score": "Score",
        "remaining": "Restants",
        "mistakes": "Erreurs",
        "level_label": "Niveau",
        "high_score": "Record",
        "new_level": "Niveau {level} - {name}",
        "game_over": "Fin de Partie !",
        "final_score": "Score Final : {score}",
        "reason_victory": "Superbe ! Toutes les voies sont terminées !",
        "reason_mistakes": "La gare ferme après trop d'erreurs.",
        "reason_quit": "Revenez bientôt pour d'autres défis !",
        "level_rookie": "Rails Débutants",
        "level_rookie_desc": "Associez les locomotives primaires pour démarrer.",
        "level_sunset": "Mélodie du Crépuscule",
        "level_sunset_desc": "Les wagons jaunes rejoignent l'heure de pointe !",
        "level_twilight": "Voies du Soir",
        "level_twilight_desc": "Les trains violets nocturnes resserrent le rythme.",
        "level_aurora": "Express Aurore",
        "level_aurora_desc": "Chaque couleur file sur des rails scintillants.",
        "level_blizzard": "Couloir Blizzard",
        "level_blizzard_desc": "Les rafales de neige voilent les rails. Suivez bien les lueurs.",
        "level_mirage": "Métro Mirage",
        "level_mirage_desc": "Les signaux montent en vagues—restez alerte aux départs rapides.",
        "level_endless": "Étape Infinie {stage}",
        "level_endless_desc": "Départs sans fin ! Chaque vague accélère la cadence.",
        "settings_title": "Paramètres du Jeu",
        "language_cycle": "Changer de Langue",
        "difficulty_cycle": "Changer la Difficulté",
        "symbols_cycle": "Basculer les Symboles",
        "mode_cycle": "Changer de Mode",
        "victory_banner": "Toutes les voies dégagées !",
        "mistake_recovered": "Signal rétabli ! Faute annulée.",
        "modifiers_title": "Conditions de Ligne",
        "modifier_dense_fog": "Brouillard sur les Voies",
        "modifier_dense_fog_desc": "Un brouillard bas dissimule les locomotives au départ.",
        "modifier_express_signals": "Signaux Express",
        "modifier_express_signals_desc": "Des poussées d'envoi accélèrent les trains périodiquement.",
        "combo_meter_label": "Bonus de Signal",
        "zen_mode": "Mode Zen",
        "zen_mode_on": "Zen Activé",
        "zen_mode_off": "Zen Désactivé",
        "zen_hint": "Partie détendue avec essais illimités.",
        "zen_reminder": "Mode Zen actif — profitez du trajet !",
        "express_start": "Signaux express ! Les départs s'accélèrent !",
        "express_end": "Signaux stables. Le rythme redevient normal.",
    },
    "de": {
        "title": "Zugfarbenspiel",
        "start": "Spiel Starten",
        "quit": "Beenden",
        "play_again": "Nochmal",
        "settings": "Einstellungen",
        "mode": "Modus",
        "mode_campaign": "Kampagne",
        "mode_endless": "Endlos",
        "mode_switch_warning": "Modus auf {mode} gewechselt. Fahrten werden zurückgesetzt.",
        "language": "Sprache",
        "color_mode": "Farbsymbole",
        "color_mode_on": "Symbole An",
        "color_mode_off": "Symbole Aus",
        "difficulty": "Schwierigkeit",
        "difficulty_standard": "Standard",
        "difficulty_relaxed": "Entspannt",
        "difficulty_expert": "Experte",
        "instruction_base": "Ordne die Züge von links beginnend zu!",
        "message_correct": "Richtig!",
        "message_wrong": "Falsche Farbe!",
        "message_click_train": "Bitte einen Zug anklicken!",
        "message_no_trains": "Keine Züge mehr zum Zuordnen!",
        "score": "Punkte",
        "remaining": "Verbleibend",
        "mistakes": "Fehler",
        "level_label": "Stufe",
        "high_score": "Rekord",
        "new_level": "Stufe {level} - {name}",
        "game_over": "Spiel Vorbei!",
        "final_score": "Endstand: {score}",
        "reason_victory": "Großartig! Alle Strecken abgeschlossen!",
        "reason_mistakes": "Zu viele Verwechslungen im Bahnhof.",
        "reason_quit": "Bis bald für mehr Rätsel!",
        "level_rookie": "Neulingsgleise",
        "level_rookie_desc": "Bringe die Grundfarben richtig auf die Reise.",
        "level_sunset": "Abendexpress",
        "level_sunset_desc": "Gelbe Wagen mischen sich in die Rushhour!",
        "level_twilight": "Dämmerungstrassen",
        "level_twilight_desc": "Violette Nachtzüge erhöhen das Tempo.",
        "level_aurora": "Aurora-Express",
        "level_aurora_desc": "Alle Farben rasen über funkelnde Schienen.",
        "level_blizzard": "Blizzard-Strecke",
        "level_blizzard_desc": "Schneestürme verhüllen die Gleise. Folge den Lichtern genau.",
        "level_mirage": "Mirage-Metro",
        "level_mirage_desc": "Signale kommen in Wellen – bleib wachsam bei schnellen Abfahrten.",
        "level_endless": "Endlos-Stufe {stage}",
        "level_endless_desc": "Endlose Abfahrten! Jede Welle wird schneller und dichter.",
        "settings_title": "Spieleinstellungen",
        "language_cycle": "Sprache wechseln",
        "difficulty_cycle": "Schwierigkeit ändern",
        "symbols_cycle": "Symbole umschalten",
        "mode_cycle": "Modus wechseln",
        "victory_banner": "Alle Strecken frei!",
        "mistake_recovered": "Signal wieder grün! Fehler verziehen.",
        "modifiers_title": "Streckenzustand",
        "modifier_dense_fog": "Gleisnebel",
        "modifier_dense_fog_desc": "Tiefer Nebel verbirgt abfahrende Lokomotiven.",
        "modifier_express_signals": "Express-Signale",
        "modifier_express_signals_desc": "Schubweise Freigaben beschleunigen die Züge regelmäßig.",
        "combo_meter_label": "Signalbonus",
        "zen_mode": "Zen-Modus",
        "zen_mode_on": "Zen Aktiv",
        "zen_mode_off": "Zen Aus",
        "zen_hint": "Entspannter Modus mit unbegrenzten Versuchen.",
        "zen_reminder": "Zen-Modus aktiv – genieße die Fahrt!",
        "express_start": "Express-Signale! Die Abfahrten werden schneller!",
        "express_end": "Signale stabil. Das Tempo beruhigt sich.",
    }
}

DEFAULT_LANGUAGE = "en"


class LanguageManager:
    """Simple helper for retrieving localized UI strings."""

    def __init__(self, language_code: str = DEFAULT_LANGUAGE):
        self.language_code = language_code if language_code in LANGUAGE_PACKS else DEFAULT_LANGUAGE

    def set_language(self, language_code: str) -> None:
        if language_code in LANGUAGE_PACKS:
            self.language_code = language_code

    def cycle_language(self) -> None:
        codes = list(LANGUAGE_PACKS.keys())
        current_index = codes.index(self.language_code)
        self.language_code = codes[(current_index + 1) % len(codes)]

    def get_text(self, key: str, **kwargs) -> str:
        base = LANGUAGE_PACKS.get(self.language_code, {})
        fallback = LANGUAGE_PACKS[DEFAULT_LANGUAGE]
        template = base.get(key, fallback.get(key, key))
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template

    def get_language_label(self) -> str:
        names = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
        }
        return names.get(self.language_code, self.language_code)

    def get_available_languages(self):
        return list(LANGUAGE_PACKS.keys())


LEVEL_CONFIGS = [
    {
        "name_key": "level_rookie",
        "description_key": "level_rookie_desc",
        "colors": [RED, BLUE, GREEN],
        "train_speed": 5,
        "max_trains": 8,
        "spacing": 90,
        "mistakes_allowed": 3,
        "modifiers": [],
    },
    {
        "name_key": "level_sunset",
        "description_key": "level_sunset_desc",
        "colors": [RED, BLUE, GREEN, YELLOW],
        "train_speed": 6,
        "max_trains": 10,
        "spacing": 85,
        "mistakes_allowed": 3,
        "modifiers": [],
    },
    {
        "name_key": "level_twilight",
        "description_key": "level_twilight_desc",
        "colors": [RED, BLUE, GREEN, YELLOW, PURPLE],
        "train_speed": 7,
        "max_trains": 12,
        "spacing": 80,
        "mistakes_allowed": 2,
        "modifiers": ["express_signals"],
    },
    {
        "name_key": "level_aurora",
        "description_key": "level_aurora_desc",
        "colors": [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, CYAN],
        "train_speed": 8,
        "max_trains": 14,
        "spacing": 75,
        "mistakes_allowed": 2,
        "modifiers": ["express_signals"],
    },
    {
        "name_key": "level_blizzard",
        "description_key": "level_blizzard_desc",
        "colors": [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, CYAN],
        "train_speed": 8.5,
        "max_trains": 15,
        "spacing": 72,
        "mistakes_allowed": 2,
        "modifiers": ["dense_fog"],
    },
    {
        "name_key": "level_mirage",
        "description_key": "level_mirage_desc",
        "colors": [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, CYAN],
        "train_speed": 9,
        "max_trains": 16,
        "spacing": 68,
        "mistakes_allowed": 1,
        "modifiers": ["express_signals", "dense_fog"],
    },
]

MODIFIER_DEFINITIONS = {
    "dense_fog": {
        "name_key": "modifier_dense_fog",
        "description_key": "modifier_dense_fog_desc",
    },
    "express_signals": {
        "name_key": "modifier_express_signals",
        "description_key": "modifier_express_signals_desc",
    },
}

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
    """Centralised audio hub for both sound effects and background music."""

    def __init__(self):
        self.available = True
        self.muted = False
        self.sfx_volume = 0.7
        self.music_volume = 0.45
        self.current_music: str | None = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_volumes: Dict[str, float] = {}
        self.music_tracks: Dict[str, str] = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error as error:
            print(f"Warning: Audio disabled: {error}")
            self.available = False
            return

        self._load_assets()

    def _load_assets(self) -> None:
        """Load sound effects and register music tracks."""

        def load_sound(key: str, filename: str, base_volume: float = 1.0) -> None:
            if not self.available:
                return
            path = os.path.join(SOUNDS_DIR, filename)
            if not os.path.exists(path):
                print(f"Warning: Missing sound effect '{filename}'")
                return
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[key] = sound
                self.sound_volumes[key] = base_volume
                sound.set_volume(0 if self.muted else base_volume * self.sfx_volume)
            except pygame.error as error:
                print(f"Warning: Failed to load sound '{filename}': {error}")

        def register_music(key: str, filename: str) -> None:
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                self.music_tracks[key] = path
            else:
                print(f"Warning: Missing music track '{filename}'")

        load_sound('correct', 'General_sound_effect.mp3')
        load_sound('wrong', 'Suspenseful Music.mp3', 0.8)
        load_sound('click', 'Button sounds.mp3', 0.6)
        load_sound('button_hover', 'UI opening sounds.mp3', 0.5)
        load_sound('level_up', 'MC Level Up.mp3', 0.7)
        load_sound('victory', 'Victory Music.mp3', 0.7)
        load_sound('item_pickup', 'Item Pickup.mp3', 0.65)
        load_sound('confirmation', 'Confirmation Sounds (in UI).mp3', 0.6)
        load_sound('game_over_sting', 'Cutscene Music.mp3', 0.8)
        load_sound('recovery', 'Recovery sound .mp3', 0.7)

        register_music('menu', 'Menu Music.mp3')
        register_music('campaign', 'Shop_MusicMerchant_T.mp3')
        register_music('endless', 'Boss Battle .mp3')
        register_music('game_over', 'Cutscene Music.mp3')
        register_music('victory_theme', 'Victory Music.mp3')

    def play(self, sound_name: str) -> None:
        if not self.available or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if sound is None:
            return
        try:
            base_volume = self.sound_volumes.get(sound_name, 1.0)
            sound.set_volume(base_volume * self.sfx_volume)
            sound.play()
        except pygame.error:
            pass

    def play_music(self, track_name: str, loop: bool = True, fade_ms: int = 500) -> None:
        if not self.available:
            return
        path = self.music_tracks.get(track_name)
        if path is None:
            return
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self.current_music = track_name
        except pygame.error as error:
            print(f"Warning: Unable to play music '{track_name}': {error}")

    def stop_music(self, fade_ms: int = 300) -> None:
        if not self.available:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            pass
        self.current_music = None

    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._refresh_sfx_volumes()

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.available:
            return
        pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)

    def _refresh_sfx_volumes(self) -> None:
        if not self.available:
            return
        for key, sound in self.sounds.items():
            base_volume = self.sound_volumes.get(key, 1.0)
            sound.set_volume(0 if self.muted else base_volume * self.sfx_volume)

    def toggle_mute(self) -> None:
        if not self.available:
            self.muted = True
            return
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)
        self._refresh_sfx_volumes()

    def is_music_playing(self, track_name: str) -> bool:
        return self.available and self.current_music == track_name and pygame.mixer.music.get_busy()

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
    def draw(self, screen, is_dark_mode: bool = False, show_identifier: bool = False):
        pygame.draw.rect(
            screen,
            self.train.color,
            (
                self.train.x,
                self.train.y,
                CONFIG["train"]["width"],
                CONFIG["train"]["height"],
            ),
            border_radius=5,
        )  # Draw the train body

        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (self.train.x + 10, self.train.y - 10, 10, 10),
        )  # Draw the train chimney

        window_color = (255, 255, 200) if is_dark_mode else (200, 200, 200)  # Window color
        if is_dark_mode:  # If dark mode is enabled
            for window_x in [self.train.x + 25, self.train.x + 45]:  # For each window
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)  # Create a surface for the glow
                pygame.draw.circle(glow_surf, (255, 255, 0, 100), (10, 10), 8)  # Draw the glow
                screen.blit(glow_surf, (window_x - 5, self.train.y))  # Blit the glow to the screen

        pygame.draw.rect(
            screen, window_color, (self.train.x + 25, self.train.y + 5, 10, 10)
        )  # Draw the first window
        pygame.draw.rect(
            screen, window_color, (self.train.x + 45, self.train.y + 5, 10, 10)
        )  # Draw the second window

        pygame.draw.circle(
            screen, BLACK, (self.train.x + 15, self.train.y + 30), 5
        )  # Draw the first wheel
        pygame.draw.circle(
            screen, BLACK, (self.train.x + 45, self.train.y + 30), 5
        )  # Draw the second wheel

        if self.train.identifier:
            try:
                font = pygame.font.Font(FONT_PATH, 26)
            except Exception:
                font = pygame.font.Font(None, 26)

            text_color = WHITE if show_identifier else (40, 40, 40)
            text_surface = font.render(self.train.identifier, True, text_color)
            text_rect = text_surface.get_rect(
                center=(
                    self.train.x + CONFIG["train"]["width"] // 2,
                    self.train.y + CONFIG["train"]["height"] // 2,
                )
            )

            if show_identifier:
                badge = pygame.Surface((text_rect.width + 12, text_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(badge, (0, 0, 0, 140), badge.get_rect(), border_radius=8)
                screen.blit(badge, (text_rect.x - 6, text_rect.y - 4))
                text_surface = font.render(self.train.identifier, True, WHITE)

            screen.blit(text_surface, text_rect)

        for particle in self.train.smoke_particles:  # Draw the smoke particles
            particle.draw(screen)

# Train class to handle train behavior
class Train:
    # Initializes a train
    def __init__(self, x, y, color, speed=5, identifier=""):
        self.x = x  # X position
        self.y = y  # Y position
        self.color = color  # Color
        self.speed = speed  # Movement speed
        self.identifier = identifier  # Identifier symbol for accessibility
        self.width = CONFIG["train"]["width"]  # Width
        self.height = CONFIG["train"]["height"]  # Height
        self.moving = False  # Moving state
        self.move_direction = "left"  # Move direction
        self.smoke_particles = []  # Smoke particles
        self.renderer = TrainRenderer(self)  # Train renderer

    # Draws the train
    def draw(self, screen, is_dark_mode: bool = False, show_identifier: bool = False):
        self.renderer.draw(screen, is_dark_mode, show_identifier)  # Draw the train

    # Moves the train
    def move(self):
        if self.moving:  # If the train is moving
            if self.move_direction == "left":  # If the train is moving left
                self.x -= self.speed  # Move left
            elif self.move_direction == "right":  # If the train is moving right
                self.x += self.speed  # Move right

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
    def __init__(self, language_manager: LanguageManager | None = None):
        self.language_manager = language_manager or LanguageManager()
        if not hasattr(self, "theme"):
            self.theme = LIGHT_THEME

        self.state = MENU  # Set the initial state to MENU
        self.high_score = 0  # Initialize campaign high score
        self.endless_high_score = 0  # Separate tracker for endless runs
        self.game_mode = 'campaign'
        self.available_modes = ['campaign', 'endless']
        self.endless_stage = 0
        self.sound_manager = SoundManager()  # Initialize sound manager
        self.messages: List['Message'] = []  # Initialize messages
        self.explosion_particles: List[ExplosionParticle] = []  # Initialize explosion particles
        self.mute_button = Button(WIDTH - 60, 10, 50, 50, "🔊", WHITE)  # Create mute button
        self.background = pygame.Surface((WIDTH, HEIGHT))  # Create background surface
        self.combo_count = 0  # Initialize combo count
        self.combo_message: 'ComboMessage' | None = None  # Initialize combo message
        self.additional_mistakes = 0  # Difficulty modifier
        self.color_blind_mode = False  # Accessibility toggle
        self.level_index = 0  # Track the active level
        self.level_intro_timer = 0  # Timer for level banner
        self.game_over_reason: str | None = None  # Store why the game ended
        self.active_modifiers: List[str] = []  # Active level modifiers
        self.modifier_display_lines: List[Tuple[str, str]] = []  # Localised modifier descriptions
        self.fog_phase = 0.0
        self.fog_offsets: List[float] = []
        self.express_timer = 0.0
        self.express_cooldown = 0.0
        self.express_elapsed = 0.0
        self.express_active = False
        self.express_announced = False
        self.speed_multiplier = 1.0
        self.base_level_mistakes = 3
        self.zen_mode = False

        self.parallax_layers = [
            ParallaxLayer(os.path.join(IMAGES_DIR, "cloud_layer.png"), 10),
            ParallaxLayer(os.path.join(IMAGES_DIR, "tree_layer.png"), 30)
        ]

        self.create_background()
        self.reset_game()  # Reset the game
        self.create_buttons()  # Create buttons

        if getattr(self.sound_manager, 'available', False):
            self.sound_manager.play_music('menu')

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

    def update_mistake_limits(self, base_value: int) -> None:
        base_value = max(1, base_value)
        self.base_level_mistakes = base_value
        if self.zen_mode:
            self.max_mistakes = 999
        else:
            self.max_mistakes = max(1, base_value + self.additional_mistakes)

    # Resets the game
    def reset_game(self):
        self.track_trains: List[Train] = []  # Initialize track trains
        self.selection_trains: List[Train] = []  # Initialize selection trains
        self.score = 0  # Initialize score
        self.mistakes = 0  # Mistakes for current level
        self.current_train_index = 0  # Initialize current train index
        self.all_trains_moving = False  # Initialize all trains moving state
        self.explosion_particles = []  # Initialize explosion particles
        self.level_index = 0  # Reset level index
        self.endless_stage = 0  # Reset endless scaling
        self.level = 1  # Human readable level number
        self.speed_multiplier = 1.0
        self.express_active = False
        self.express_announced = False
        self.express_timer = 0.0
        self.express_elapsed = 0.0
        self.fog_phase = 0.0
        self.apply_level_rules()  # Apply current level configuration
        self.initialize_trains()  # Initialize trains
        self.last_time = pygame.time.get_ticks()  # Set last time
        self.combo_count = 0  # Initialize combo count
        self.combo_message = None  # Initialize combo message
        self.game_over_reason = None
        self.level_intro_timer = 2.5  # Show intro banner for first level

        if self.state == PLAYING and getattr(self.sound_manager, 'available', False):
            track = 'campaign' if self.game_mode == 'campaign' else 'endless'
            self.sound_manager.play_music(track)

    # Creates buttons
    def create_buttons(self):
        self.start_button = Button(
            WIDTH//2 - 100,
            HEIGHT//2 - 50,
            200,
            50,
            self.language_manager.get_text("start"),
            self.theme['primary']
        )
        self.quit_button = Button(
            WIDTH//2 - 100,
            HEIGHT//2 + 50,
            200,
            50,
            self.language_manager.get_text("quit"),
            self.theme['error']
        )
        self.play_again_button = Button(
            WIDTH//2 - 100,
            HEIGHT//2 + 50,
            200,
            50,
            self.language_manager.get_text("play_again"),
            self.theme['primary']
        )

    def apply_level_rules(self):
        if self.game_mode == 'endless':
            base_index = min(self.endless_stage, len(LEVEL_CONFIGS) - 1)
            base_config = LEVEL_CONFIGS[base_index]
            self.level_config = {
                **base_config,
                "name_key": "level_endless",
                "description_key": "level_endless_desc",
                "modifiers": base_config.get("modifiers", []),
            }
            base_speed = base_config.get("train_speed", CONFIG['game']['initial_train_speed'])
            base_spacing = base_config.get("spacing", TRAIN_SPACING)
            base_max = base_config.get("max_trains", CONFIG['game']['initial_max_trains'])
            base_mistakes = base_config.get("mistakes_allowed", 3)

            self.available_colors = base_config["colors"]
            self.train_speed = base_speed + min(self.endless_stage * 0.35, 3.5)
            self.max_trains = min(base_max + self.endless_stage // 2, 18)
            self.train_spacing = max(55, base_spacing - self.endless_stage * 2)
            penalty = self.endless_stage // 3
            base_value = max(1, base_mistakes - penalty)
            self.active_modifiers = list(self.level_config.get("modifiers", []))
            if self.endless_stage >= 2 and "express_signals" not in self.active_modifiers:
                self.active_modifiers.append("express_signals")
            if self.endless_stage >= 4 and "dense_fog" not in self.active_modifiers:
                self.active_modifiers.append("dense_fog")
            self.update_mistake_limits(base_value)
        else:
            self.level_config = LEVEL_CONFIGS[self.level_index]
            self.available_colors = self.level_config["colors"]
            self.train_speed = self.level_config.get("train_speed", CONFIG['game']['initial_train_speed'])
            self.max_trains = self.level_config.get("max_trains", CONFIG['game']['initial_max_trains'])
            self.train_spacing = self.level_config.get("spacing", TRAIN_SPACING)
            base_mistakes = self.level_config.get("mistakes_allowed", 3)
            self.active_modifiers = list(self.level_config.get("modifiers", []))
            self.update_mistake_limits(base_mistakes)

        self._reset_modifier_runtime()
        self.refresh_level_texts()

    def _reset_modifier_runtime(self) -> None:
        self.active_modifiers = list(dict.fromkeys(self.active_modifiers))
        self.modifier_display_lines = []
        self.fog_phase = 0.0
        self.fog_offsets = [random.random() * math.tau for _ in range(6)]
        self.express_timer = 0.0
        self.express_elapsed = 0.0
        self.express_cooldown = random.uniform(7.0, 11.0)
        self.express_active = False
        self.express_announced = False
        self.speed_multiplier = 1.0

    def update_modifier_texts(self) -> None:
        lines: List[Tuple[str, str]] = []
        for modifier in self.active_modifiers:
            info = MODIFIER_DEFINITIONS.get(modifier)
            if not info:
                continue
            name = self.language_manager.get_text(info["name_key"])
            description = self.language_manager.get_text(info["description_key"])
            lines.append((name, description))
        self.modifier_display_lines = lines

    def _update_modifier_effects(self, dt: float) -> None:
        if "dense_fog" in self.active_modifiers:
            self.fog_phase = (self.fog_phase + dt * 0.25) % math.tau

        if "express_signals" in self.active_modifiers:
            if self.express_active:
                self.express_elapsed += dt
                if self.express_elapsed >= 3.0:
                    self.express_active = False
                    self.express_elapsed = 0.0
                    if self.express_announced:
                        self.add_message(self.language_manager.get_text("express_end"), self.theme['secondary'], 0.8)
                        self.express_announced = False
            else:
                self.express_timer += dt
                if self.express_timer >= self.express_cooldown:
                    self.express_active = True
                    self.express_timer = 0.0
                    self.express_elapsed = 0.0
                    self.express_cooldown = random.uniform(9.0, 13.0)
                    self.add_message(self.language_manager.get_text("express_start"), self.theme['accent'], 0.9)
                    self.express_announced = True

            target_multiplier = 1.45 if self.express_active else 1.0
            if self.speed_multiplier < target_multiplier:
                self.speed_multiplier = min(target_multiplier, self.speed_multiplier + dt * 1.2)
            else:
                self.speed_multiplier = max(target_multiplier, self.speed_multiplier - dt * 1.2)
        else:
            self.speed_multiplier = max(1.0, self.speed_multiplier - dt * 1.2)

    def _draw_fog_if_needed(self, screen: pygame.Surface) -> None:
        if "dense_fog" not in self.active_modifiers:
            return
        fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        lumps = max(3, len(self.fog_offsets))
        denominator = max(1, lumps - 1)
        for index, offset in enumerate(self.fog_offsets):
            wave = self.fog_phase + offset
            alpha = max(40, min(150, int(100 + 60 * math.sin(wave))))
            width = 240
            height = 130
            center_x = (index / denominator) * WIDTH + math.sin(wave * 0.7) * 80
            center_y = 190 + math.cos(wave * 0.5) * 25
            rect = pygame.Rect(int(center_x - width / 2), int(center_y - height / 2), width, height)
            pygame.draw.ellipse(fog_surface, (255, 255, 255, alpha), rect)
        screen.blit(fog_surface, (0, 0))

    def render_modifier_badges(self, screen: pygame.Surface, x: int, y: int, max_width: int) -> int:
        if not self.modifier_display_lines:
            return y
        header_font = pygame.font.Font(FONT_PATH, 22)
        detail_font = pygame.font.Font(FONT_PATH, 18)
        header_surface = header_font.render(self.language_manager.get_text("modifiers_title"), True, self.theme['text'])
        screen.blit(header_surface, (x, y))
        y += header_surface.get_height() + 6
        for name, description in self.modifier_display_lines:
            name_surface = detail_font.render(name, True, self.theme['accent'])
            screen.blit(name_surface, (x, y))
            y += name_surface.get_height() + 2
            for line in wrap_text(description, detail_font, max_width):
                desc_surface = detail_font.render(line, True, self.theme['text'])
                screen.blit(desc_surface, (x, y))
                y += desc_surface.get_height() + 2
            y += 6
        return y

    def draw_combo_meter(self, screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        label_font = pygame.font.Font(FONT_PATH, 24)
        value_font = pygame.font.Font(FONT_PATH, 18)
        label_surface = label_font.render(self.language_manager.get_text("combo_meter_label"), True, self.theme['text'])
        screen.blit(label_surface, (x, y))
        y += label_surface.get_height() + 6
        bar_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (*self.theme['button'], 200), bar_rect, border_radius=height // 2)
        progress_count = self.combo_count % 4
        if self.combo_count > 0 and progress_count == 0:
            progress_count = 4
        progress = progress_count / 4 if progress_count else 0
        if progress > 0:
            inner_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height)
            pygame.draw.rect(screen, self.theme['accent'], inner_rect, border_radius=bar_rect.height // 2)
        ratio_text = f"{progress_count}/4" if progress_count else "0/4"
        ratio_surface = value_font.render(ratio_text, True, self.theme['text'])
        screen.blit(
            ratio_surface,
            (
                bar_rect.centerx - ratio_surface.get_width() // 2,
                bar_rect.centery - ratio_surface.get_height() // 2,
            ),
        )

    def refresh_level_texts(self):
        name_kwargs = {}
        desc_kwargs = {}
        if self.level_config.get("name_key") == "level_endless":
            name_kwargs["stage"] = self.level
        if self.level_config.get("description_key") == "level_endless_desc":
            desc_kwargs["stage"] = self.level

        self.level_name = self.language_manager.get_text(self.level_config["name_key"], **name_kwargs)
        self.level_description = self.language_manager.get_text(self.level_config["description_key"], **desc_kwargs)
        self.instruction_text = self.language_manager.get_text("instruction_base")
        self.update_modifier_texts()

    def update_language(self, language_code: str | None = None) -> None:
        if language_code:
            self.language_manager.set_language(language_code)
        self.refresh_level_texts()
        if hasattr(self, 'start_button'):
            self.start_button.text = self.language_manager.get_text("start")
        if hasattr(self, 'quit_button'):
            self.quit_button.text = self.language_manager.get_text("quit")
        if hasattr(self, 'play_again_button'):
            self.play_again_button.text = self.language_manager.get_text("play_again")

    def get_current_high_score(self) -> int:
        return self.high_score if self.game_mode == 'campaign' else self.endless_high_score

    # Initializes trains
    def initialize_trains(self):
        self.train_positions = [i * self.train_spacing for i in range(self.max_trains)]  # Set train positions
        self.track_trains = []  # Initialize track trains
        for i in range(self.max_trains):  # Create track trains
            color = random.choice(self.available_colors)  # Choose a random color
            identifier = COLOR_IDENTIFIERS.get(color, {}).get("symbol", "")
            x = self.train_positions[i]  # Set X position
            self.track_trains.append(Train(x, 200, color, speed=self.train_speed, identifier=identifier))

        self.selection_trains = []  # Initialize selection trains
        selection_spacing = 120
        start_x = WIDTH//2 - ((len(self.available_colors) - 1) * selection_spacing)//2
        for i, color in enumerate(self.available_colors):  # Create selection trains
            identifier = COLOR_IDENTIFIERS.get(color, {}).get("symbol", "")
            self.selection_trains.append(Train(start_x + i * selection_spacing, 400, color, identifier=identifier))

        if self.selection_trains:
            if hasattr(self, "selected_train_index"):
                self.selected_train_index = min(self.selected_train_index, len(self.selection_trains) - 1)
            else:
                self.selected_train_index = 0
        elif hasattr(self, "selected_train_index"):
            self.selected_train_index = 0

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
        title_text = title_font.render(self.language_manager.get_text("title"), True, self.theme['text'])  # Render title text
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))  # Get title rectangle
        screen.blit(title_text, title_rect)  # Blit title text

        self.start_button.draw(screen)  # Draw start button
        self.quit_button.draw(screen)  # Draw quit button

        version_font = pygame.font.Font(FONT_PATH, 16)  # Set version font
        version_text = version_font.render("v1.4 | Zenith Update", True, self.theme['text'])  # Render version text
        version_rect = version_text.get_rect(bottomleft=(10, HEIGHT - 10))  # Get version rectangle
        screen.blit(version_text, version_rect)  # Blit version text

    # Draws the game
    def draw_game(self, screen):
        for layer in self.parallax_layers:  # Draw parallax layers
            layer.draw(screen)

        screen.blit(self.background, (0, 0))  # Blit background

        for train in self.track_trains:  # Draw track trains
            if not train.moving:
                train.draw(screen, False, self.color_blind_mode)
        self._draw_fog_if_needed(screen)
        for train in self.selection_trains:  # Draw selection trains
            train.draw(screen, False, self.color_blind_mode)

        for message in self.messages:  # Draw messages
            message.draw(screen)

        info_font = pygame.font.Font(FONT_PATH, 34)  # Set font
        small_font = pygame.font.Font(FONT_PATH, 24)

        remaining_trains = len(self.track_trains) - self.current_train_index
        score_text = info_font.render(
            f"{self.language_manager.get_text('score')}: {self.score}", True, self.theme['text']
        )
        remaining_text = info_font.render(
            f"{self.language_manager.get_text('remaining')}: {remaining_trains}", True, self.theme['text']
        )
        mistake_cap = "∞" if self.zen_mode else str(self.max_mistakes)
        mistakes_text = info_font.render(
            f"{self.language_manager.get_text('mistakes')}: {self.mistakes}/{mistake_cap}", True, self.theme['text']
        )
        level_text = info_font.render(
            f"{self.language_manager.get_text('level_label')} {self.level}: {self.level_name}", True, self.theme['text']
        )
        high_score_value = self.get_current_high_score()
        high_score_text = info_font.render(
            f"{self.language_manager.get_text('high_score')}: {high_score_value}", True, self.theme['text']
        )
        mode_label = self.language_manager.get_text('mode')
        active_mode = self.language_manager.get_text(f"mode_{self.game_mode}")
        mode_text = small_font.render(f"{mode_label}: {active_mode}", True, self.theme['text'])
        description_text = small_font.render(self.level_description, True, self.theme['text'])

        screen.blit(score_text, (10, 10))
        screen.blit(remaining_text, (10, 50))
        screen.blit(mistakes_text, (10, 90))
        screen.blit(level_text, (10, 130))
        screen.blit(high_score_text, (10, 170))
        screen.blit(mode_text, (10, 210))
        screen.blit(description_text, (10, 240))
        info_bottom = self.render_modifier_badges(screen, 10, 280, 360)
        self.draw_combo_meter(screen, 10, info_bottom + 10, 260, 26)

        self.mute_button.draw(screen)  # Draw mute button

        for particle in self.explosion_particles:  # Draw explosion particles
            particle.draw(screen)

        if self.combo_message:  # Draw combo message
            self.combo_message.draw(screen)

        if self.level_intro_timer > 0:
            banner_font = pygame.font.Font(FONT_PATH, 48)
            banner_text = self.language_manager.get_text(
                "new_level", level=self.level, name=self.level_name
            )
            text_surface = banner_font.render(banner_text, True, self.theme['text'])
            banner_surface = pygame.Surface((text_surface.get_width() + 40, text_surface.get_height() + 20), pygame.SRCALPHA)
            pygame.draw.rect(banner_surface, (*self.theme['button'], 200), banner_surface.get_rect(), border_radius=12)
            banner_surface.blit(text_surface, (20, 10))
            screen.blit(
                banner_surface,
                (WIDTH//2 - banner_surface.get_width()//2, HEIGHT//6),
            )

    # Draws the game over screen
    def draw_game_over(self, screen):
        title_font = pygame.font.Font(FONT_PATH, 64)
        body_font = pygame.font.Font(FONT_PATH, 36)

        game_over_text = title_font.render(self.language_manager.get_text("game_over"), True, self.theme['text'])
        score_text = body_font.render(
            self.language_manager.get_text("final_score", score=self.score), True, self.theme['text']
        )

        if self.game_over_reason == 'victory':
            reason_text = self.language_manager.get_text("reason_victory")
        elif self.game_over_reason == 'mistakes':
            reason_text = self.language_manager.get_text("reason_mistakes")
        else:
            reason_text = self.language_manager.get_text("reason_quit")

        reason_surface = body_font.render(reason_text, True, self.theme['text'])
        high_score_surface = body_font.render(
            f"{self.language_manager.get_text('high_score')}: {self.get_current_high_score()}",
            True,
            self.theme['text'],
        )

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//4 + 80))
        screen.blit(reason_surface, (WIDTH//2 - reason_surface.get_width()//2, HEIGHT//4 + 140))
        screen.blit(high_score_surface, (WIDTH//2 - high_score_surface.get_width()//2, HEIGHT//4 + 200))

        self.play_again_button.draw(screen)

    # Handles click events
    def handle_click(self, pos):
        if self.mute_button.is_clicked(pos):  # If the mute button is clicked
            self.sound_manager.toggle_mute()
            self.mute_button.text = "🔊" if not self.sound_manager.muted else "🔈"  # Update mute button text
            return True

        if self.state == MENU:  # If the state is MENU
            if self.start_button.is_clicked(pos):  # If the start button is clicked
                self.start_button.create_particles()  # Create particles
                self.sound_manager.play('click')  # Play click sound
                self.state = PLAYING  # Set state to PLAYING
                self.reset_game()  # Reset the game
            elif self.quit_button.is_clicked(pos):  # If the quit button is clicked
                self.game_over_reason = 'quit'
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
                            self.on_correct_match(current_train)
                        else:
                            self.on_wrong_match()
            if not clicked:
                self.add_message(self.language_manager.get_text("message_click_train"), self.theme['accent'], 0.5)

        elif self.state == GAME_OVER:  # If the state is GAME_OVER
            if self.play_again_button.is_clicked(pos):  # If the play again button is clicked
                self.sound_manager.play('click')  # Play click sound
                self.state = PLAYING  # Set state to PLAYING
                self.reset_game()  # Reset the game
            elif self.quit_button.is_clicked(pos):  # If the quit button is clicked
                self.game_over_reason = 'quit'
                if getattr(self.sound_manager, 'available', False):
                    self.sound_manager.play_music('menu')
                return False
        return True

    # Updates the game
    def update(self):
        if self.state == PLAYING:  # If the state is PLAYING
            current_time = pygame.time.get_ticks()  # Get current time
            dt = (current_time - self.last_time) / 1000.0  # Calculate delta time
            self.last_time = current_time  # Update last time

            self._update_modifier_effects(dt)

            for layer in self.parallax_layers:  # Update parallax layers
                layer.update(dt)

            if self.level_intro_timer > 0:
                self.level_intro_timer = max(0, self.level_intro_timer - dt)

            for train in self.track_trains:  # Update track trains
                if train.moving:
                    train.speed = self.train_speed * self.speed_multiplier
                    train.move()

            if self.all_trains_moving and all(not train.moving for train in self.track_trains):
                self.all_trains_moving = False
                self.handle_level_completion()

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

    def on_correct_match(self, current_train: Train) -> None:
        self.sound_manager.play('correct')
        self.create_explosion(current_train.x, current_train.y, current_train.color)
        current_train.moving = True
        current_train.move_direction = "left"
        current_train.speed = self.train_speed
        self.score += 1
        self.add_message(self.language_manager.get_text("message_correct"), self.theme['secondary'])
        self.current_train_index += 1
        self.combo_count += 1
        self.update_combo_message()
        self.sound_manager.play('item_pickup')
        if self.combo_count % 4 == 0 and self.mistakes > 0:
            self.mistakes -= 1
            self.sound_manager.play('recovery')
            self.add_message(
                self.language_manager.get_text('mistake_recovered'),
                self.theme['secondary'],
                0.9,
            )
        if self.current_train_index >= len(self.track_trains):
            self.all_trains_moving = True

    def on_wrong_match(self) -> None:
        self.sound_manager.play('wrong')
        self.add_message(self.language_manager.get_text("message_wrong"), self.theme['error'])
        self.combo_count = 0
        self.combo_message = None
        self.mistakes += 1
        if self.zen_mode:
            self.add_message(self.language_manager.get_text("zen_reminder"), self.theme['secondary'], 0.6)
            return
        if self.mistakes >= self.max_mistakes:
            self.state = GAME_OVER
            self.game_over_reason = 'mistakes'
            if self.game_mode == 'endless':
                self.endless_high_score = max(self.endless_high_score, self.score)
            else:
                self.high_score = max(self.high_score, self.score)
            self.sound_manager.play('game_over_sting')
            if getattr(self.sound_manager, 'available', False):
                self.sound_manager.play_music('game_over', loop=False)

    def handle_level_completion(self):
        if self.game_mode == 'endless':
            self.endless_stage += 1
            self.level = self.endless_stage + 1
            previous_mistakes = self.mistakes
            self.mistakes = max(0, self.mistakes - 1)
            self.combo_count = 0
            self.combo_message = None
            self.level_index = min(self.endless_stage, len(LEVEL_CONFIGS) - 1)
            previous_modifiers = set(self.active_modifiers)
            self.apply_level_rules()
            self.initialize_trains()
            self.level_intro_timer = 2.5
            banner = self.language_manager.get_text('new_level', level=self.level, name=self.level_name)
            self.add_message(banner, self.theme['accent'], 1.5)
            if self.mistakes < previous_mistakes:
                self.add_message(
                    self.language_manager.get_text('mistake_recovered'),
                    self.theme['secondary'],
                    0.8,
                )
            new_modifiers = set(self.active_modifiers) - previous_modifiers
            for modifier in new_modifiers:
                info = MODIFIER_DEFINITIONS.get(modifier)
                if info:
                    name = self.language_manager.get_text(info["name_key"])
                    self.add_message(name, self.theme['accent'], 1.2)
            self.sound_manager.play('level_up')
            if getattr(self.sound_manager, 'available', False):
                self.sound_manager.play_music('endless')
        else:
            if self.level_index < len(LEVEL_CONFIGS) - 1:
                self.level_index += 1
                self.level = self.level_index + 1
                self.mistakes = 0
                self.combo_count = 0
                self.combo_message = None
                previous_modifiers = set(self.active_modifiers)
                self.apply_level_rules()
                self.initialize_trains()
                self.level_intro_timer = 2.5
                self.add_message(
                    self.language_manager.get_text('new_level', level=self.level, name=self.level_name),
                    self.theme['accent'],
                    1.5,
                )
                new_modifiers = set(self.active_modifiers) - previous_modifiers
                for modifier in new_modifiers:
                    info = MODIFIER_DEFINITIONS.get(modifier)
                    if info:
                        name = self.language_manager.get_text(info["name_key"])
                        self.add_message(name, self.theme['accent'], 1.2)
                self.sound_manager.play('level_up')
            else:
                self.state = GAME_OVER
                self.game_over_reason = 'victory'
                self.high_score = max(self.high_score, self.score)
                self.sound_manager.play('victory')
                if getattr(self.sound_manager, 'available', False):
                    self.sound_manager.play_music('victory_theme', loop=False)
                self.add_message(self.language_manager.get_text('victory_banner'), self.theme['secondary'], 2.0)

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
    """Modern presentation layer with enhanced UI, settings, and language support."""

    def __init__(self):
        self.theme = LIGHT_THEME  # Ensure theme exists before base init
        self.language_manager = LanguageManager()
        super().__init__(language_manager=self.language_manager)
        self.dark_mode = False
        self.transitioning = False
        self.transition_alpha = 0
        self.particles: List[Particle] = []
        self.selected_train_index = 0
        self.instruction_font = pygame.font.Font(FONT_PATH, 32)
        self.difficulty_modes = ["standard", "relaxed", "expert"]
        self.difficulty_mode_index = 0
        self.difficulty_mode = self.difficulty_modes[self.difficulty_mode_index]
        self.trees = [Tree(random.randint(50, WIDTH - 50), HEIGHT - 100) for _ in range(TREE_COUNT)]
        self.clouds = [Cloud(random.randint(0, WIDTH), random.randint(*CLOUD_HEIGHT_RANGE)) for _ in range(CLOUD_COUNT)]
        self.stars = [Star(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)) for _ in range(STAR_COUNT)]

        self.create_modern_buttons()
        self.theme_button = ModernButton(
            WIDTH - 120,
            10,
            100,
            40,
            "DARK",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )
        self.settings_button = ModernButton(
            WIDTH - 240,
            10,
            110,
            40,
            self.language_manager.get_text("settings"),
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )

        self.show_settings = False
        panel_width, panel_height = 420, 430
        self.settings_panel_rect = pygame.Rect(
            WIDTH // 2 - panel_width // 2,
            HEIGHT // 2 - panel_height // 2,
            panel_width,
            panel_height,
        )
        self.create_settings_buttons()
        self.update_settings_texts()
        self.update_button_styles()

        try:
            self.parallax_layers = [
                ParallaxLayer(
                    os.path.join(IMAGES_DIR, "cloud_layer.png"),
                    CONFIG["parallax"]["cloud_speed"],
                    CONFIG["parallax"]["cloud_offset_y"],
                ),
                ParallaxLayer(
                    os.path.join(IMAGES_DIR, "tree_layer.png"),
                    CONFIG["parallax"]["tree_speed"],
                    CONFIG["parallax"]["tree_offset_y"],
                ),
            ]
        except KeyError as e:
            print(f"Warning: Missing parallax configuration: {e}")
            self.parallax_layers = []

    def create_modern_buttons(self):
        self.start_button = ModernButton(
            WIDTH//2 - 140,
            HEIGHT//2,
            280,
            60,
            self.language_manager.get_text("start"),
            self.theme['primary'],
            self.theme,
            self.sound_manager,
        )
        self.quit_button = ModernButton(
            WIDTH//2 - 140,
            HEIGHT//2 + 80,
            280,
            60,
            self.language_manager.get_text("quit"),
            self.theme['error'],
            self.theme,
            self.sound_manager,
        )
        self.play_again_button = ModernButton(
            WIDTH//2 - 140,
            HEIGHT//2 + 80,
            280,
            60,
            self.language_manager.get_text("play_again"),
            self.theme['primary'],
            self.theme,
            self.sound_manager,
        )

    def create_settings_buttons(self):
        btn_width = self.settings_panel_rect.width - 60
        base_x = self.settings_panel_rect.x + 30
        base_y = self.settings_panel_rect.y + 90
        self.language_button = ModernButton(
            base_x,
            base_y,
            btn_width,
            50,
            "",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )
        self.difficulty_button = ModernButton(
            base_x,
            base_y + 70,
            btn_width,
            50,
            "",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )
        self.symbols_button = ModernButton(
            base_x,
            base_y + 140,
            btn_width,
            50,
            "",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )
        self.mode_button = ModernButton(
            base_x,
            base_y + 210,
            btn_width,
            50,
            "",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )
        self.zen_button = ModernButton(
            base_x,
            base_y + 280,
            btn_width,
            50,
            "",
            self.theme['button'],
            self.theme,
            self.sound_manager,
        )

    def reset_game(self):
        super().reset_game()
        self.show_settings = False
        if hasattr(self, 'language_button'):
            self.update_settings_texts()

    def update_settings_texts(self):
        language_label = f"{self.language_manager.get_text('language')}: {self.language_manager.get_language_label()}"
        difficulty_key = f"difficulty_{self.difficulty_modes[self.difficulty_mode_index]}"
        difficulty_label = f"{self.language_manager.get_text('difficulty')}: {self.language_manager.get_text(difficulty_key)}"
        symbols_state = (
            self.language_manager.get_text('color_mode_on')
            if self.color_blind_mode
            else self.language_manager.get_text('color_mode_off')
        )
        symbols_label = f"{self.language_manager.get_text('color_mode')}: {symbols_state}"
        mode_label = f"{self.language_manager.get_text('mode')}: {self.language_manager.get_text(f'mode_{self.game_mode}')}"
        zen_state = (
            self.language_manager.get_text('zen_mode_on')
            if self.zen_mode
            else self.language_manager.get_text('zen_mode_off')
        )
        zen_label = f"{self.language_manager.get_text('zen_mode')}: {zen_state}"

        self.language_button.text = language_label
        self.difficulty_button.text = difficulty_label
        self.symbols_button.text = symbols_label
        self.mode_button.text = mode_label
        self.zen_button.text = zen_label

    def update_button_styles(self):
        for button in [self.start_button, self.play_again_button]:
            button.color = self.theme['primary']
            button.theme = self.theme
        self.quit_button.color = self.theme['error']
        self.quit_button.theme = self.theme
        self.theme_button.color = self.theme['button']
        self.theme_button.theme = self.theme
        self.settings_button.color = self.theme['button']
        self.settings_button.theme = self.theme
        for button in [self.language_button, self.difficulty_button, self.symbols_button, self.mode_button, self.zen_button]:
            button.color = self.theme['button']
            button.theme = self.theme

    def update_language(self, language_code: str | None = None) -> None:
        super().update_language(language_code)
        self.settings_button.text = self.language_manager.get_text("settings")
        self.start_button.text = self.language_manager.get_text("start")
        self.quit_button.text = self.language_manager.get_text("quit")
        self.play_again_button.text = self.language_manager.get_text("play_again")
        self.update_settings_texts()

    def cycle_language(self):
        self.language_manager.cycle_language()
        self.update_language()

    def cycle_difficulty(self):
        self.difficulty_mode_index = (self.difficulty_mode_index + 1) % len(self.difficulty_modes)
        self.difficulty_mode = self.difficulty_modes[self.difficulty_mode_index]
        modifiers = {"standard": 0, "relaxed": 1, "expert": -1}
        self.additional_mistakes = modifiers.get(self.difficulty_mode, 0)
        self.update_mistake_limits(self.base_level_mistakes)
        self.update_settings_texts()
        diff_label = self.language_manager.get_text(f"difficulty_{self.difficulty_mode}")
        self.add_message(diff_label, self.theme['accent'], 0.6)

    def toggle_symbols(self):
        self.color_blind_mode = not self.color_blind_mode
        self.update_settings_texts()
        message_key = 'color_mode_on' if self.color_blind_mode else 'color_mode_off'
        self.add_message(self.language_manager.get_text(message_key), self.theme['accent'], 0.6)

    def toggle_zen_mode(self):
        self.zen_mode = not self.zen_mode
        self.update_mistake_limits(self.base_level_mistakes)
        self.update_settings_texts()
        if self.zen_mode:
            message = self.language_manager.get_text('zen_hint')
            color = self.theme['secondary']
        else:
            message = self.language_manager.get_text('zen_mode_off')
            color = self.theme['accent']
        self.add_message(message, color, 0.8)
        if self.zen_mode and self.state == PLAYING:
            self.add_message(self.language_manager.get_text('zen_reminder'), self.theme['secondary'], 0.6)

    def cycle_mode(self):
        current_index = self.available_modes.index(self.game_mode)
        self.game_mode = self.available_modes[(current_index + 1) % len(self.available_modes)]
        mode_label = self.language_manager.get_text(f"mode_{self.game_mode}")
        self.update_settings_texts()
        self.state = MENU
        self.reset_game()
        if getattr(self.sound_manager, 'available', False):
            self.sound_manager.play_music('menu')
        self.add_message(
            self.language_manager.get_text('mode_switch_warning', mode=mode_label),
            self.theme['accent'],
            1.0,
        )

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
                self.on_correct_match(current_train)
            else:
                self.on_wrong_match()
        else:
            self.add_message(self.language_manager.get_text("message_no_trains"), self.theme['accent'], 0.5)

    def start_transition(self):
        self.transitioning = True
        self.transition_alpha = 0

    def toggle_theme(self):
        self.start_transition()

    def create_background(self):
        self.background.fill(self.theme['background'])
        for x in range(0, WIDTH, 30):
            pygame.draw.rect(self.background, self.theme['track'], (x, RAILROAD_HEIGHT, 20, 20))
        rail_color = self.theme.get('rail_color', self.theme['text'])
        pygame.draw.line(self.background, rail_color, (0, RAILROAD_HEIGHT - 5), (WIDTH, RAILROAD_HEIGHT - 5), RAIL_THICKNESS)
        pygame.draw.line(self.background, rail_color, (0, RAILROAD_HEIGHT + 25), (WIDTH, RAILROAD_HEIGHT + 25), RAIL_THICKNESS)

    def draw_menu(self, screen):
        screen.blit(self.background, (0, 0))
        title_font = pygame.font.Font(FONT_PATH, 72)
        subtitle_font = pygame.font.Font(FONT_PATH, 32)
        title_text = title_font.render(self.language_manager.get_text("title"), True, self.theme['text'])
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4 - 40))

        subtitle = subtitle_font.render(self.level_description, True, self.theme['text'])
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 20))

        self.start_button.draw(screen)
        self.quit_button.draw(screen)
        self.settings_button.draw(screen)

        info_font = pygame.font.Font(FONT_PATH, 24)
        difficulty_key = f"difficulty_{self.difficulty_modes[self.difficulty_mode_index]}"
        difficulty_text = info_font.render(
            f"{self.language_manager.get_text('difficulty')}: {self.language_manager.get_text(difficulty_key)}",
            True,
            self.theme['text'],
        )
        language_text = info_font.render(
            f"{self.language_manager.get_text('language')}: {self.language_manager.get_language_label()}",
            True,
            self.theme['text'],
        )
        mode_text = info_font.render(
            f"{self.language_manager.get_text('mode')}: {self.language_manager.get_text(f'mode_{self.game_mode}')}",
            True,
            self.theme['text'],
        )
        screen.blit(difficulty_text, (WIDTH//2 - difficulty_text.get_width()//2, HEIGHT//2 + 170))
        screen.blit(language_text, (WIDTH//2 - language_text.get_width()//2, HEIGHT//2 + 200))
        screen.blit(mode_text, (WIDTH//2 - mode_text.get_width()//2, HEIGHT//2 + 230))

        version_font = pygame.font.Font(FONT_PATH, 16)
        version_text = version_font.render("v1.4 | Zenith Update", True, self.theme['text'])
        screen.blit(version_text, (10, HEIGHT - 30))

        if self.show_settings:
            self.draw_settings_panel(screen)

    def draw_settings_panel(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        panel_surface = pygame.Surface((self.settings_panel_rect.width, self.settings_panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*self.theme['button'], 235), panel_surface.get_rect(), border_radius=16)
        title_font = pygame.font.Font(FONT_PATH, 36)
        title_text = title_font.render(self.language_manager.get_text("settings_title"), True, self.theme['text'])
        panel_surface.blit(title_text, (panel_surface.get_width()//2 - title_text.get_width()//2, 20))
        screen.blit(panel_surface, self.settings_panel_rect.topleft)

        for button in [
            self.language_button,
            self.difficulty_button,
            self.symbols_button,
            self.mode_button,
            self.zen_button,
        ]:
            button.draw(screen)

    def draw_game(self, screen):
        for layer in self.parallax_layers:
            layer.draw(screen)
        screen.blit(self.background, (0, 0))

        if self.dark_mode:
            for star in self.stars:
                star.draw(screen)
        else:
            for cloud in self.clouds:
                cloud.draw(screen)

        for tree in self.trees:
            tree.draw(screen)

        for train in self.track_trains:
            if not train.moving:
                train.draw(screen, self.dark_mode, self.color_blind_mode)
        self._draw_fog_if_needed(screen)
        for train in self.selection_trains:
            train.draw(screen, self.dark_mode, self.color_blind_mode)

        selection_train = self.selection_trains[self.selected_train_index]
        pygame.draw.rect(
            screen,
            self.theme['accent'],
            (selection_train.x - 8, selection_train.y - 8, selection_train.width + 16, selection_train.height + 16),
            3,
        )

        for message in self.messages:
            message.draw(screen)

        info_font = pygame.font.Font(FONT_PATH, 30)
        small_font = pygame.font.Font(FONT_PATH, 22)
        panel_height = 340 + len(self.modifier_display_lines) * 70
        panel = pygame.Surface((320, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*self.theme['button'], 210), panel.get_rect(), border_radius=16)
        lines = [
            f"{self.language_manager.get_text('score')}: {self.score}",
            f"{self.language_manager.get_text('remaining')}: {len(self.track_trains) - self.current_train_index}",
            f"{self.language_manager.get_text('mistakes')}: {self.mistakes}/{('∞' if self.zen_mode else self.max_mistakes)}",
            f"{self.language_manager.get_text('level_label')} {self.level}: {self.level_name}",
            f"{self.language_manager.get_text('high_score')}: {self.get_current_high_score()}",
        ]
        for idx, line in enumerate(lines):
            text_surface = info_font.render(line, True, self.theme['text'])
            panel.blit(text_surface, (16, 16 + idx * 34))

        diff_label = f"{self.language_manager.get_text('difficulty')}: {self.language_manager.get_text(f'difficulty_{self.difficulty_mode}')}"
        lang_label = f"{self.language_manager.get_text('language')}: {self.language_manager.get_language_label()}"
        label_y = 16 + len(lines) * 34
        panel.blit(small_font.render(diff_label, True, self.theme['text']), (16, label_y))
        panel.blit(small_font.render(lang_label, True, self.theme['text']), (16, label_y + 28))
        badges_bottom = self.render_modifier_badges(panel, 16, label_y + 60, panel.get_width() - 32)
        self.draw_combo_meter(panel, 16, badges_bottom + 10, panel.get_width() - 32, 24)
        screen.blit(panel, (WIDTH - panel.get_width() - 20, 20))

        instruction_surface = self.instruction_font.render(self.instruction_text, True, self.theme['text'])
        instruction_bg = pygame.Surface((instruction_surface.get_width() + 50, 60), pygame.SRCALPHA)
        pygame.draw.rect(instruction_bg, (*self.theme['button'], 220), instruction_bg.get_rect(), border_radius=24)
        instruction_bg.blit(instruction_surface, (25, 18))
        screen.blit(instruction_bg, (WIDTH//2 - instruction_bg.get_width()//2, HEIGHT - 90))

        self.mute_button.draw(screen)
        self.theme_button.draw(screen)
        self.settings_button.draw(screen)

        for particle in self.explosion_particles:
            particle.draw(screen)

        if self.combo_message:
            self.combo_message.draw(screen)

        if self.level_intro_timer > 0:
            banner_font = pygame.font.Font(FONT_PATH, 48)
            banner_text = self.language_manager.get_text("new_level", level=self.level, name=self.level_name)
            text_surface = banner_font.render(banner_text, True, self.theme['text'])
            banner_surface = pygame.Surface((text_surface.get_width() + 40, text_surface.get_height() + 20), pygame.SRCALPHA)
            pygame.draw.rect(banner_surface, (*self.theme['button'], 200), banner_surface.get_rect(), border_radius=12)
            banner_surface.blit(text_surface, (20, 10))
            screen.blit(banner_surface, (WIDTH//2 - banner_surface.get_width()//2, HEIGHT//6))

        if self.show_settings:
            self.draw_settings_panel(screen)

        if self.transitioning:
            transition_surface = pygame.Surface((WIDTH, HEIGHT))
            transition_surface.fill(self.theme['background'])
            transition_surface.set_alpha(self.transition_alpha)
            screen.blit(transition_surface, (0, 0))

    def handle_click(self, pos):
        if self.theme_button.is_clicked(pos):
            self.toggle_theme()
            self.sound_manager.play('click')
            return True

        if self.settings_button.is_clicked(pos):
            self.show_settings = not self.show_settings
            self.sound_manager.play('click')
            return True

        if self.show_settings:
            if self.language_button.is_clicked(pos):
                self.cycle_language()
                self.sound_manager.play('confirmation')
                return True
            if self.difficulty_button.is_clicked(pos):
                self.cycle_difficulty()
                self.sound_manager.play('confirmation')
                return True
            if self.symbols_button.is_clicked(pos):
                self.toggle_symbols()
                self.sound_manager.play('confirmation')
                return True
            if self.mode_button.is_clicked(pos):
                self.cycle_mode()
                self.sound_manager.play('confirmation')
                return True
            if self.zen_button.is_clicked(pos):
                self.toggle_zen_mode()
                self.sound_manager.play('confirmation')
                return True
            if not self.settings_panel_rect.collidepoint(pos):
                self.show_settings = False

        return super().handle_click(pos)

    def update(self, dt: float) -> None:
        super().update()
        for cloud in self.clouds:
            cloud.update(dt)

        for button in [
            self.start_button,
            self.quit_button,
            self.play_again_button,
            self.theme_button,
            self.settings_button,
        ]:
            button.update(dt)

        if self.show_settings:
            for button in [
                self.language_button,
                self.difficulty_button,
                self.symbols_button,
                self.mode_button,
                self.zen_button,
            ]:
                button.update(dt)

        if self.transitioning:
            self.transition_alpha += TRANSITION_SPEED * dt
            if self.transition_alpha >= 255:
                self.complete_transition()

    def complete_transition(self):
        self.dark_mode = not self.dark_mode
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.theme_button.text = "LIGHT" if self.dark_mode else "DARK"
        self.create_background()
        self.update_button_styles()
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
                hover_buttons = [
                    game.theme_button,
                    game.start_button,
                    game.quit_button,
                    game.play_again_button,
                    game.settings_button,
                ]
                if getattr(game, 'show_settings', False):
                    hover_buttons.extend(
                        [
                            game.language_button,
                            game.difficulty_button,
                            game.symbols_button,
                            game.mode_button,
                            game.zen_button,
                        ]
                    )
                for button in hover_buttons:
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
