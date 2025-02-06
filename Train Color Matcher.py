import json
import pygame
import random
import os
import math
from typing import List, Dict, Tuple

# Initialize Pygame and fonts module
pygame.init()
pygame.font.init()  # Add this line to initialize the font module

# Load configuration
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Initialize constants from config
WIDTH = CONFIG["window"]["width"]
HEIGHT = CONFIG["window"]["height"]
WINDOW_TITLE = CONFIG["window"]["title"]

# Colors from config
WHITE = tuple(CONFIG["colors"]["white"])
BLACK = tuple(CONFIG["colors"]["black"])

# Asset directories
ASSETS_DIR = "assets"
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "music")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Theme colors
LIGHT_THEME = {
    'background': (245, 245, 245),
    'primary': (66, 133, 244),
    'secondary': (52, 168, 83),
    'accent': (251, 188, 4),
    'error': (234, 67, 53),
    'text': (32, 33, 36),
    'shadow': (0, 0, 0, 50),
    'button': (255, 255, 255),
    'track': (200, 200, 200),
    'rail_color': (100, 100, 100)
}

DARK_THEME = {
    'background': (30, 30, 30),
    'primary': (138, 180, 248),
    'secondary': (129, 201, 149),
    'accent': (253, 214, 99),
    'error': (242, 139, 130),
    'text': (232, 234, 237),
    'shadow': (0, 0, 0, 80),
    'button': (70, 70, 70),
    'track': (70, 70, 70),
    'rail_color': (200, 200, 200)
}

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

# Train colors
TRAIN_COLORS = [RED, BLUE, GREEN]

# Font settings
FONT_PATH = os.path.join(FONTS_DIR, "RobotoCondensed-Italic-VariableFont_wght.ttf")

# Initialize the font
try:
    game_font = pygame.font.Font(FONT_PATH, 36)
except:
    print("Warning: Custom font not found. Using system default.")
    game_font = pygame.font.Font(None, 36)

# Add sound initialization
class SoundManager:
    def __init__(self):
        try:
            self.sounds = {
                'correct': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'General_sound_effect.mp3')),
                'wrong': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Suspenseful Music.mp3')),
                'click': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Button sounds.mp3')),
                'game_over': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Cutscene Music.mp3')),
                'background': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Menu Music.mp3')),  # 新增背景音樂
                'button_hover': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'UI opening sounds.mp3')),
                'level_up': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'MC Level Up.mp3')),
                'victory': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Victory Music.mp3')),
                'item_pickup': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Item Pickup.mp3')),
                'confirmation': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'Confirmation Sounds (in UI).mp3'))
            }
            self.sounds['background'].set_volume(0.5)  # 設置背景音樂音量
            self.sounds['background'].play(-1)  # 循環播放背景音樂
        except:
            print("Warning: Sound files not found. Running without sound.")
            self.sounds = {}
        self.muted = False

    def play(self, sound_name):
        if not self.muted and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.lifetime = 1.0
        self.velocity = [random.uniform(-30, 30), random.uniform(-30, 30)]
        self.gravity = 15  # 重力效果
        self.alpha_decay = random.uniform(0.5, 1.5)  # Random alpha decay rate
        self.original_size = self.size  # Store original size for scaling

    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.velocity[1] += self.gravity * dt  # 施加重力
        self.lifetime -= dt * 2
        self.size = max(0, self.original_size * self.lifetime)  # Scale size over lifetime

    def draw(self, screen):
        alpha = int(255 * self.lifetime)
        if (alpha > 0):
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(surface, (self.x - self.size, self.y - self.size))

class SmokeParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.velocity = [random.uniform(-5, 5), random.uniform(-10, -5)]  # Upward drift
        self.gravity = 2  # Less gravity for smoke
        self.original_size = self.size

    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.velocity[1] += self.gravity * dt
        self.lifetime -= dt
        self.size = max(0, self.original_size * self.lifetime)

    def draw(self, screen):
        alpha = int(255 * self.lifetime)
        if alpha > 0:
            size = int(self.size)
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha), (size, size), size)
            screen.blit(surface, (self.x - size, self.y - size))

class ExplosionParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.lifetime = random.uniform(0.3, 0.7)  # Shorter lifetime for explosion
        self.velocity = [random.uniform(-100, 100), random.uniform(-100, 100)]  # Higher velocity
        self.gravity = 50  # Stronger gravity for explosion

    def update(self, dt):
        super().update(dt)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(FONT_PATH, 36)  # Use custom font

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class ModernButton(Button):
    def __init__(self, x, y, width, height, text, color, theme, sound_manager):  # Pass the sound_manager instance
        super().__init__(x, y, width, height, text, color)
        self.hover = False
        self.original_y = y
        self.animation_offset = 0
        self.particles = []
        self.theme = theme  # 儲存主題設定
        self.glow_radius = 0
        self.glow_direction = 1  # 1 for increasing, -1 for decreasing
        self.sound_manager = sound_manager  # Store the sound_manager instance
        self.font = pygame.font.Font(FONT_PATH, 36)  # Use custom font

    def draw(self, screen):
        # Shadow with theme support
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.theme['shadow'], 
                        (0, 0, self.rect.width, self.rect.height), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x, self.rect.y + 5))

        # Button with hover effect
        hover_offset = 3 if self.hover else 0

        # Draw glow effect
        if self.hover:
            glow_color = (255, 255, 255, int(self.glow_radius))  # White glow
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, self.rect.width + 20, self.rect.height + 20), border_radius=10)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - hover_offset - self.animation_offset - 10))

        pygame.draw.rect(screen, self.color, 
                        (self.rect.x, self.rect.y - hover_offset - self.animation_offset, 
                         self.rect.width, self.rect.height), 
                        border_radius=10)

        # Text with theme support
        text_surface = self.font.render(self.text, True, self.theme['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        text_rect.y -= hover_offset + self.animation_offset
        screen.blit(text_surface, text_rect)

        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

    def update(self, dt):
        # Update hover animation
        if self.hover:
            self.animation_offset = math.sin(pygame.time.get_ticks() / 200) * 2
            self.glow_radius += 5 * self.glow_direction
            if self.glow_radius > 100:
                self.glow_direction = -1
            elif self.glow_radius < 20:
                self.glow_direction = 1
        else:
            self.glow_radius = 0
            self.glow_direction = 1

        # Update particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)

    def handle_hover(self, pos):
        is_hovering = self.rect.collidepoint(pos)
        if is_hovering and not self.hover:
            self.sound_manager.play('button_hover')  # Play hover sound
        self.hover = is_hovering

    def create_particles(self):
        for _ in range(20):
            self.particles.append(Particle(
                self.rect.centerx, 
                self.rect.centery, 
                self.color
            ))

class TrainRenderer:
    def __init__(self, train):
        self.train = train

    def draw(self, screen, is_dark_mode=False):
        # Draw train body
        pygame.draw.rect(screen, self.train.color, 
            (self.train.x, self.train.y, 
             CONFIG["train"]["width"], CONFIG["train"]["height"]), 
            border_radius=5)
        
        # Draw train chimney
        pygame.draw.rect(screen, (50, 50, 50), 
            (self.train.x + 10, self.train.y - 10, 10, 10))
        
        # Draw train windows with light effect in dark mode
        window_color = (255, 255, 200) if is_dark_mode else (200, 200, 200)
        if is_dark_mode:
            # Add glow effect for windows in dark mode
            for window_x in [self.train.x + 25, self.train.x + 45]:
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 255, 0, 100), (10, 10), 8)
                screen.blit(glow_surf, (window_x - 5, self.train.y))
        
        # Draw windows
        pygame.draw.rect(screen, window_color, (self.train.x + 25, self.train.y + 5, 10, 10))
        pygame.draw.rect(screen, window_color, (self.train.x + 45, self.train.y + 5, 10, 10))
        
        # Draw train wheels
        pygame.draw.circle(screen, BLACK, (self.train.x + 15, self.train.y + 30), 5)
        pygame.draw.circle(screen, BLACK, (self.train.x + 45, self.train.y + 30), 5)

        # Draw smoke particles
        for particle in self.train.smoke_particles:
            particle.draw(screen)

