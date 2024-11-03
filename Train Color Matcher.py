import pygame
import random
import os
import math
from typing import List, Dict, Tuple

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Train Color Matching Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
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
    'track': (200, 200, 200)
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
    'track': (70, 70, 70)
}

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

# Train colors
TRAIN_COLORS = [RED, BLUE, GREEN]

FONT_PATH = pygame.font.get_default_font()
SOUNDS_DIR = "sounds"  # Create this directory and add sound files

# Add sound initialization
class SoundManager:
    def __init__(self):
        try:
            self.sounds = {
                'correct': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'correct.wav')),
                'wrong': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'wrong.wav')),
                'click': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'click.wav')),
                'game_over': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'game_over.wav')),
                'background': pygame.mixer.Sound(os.path.join(SOUNDS_DIR, 'background.wav'))  # 新增背景音樂
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
        self.size = random.randint(2, 6)
        self.lifetime = 1.0
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]

    def update(self, dt):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= dt * 2
        self.size = max(0, self.size - dt * 2)

    def draw(self, screen):
        alpha = int(255 * self.lifetime)
        if (alpha > 0):
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(surface, (self.x - self.size, self.y - self.size))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class ModernButton(Button):
    def __init__(self, x, y, width, height, text, color, theme):
        super().__init__(x, y, width, height, text, color)
        self.hover = False
        self.original_y = y
        self.animation_offset = 0
        self.particles = []
        self.theme = theme  # 儲存主題設定

    def draw(self, screen):
        # Shadow with theme support
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.theme['shadow'], 
                        (0, 0, self.rect.width, self.rect.height), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x, self.rect.y + 5))

        # Button with hover effect
        hover_offset = 3 if self.hover else 0
        pygame.draw.rect(screen, self.color, 
                        (self.rect.x, self.rect.y - hover_offset - self.animation_offset, 
                         self.rect.width, self.rect.height), 
                        border_radius=10)

        # Text with theme support
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, self.theme['text'])
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

        # Update particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)

    def handle_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def create_particles(self):
        for _ in range(10):
            self.particles.append(Particle(
                self.rect.centerx, 
                self.rect.centery, 
                self.color
            ))

class Train:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.width = 60
        self.height = 30
        self.moving = False
        self.move_direction = "left"
        
    def draw(self, screen, is_dark_mode=False):
        # Draw train body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=5)
        # Draw train chimney
        pygame.draw.rect(screen, (50, 50, 50), (self.x + 10, self.y - 10, 10, 10))
        
        # Draw train windows with light effect in dark mode
        window_color = (255, 255, 200) if is_dark_mode else (200, 200, 200)
        if is_dark_mode:
            # Add glow effect for windows in dark mode
            for window_x in [self.x + 25, self.x + 45]:
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 255, 0, 100), (10, 10), 8)
                screen.blit(glow_surf, (window_x - 5, self.y))
        
        # Draw windows
        pygame.draw.rect(screen, window_color, (self.x + 25, self.y + 5, 10, 10))
        pygame.draw.rect(screen, window_color, (self.x + 45, self.y + 5, 10, 10))
        
        # Draw train wheels
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 30), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 45, self.y + 30), 5)

    def move(self):
        if self.moving:
            if self.move_direction == "left":
                self.x -= 5
            elif self.move_direction == "right":
                self.x += 5
            # 火車移動出螢幕後停止
            if self.x + self.width < 0 or self.x > WIDTH:
                self.moving = False
        return self.moving