class Train:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.width = CONFIG["train"]["width"]
        self.height = CONFIG["train"]["height"]
        self.moving = False
        self.move_direction = "left"
        self.smoke_particles = []  # Add smoke particles
        self.renderer = TrainRenderer(self)

    def draw(self, screen, is_dark_mode=False):
        self.renderer.draw(screen, is_dark_mode)

    def move(self):
        if self.moving:
            if self.move_direction == "left":
                self.x -= 5
            elif self.move_direction == "right":
                self.x += 5

            # Emit smoke particles
            if random.random() < 0.3:
                self.emit_smoke()

            # Update smoke particles
            for particle in self.smoke_particles:
                particle.update(0.1)  # dt value

            self.smoke_particles = [p for p in self.smoke_particles if p.lifetime > 0]

            # 火車移動出螢幕後停止
            if self.x + self.width < 0 or self.x > WIDTH:
                self.moving = False
        return self.moving

    def emit_smoke(self):
        # Create smoke particle
        self.smoke_particles.append(SmokeParticle(self.x + 10, self.y - 10, GRAY))

class Message:
    def __init__(self, text, color, duration=1.0):
        self.text = text
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(FONT_PATH, 48)  # Use custom font
        self.alpha = 255  # Initial alpha value for fading effect
        
    def should_remove(self):
        return self.alpha <= 0

    def draw(self, screen):
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text_surface, text_rect)

    def update(self, dt):
        # Reduce alpha over time for fading effect
        self.alpha -= 255 * dt  # Fade out in one second

class ParallaxLayer:
    def __init__(self, image_path, speed, offset_y=0):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.valid = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Create fallback surface
            self.image = pygame.Surface((800, 200))
            self.image.fill((200, 200, 200))
            self.valid = False
        
        self.x = 0
        self.y = HEIGHT - self.image.get_height() + offset_y
        self.speed = speed

    def update(self, dt):
        if not self.valid:
            return
        self.x -= self.speed * dt
        if (self.x <= -self.image.get_width()):
            self.x = 0

    def draw(self, screen):
        if not self.valid:
            return
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x + self.image.get_width(), self.y))

class Game:
    def __init__(self):
        self.state = MENU
        self.reset_game()
        self.create_buttons()
        self.high_score = 0
        self.sound_manager = SoundManager()
        self.messages = []
        self.mute_button = Button(WIDTH - 60, 10, 50, 50, "🔊", WHITE)
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.create_background()
        self.current_train_index = 0  # 新增：追蹤當前要配對的火車索引
        self.explosion_particles = []
        self.level = 1
        self.level_up_threshold = 5  # Score needed to level up
        self.train_speed = 5  # Initial train speed
        self.max_trains = 10  # Initial number of trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # 十個固定位置
        self.font = pygame.font.Font(FONT_PATH, 36)  # Use FONT_PATH instead of FONT_NAME
        self.parallax_layers = [
            ParallaxLayer(os.path.join(IMAGES_DIR, "cloud_layer.png"), 10),
            ParallaxLayer(os.path.join(IMAGES_DIR, "tree_layer.png"), 30)
        ]
        self.combo_count = 0  # Initialize combo counter
        self.combo_message = None  # Initialize combo message

    def create_background(self):
        # Create a simple background with railroad tracks
        self.background.fill(self.theme['background'])
        # Draw railroad ties
        for x in range(0, WIDTH, 30):
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 235), (WIDTH, 235), 5)
        pygame.draw.line(self.background, self.theme['rail_color'], (0, 265), (WIDTH, 265), 5)

    def add_message(self, text, color, duration=1.0):
        self.messages = [msg for msg in self.messages if not msg.should_remove()]
        self.messages.append(Message(text, color, duration))

    def reset_game(self):
        self.track_trains = []
        self.selection_trains = []
        self.score = 0
        self.current_train_index = 0  # 重置當前火車索引
        self.all_trains_moving = False  # 重置標誌
        self.explosion_particles = []
        self.level = 1  # Reset level
        self.train_speed = 5  # Reset train speed
        self.max_trains = 10  # Reset max trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]
        self.initialize_trains()
        self.last_time = pygame.time.get_ticks()
        self.combo_count = 0  # Reset combo counter
        self.combo_message = None  # Reset combo message

    def create_buttons(self):
        self.start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game", self.theme['primary'])
        self.quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Quit", self.theme['error'])
        self.play_again_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Play Again", self.theme['primary'])

    def initialize_trains(self):
        # 初始化固定位置的十列火車
        self.train_positions = [i * 80 for i in range(self.max_trains)]  # 十個固定位置
        self.track_trains = []
        for i in range(self.max_trains):
            color = random.choice(TRAIN_COLORS)
            x = self.train_positions[i]
            self.track_trains.append(Train(x, 200, color))

        # 初始化玩家可選擇的火車（底下的三個選項）
        self.selection_trains = []
        for i, color in enumerate(TRAIN_COLORS):
            self.selection_trains.append(Train(250 + i * 100, 400, color))

    def draw(self, screen):
        screen.fill(self.theme['background'])
        
        if self.state == MENU:
            self.draw_menu(screen)
        elif self.state == PLAYING:
            self.draw_game(screen)
        elif self.state == GAME_OVER:
            self.draw_game_over(screen)

    def draw_menu(self, screen):
        title_font = pygame.font.Font(FONT_PATH, 64)  # Use FONT_PATH instead of FONT_NAME
        title_text = title_font.render("Train Color Matcher", True, self.theme['text'])
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_text, title_rect)
        
        self.start_button.draw(screen)
        self.quit_button.draw(screen)

        # Add version and build info
        version_font = pygame.font.Font(FONT_PATH, 16)
        version_text = version_font.render("v1.1 | Built by dundd - Feb 2025", True, self.theme['text'])
        version_rect = version_text.get_rect(bottomleft=(10, HEIGHT - 10))
        screen.blit(version_text, version_rect)

    def draw_game(self, screen):
        # Draw parallax background
        for layer in self.parallax_layers:
            layer.draw(screen)
        
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw trains
        for i, train in enumerate(self.track_trains):
            if not train.moving:  # 只畫出還沒移動的火車
                train.draw(screen)
        for train in self.selection_trains:
            train.draw(screen)

        # Draw messages
        for message in self.messages:
            message.draw(screen)

        # Draw UI
        font = pygame.font.Font(FONT_PATH, 36)  # Use FONT_PATH instead of FONT_NAME
        
        # 更新UI顯示
        remaining_trains = len(self.track_trains) - self.current_train_index
        progress_text = font.render(f'Remaining Trains: {remaining_trains}', True, self.theme['text'])
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])
        level_text = font.render(f'Level: {self.level}', True, self.theme['text'])
        
        screen.blit(progress_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(level_text, (10, 70))
        
        self.mute_button.draw(screen)

        # Draw explosion particles
        for particle in self.explosion_particles:
            particle.draw(screen)

        # Draw combo message
        if self.combo_message:
            self.combo_message.draw(screen)

    def draw_game_over(self, screen):
        font = pygame.font.Font(FONT_PATH, 64)  # Use FONT_PATH instead of FONT_NAME
        game_over_text = font.render("Game Over!", True, self.theme['text'])
        score_text = font.render(f"Final Score: {self.score}", True, self.theme['text'])
        
        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//4))
        screen.blit(score_text, (WIDTH//2 - 150, HEIGHT//3))
        
        self.play_again_button.draw(screen)

    def handle_click(self, pos):
        if self.mute_button.is_clicked(pos):
            self.sound_manager.muted = not self.sound_manager.muted
            self.mute_button.text = "🔊" if not self.sound_manager.muted else "🔈"
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
            for selection_train in self.selection_trains:
                if (selection_train.x < pos[0] < selection_train.x + selection_train.width and
                    selection_train.y < pos[1] < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    
                    # 檢查是否還有火車需要配對
                    if self.current_train_index < len(self.track_trains):
                        current_train = self.track_trains[self.current_train_index]
                        
                        if selection_train.color == current_train.color:
                            # 配對正確
                            self.sound_manager.play('correct')
                            self.create_explosion(current_train.x, current_train.y, current_train.color)
                            current_train.moving = True
                            current_train.move_direction = "left"
                            self.score += 1
                            self.add_message("Correct!", self.theme['secondary'])
                            self.current_train_index += 1  # 移動到下一個火車
                            self.combo_count += 1  # Increment combo counter
                            self.update_combo_message()  # Update combo message
                            self.sound_manager.play('item_pickup')
                            # 檢查是否所有火車都已配對
                            if self.current_train_index >= len(self.track_trains):
                                self.all_trains_moving = True  # 設置標誌，等待所有火車移動完畢
                        else:
                            # 配對錯誤
                            self.sound_manager.play('wrong')
                            self.add_message("Wrong Color!", self.theme['error'])
                            self.combo_count = 0  # Reset combo counter
                            self.combo_message = None  # Remove combo message
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

    def update(self):
        if self.state == PLAYING:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
            self.last_time = current_time

            # Update parallax layers
            for layer in self.parallax_layers:
                layer.update(dt)

            # 更新移動中的火車
            for train in self.track_trains:
                if train.moving:
                    train.move()

            # 檢查是否所有火車都已移動完畢
            if self.all_trains_moving and all(not train.moving for train in self.track_trains):
                self.state = GAME_OVER
                self.high_score = max(self.high_score, self.score)
                self.sound_manager.play('game_over')

            # Level up check
            if self.score >= self.level * self.level_up_threshold:
                self.level_up()

            # Update messages
            for message in self.messages:
                message.update(dt)
            self.messages = [msg for msg in self.messages if not msg.should_remove()]

            # Update explosion particles
            for particle in self.explosion_particles:
                particle.update(dt)
            self.explosion_particles = [p for p in self.explosion_particles if p.lifetime > 0]

            # Update combo message
            if self.combo_message:
                self.combo_message.update(dt)
                if self.combo_message.should_remove():
                    self.combo_message = None

    def level_up(self):
        self.level += 1
        self.sound_manager.play('level_up')
        self.add_message(f"Level Up! {self.level}", self.theme['primary'], 1.5)
        self.train_speed += 1  # Increase train speed
        self.max_trains += 2  # Increase number of trains
        self.train_positions = [i * 80 for i in range(self.max_trains)]
        self.initialize_trains()  # Reinitialize trains with new parameters
        self.sound_manager.play('victory')
        # Cap the maximum number of trains
        self.max_trains = min(self.max_trains, 15)

    def create_explosion(self, x, y, color):
        for _ in range(30):
            self.explosion_particles.append(ExplosionParticle(x, y, color))

    def update_combo_message(self):
        if self.combo_count > 1:
            text = f"COMBO x{self.combo_count}!"
            if self.combo_count >= 5:
                text += " SUPER!"
            color = (255, 215, 0) if self.combo_count >= 5 else self.theme['accent']  # Gold color for super combos
            self.combo_message = ComboMessage(text, color, 1.5, 48 + min(self.combo_count * 4, 32))
            self.sound_manager.play('level_up')  # Play sound for combo

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        # Draw tree trunk
        pygame.draw.rect(screen, (139, 69, 19), (self.x, self.y, 20, 40))
        # Draw tree leaves
        pygame.draw.circle(screen, (34, 139, 34), (self.x + 10, self.y), 30)

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = random.uniform(0.5, 1.5)

    def update(self, dt):
        self.x += self.velocity * dt
        if self.x > WIDTH:
            self.x = -100

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 20)
        pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 10), 25)
        pygame.draw.circle(screen, WHITE, (self.x + 40, self.y), 20)

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.brightness = random.randint(150, 255)

    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

class ModernGame(Game):
    def __init__(self):
        self.theme = LIGHT_THEME  # Initialize theme before calling super().__init__()
        super().__init__()
        self.dark_mode = False
        self.theme = LIGHT_THEME
        self.transition_alpha = 255
        self.particles = []
        self.create_modern_buttons()
        self.theme_button = ModernButton(WIDTH - 100, 10, 80, 40, "DARK", self.theme['button'], self.theme, self.sound_manager)
        self.all_trains_moving = False  # 新增：標誌所有火車是否正在移動
        self.instruction_text = "Match the trains starting from the left!"
        self.instruction_font = pygame.font.Font(FONT_PATH, 36)  # Use custom font
        self.trees = [Tree(random.randint(50, WIDTH - 50), HEIGHT - 100) for _ in range(5)]
        self.clouds = [Cloud(random.randint(0, WIDTH), random.randint(50, 150)) for _ in range(3)]
        self.stars = [Star(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)) for _ in range(50)]
        self.transitioning = False
        self.transition_alpha = 0
        self.selected_train_index = 0  # Track the index of the selected train
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

    def handle_keyboard_input(self, event):
        if self.state == PLAYING:
            if event.key == pygame.K_LEFT:
                self.selected_train_index = (self.selected_train_index - 1) % len(self.selection_trains)
            elif event.key == pygame.K_RIGHT:
                self.selected_train_index = (self.selected_train_index + 1) % len(self.selection_trains)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.match_train()

    def match_train(self):
        if self.current_train_index < len(self.track_trains):
            selected_train = self.selection_trains[self.selected_train_index]
            current_train = self.track_trains[self.current_train_index]

            if selected_train.color == current_train.color:
                # 配對正確
                self.sound_manager.play('correct')
                current_train.moving = True
                current_train.move_direction = "left"
                self.score += 1
                self.add_message("Correct!", self.theme['secondary'])
                self.current_train_index += 1  # 移動到下一個火車

                # 檢查是否所有火車都已配對
                if self.current_train_index >= len(self.track_trains):
                    self.all_trains_moving = True  # 設置標誌，等待所有火車移動完畢
            else:
                # 配對錯誤
                self.sound_manager.play('wrong')
                self.add_message("Wrong Color!", self.theme['error'])
        else:
            self.add_message("No more trains to match!", self.theme['accent'], 0.5)

    def start_transition(self):
        self.transitioning = True
        self.transition_alpha = 0

    def toggle_theme(self):
        self.start_transition()

    def create_background(self):
        self.background.fill(self.theme['background'])
        for x in range(0, WIDTH, 30):
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['text'], (0, 235), (WIDTH, 235), 5)
        pygame.draw.line(self.background, self.theme['text'], (0, 265), (WIDTH, 265), 5)

    def draw_game(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw stars if in dark mode
        if self.dark_mode:
            for star in self.stars:
                star.draw(screen)

        # Draw trees
        for tree in self.trees:
            tree.draw(screen)

        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(screen)
        
        # Draw trains with dark mode parameter
        for train in self.track_trains + self.selection_trains:
            train.draw(screen, self.dark_mode)

        # Highlight the selected train
        selection_train = self.selection_trains[self.selected_train_index]
        pygame.draw.rect(screen, YELLOW, (selection_train.x - 5, selection_train.y - 5,
                                            selection_train.width + 10, selection_train.height + 10), 3)

        # Draw messages
        for message in self.messages:
            message.draw(screen)

        # Draw UI
        font = pygame.font.Font(None, 36)
        
        # Improved UI layout
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])
        remaining_trains = len(self.track_trains) - self.current_train_index
        progress_text = font.render(f'Remaining: {remaining_trains}', True, self.theme['text'])
        high_score_text = font.render(f'High Score: {self.high_score}', True, self.theme['text'])
        
        # Adjust UI positions
        screen.blit(score_text, (20, 20))
        screen.blit(progress_text, (20, 60))
        screen.blit(high_score_text, (20, 100))
        
        # Draw instruction with background
        instruction_surface = self.instruction_font.render(
            self.instruction_text, True, self.theme['text'])
        instruction_bg = pygame.Surface((instruction_surface.get_width() + 20, 40))
        instruction_bg.fill(self.theme['button'])
        instruction_bg.set_alpha(200)
        screen.blit(instruction_bg, 
                   (WIDTH//2 - instruction_bg.get_width()//2, HEIGHT - 60))
        screen.blit(instruction_surface, 
                   (WIDTH//2 - instruction_surface.get_width()//2, HEIGHT - 50))
        
        # Draw theme and mute buttons
        self.mute_button.draw(screen)
        self.theme_button.draw(screen)

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
            for i, selection_train in enumerate(self.selection_trains):
                if (selection_train.x < pos[0] < selection_train.x + selection_train.width and
                    selection_train.y < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    self.selected_train_index = i
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
        super().update()
        for cloud in self.clouds:
            cloud.update(dt)

        # Update particles
        for button in [self.start_button, self.quit_button, self.play_again_button, self.theme_button]:
            button.update(dt)

        # Update theme transition
        if self.transitioning:
            self.transition_alpha += 500 * dt  # Adjust speed as needed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.dark_mode = not self.dark_mode
                self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
                self.theme_button.text = "LIGHT" if self.dark_mode else "DARK"
                self.create_modern_buttons()
                self.create_background()
                self.transitioning = False
                self.transition_alpha = 0

        # Update trains
        for train in self.track_trains:
            train.move()

        # Update messages
        for message in self.messages:
            message.update(dt)
        self.messages = [msg for msg in self.messages if not msg.should_remove()]

    def create_modern_buttons(self):
        # Update buttons with emojis
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

class ComboMessage(Message):
    def __init__(self, text, color, duration=1.0, font_size=48):
        super().__init__(text, color, duration)
        try:
            self.font = pygame.font.Font(FONT_PATH, font_size)
        except:
            print(f"Warning: Could not load font {FONT_PATH}, using system default")
            self.font = pygame.font.Font(None, font_size)
        self.start_time = pygame.time.get_ticks()
        self.initial_font_size = font_size
        self.scale = 1.0
        self.position = (WIDTH//2, HEIGHT//3)
        self.color = color

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        age = (current_time - self.start_time) / 1000.0
        
        # Bounce effect
        self.scale = 1.0 + 0.2 * abs(math.sin(age * 10))
        
        # Fade out
        self.alpha = max(0, 255 * (1.0 - age / self.duration))

    def draw(self, screen):
        if self.alpha > 0:
            # Render text with current scale
            base_surface = self.font.render(self.text, True, self.color)
            scaled_size = (int(base_surface.get_width() * self.scale),
                         int(base_surface.get_height() * self.scale))
            
            # Create scaled surface
            scaled_surface = pygame.transform.scale(base_surface, scaled_size)
            scaled_surface.set_alpha(self.alpha)
            
            # Position at center
            pos = (self.position[0] - scaled_size[0]//2,
                  self.position[1] - scaled_size[1]//2)
            
            screen.blit(scaled_surface, pos)

def main():
    pygame.init()
    game = ModernGame()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game.handle_click(event.pos):
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                for button in [game.theme_button, game.start_button, 
                             game.quit_button, game.play_again_button]:
                    button.handle_hover(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_keyboard_input(event)
        
        # 更新和渲染
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        pygame.quit()