class Message:
    def __init__(self, text, color, duration=1.0):
        self.text = text
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 48)
        
    def should_remove(self):
        return (pygame.time.get_ticks() - self.start_time) > self.duration * 1000

    def draw(self, screen):
        alpha = 255 * (1 - (pygame.time.get_ticks() - self.start_time)/(self.duration * 1000))
        if alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text_surface, text_rect)

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

    def create_background(self):
        # Create a simple background with railroad tracks
        self.background.fill(self.theme['background'])
        # Draw railroad ties
        for x in range(0, WIDTH, 30):
            pygame.draw.rect(self.background, self.theme['track'], (x, 240, 20, 20))
        pygame.draw.line(self.background, self.theme['text'], (0, 235), (WIDTH, 235), 5)
        pygame.draw.line(self.background, self.theme['text'], (0, 265), (WIDTH, 265), 5)

    def add_message(self, text, color, duration=1.0):
        self.messages = [msg for msg in self.messages if not msg.should_remove()]
        self.messages.append(Message(text, color, duration))

    def reset_game(self):
        self.track_trains = []
        self.selection_trains = []
        self.score = 0
        self.current_train_index = 0  # 重置當前火車索引
        self.all_trains_moving = False  # 重置標誌
        self.initialize_trains()
        self.last_time = pygame.time.get_ticks()

    def create_buttons(self):
        self.start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game", self.theme['primary'])
        self.quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Quit", self.theme['error'])
        self.play_again_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Play Again", self.theme['primary'])

    def initialize_trains(self):
        # 初始化固定位置的十列火車
        self.train_positions = [i * 80 for i in range(10)]  # 十個固定位置
        self.track_trains = []
        for i in range(10):
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
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("Train Color Matcher", True, self.theme['text'])
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_text, title_rect)
        
        self.start_button.draw(screen)
        self.quit_button.draw(screen)

    def draw_game(self, screen):
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
        font = pygame.font.Font(None, 36)
        
        # 更新UI顯示
        remaining_trains = len(self.track_trains) - self.current_train_index
        progress_text = font.render(f'Remaining Trains: {remaining_trains}', True, self.theme['text'])
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])
        
        screen.blit(progress_text, (10, 10))
        screen.blit(score_text, (10, 40))
        
        self.mute_button.draw(screen)

    def draw_game_over(self, screen):
        font = pygame.font.Font(None, 64)
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

            # 更新移動中的火車
            for train in self.track_trains:
                if train.moving:
                    train.move()

            # 檢查是否所有火車都已移動完畢
            if self.all_trains_moving and all(not train.moving for train in self.track_trains):
                self.state = GAME_OVER
                self.high_score = max(self.high_score, self.score)

            # 更新消息
            self.messages = [msg for msg in self.messages if not msg.should_remove()]

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
        self.theme_button = ModernButton(WIDTH - 100, 10, 80, 40, "DARK", self.theme['button'], self.theme)
        self.all_trains_moving = False  # 新增：標誌所有火車是否正在移動
        self.instruction_text = "Match the trains starting from the left!"
        self.instruction_font = pygame.font.Font(None, 36)
        self.trees = [Tree(random.randint(50, WIDTH - 50), HEIGHT - 100) for _ in range(5)]
        self.clouds = [Cloud(random.randint(0, WIDTH), random.randint(50, 150)) for _ in range(3)]
        self.stars = [Star(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)) for _ in range(50)]

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.theme_button.text = "LIGHT" if self.dark_mode else "DARK"
        self.create_modern_buttons()
        self.create_background()

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
            for selection_train in self.selection_trains:
                if (selection_train.x < pos[0] < selection_train.x + selection_train.width and
                    selection_train.y < pos[1] < selection_train.y + selection_train.height):
                    clicked = True
                    
                    # 檢查是否還有火車需要配對
                    if self.current_train_index < len(self.track_trains):
                        current_train = self.track_trains[self.current_train_index]
                        
                        if selection_train.color == current_train.color:
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

    def create_modern_buttons(self):
        # Update buttons with emojis
        self.start_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50,
            "Start Game", self.theme['primary'], self.theme
        )
        self.quit_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50,
            "Quit", self.theme['error'], self.theme
        )
        self.play_again_button = ModernButton(
            WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50,
            "Play Again", self.theme['primary'], self.theme
        )

def main():
    # 初始化遊戲
    game = ModernGame()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Modern Train Color Game")
    
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