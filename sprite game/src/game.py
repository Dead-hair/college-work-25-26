import pygame
from src.settings import *
from src.base import Base
from src.units import Swordsman, Archer, Catapult
from src.player import Player
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle of Bases")
        self.clock = pygame.time.Clock()
        self.running = True

        # Шрифт для отображения HP
        self.font = pygame.font.SysFont("Arial", 24)

        # Загрузка и масштабирование фона
        bg_path = os.path.join("assets", "background", "i.jpeg")
        self.background = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Загрузка и масштабирование изображения замков
        base_player_path = os.path.join("assets", "sprites", "base", "player_castle.png")
        self.base_player_img = pygame.image.load(base_player_path).convert_alpha()
        self.base_player_img = pygame.transform.scale(self.base_player_img, (200, 200))

        base_enemy_path = os.path.join("assets", "sprites", "base", "enemy_castle.png")
        self.base_enemy_img = pygame.image.load(base_enemy_path).convert_alpha()
        self.base_enemy_img = pygame.transform.scale(self.base_enemy_img, (200, 200))

        # Загрузка кнопки
        button_path = os.path.join("assets", "ui", "button_buy_swordsman.png")
        self.button_img = pygame.image.load(button_path).convert_alpha()
        self.button_img = pygame.transform.scale(self.button_img, (200, 80))  # масштабируем после загрузки
        self.button_rect = self.button_img.get_rect()
        self.button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Инициализация игроков и баз (будут создаваться при старте игры)
        self.player = None
        self.enemy_base = None
        self.player_base = None

        # Состояние игры: меню или игра
        self.state = 'menu'  # 'menu' или 'playing'

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.state == 'menu':
                    if self.button_rect.collidepoint(mouse_pos):
                        self.start_game()

    def start_game(self):
        # Инициализация игровых объектов при старте игры
        self.player = Player()
        self.enemy_base = Base(BASE_HP)  # BASE_HP должен быть 1000 или задан в настройках
        self.player_base = Base(BASE_HP)
        self.state = 'playing'

    def update(self):
        if self.state == 'playing':
            # Обновление состояния игры (пока пусто)
            pass

    def draw_hp_bar(self, base, x, y, width=200, height=20):
        # Рисуем рамку полоски HP
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height), 2)

        # Вычисляем ширину заполненной части полоски в зависимости от текущего HP
        fill_width = int((base.hp / 1000) * (width - 4))  # -4 для учета рамки

        # Рисуем саму полоску (зелёную)
        pygame.draw.rect(self.screen, (0, 255, 0), (x + 2, y + 2, fill_width, height - 4))

        # Рисуем текст HP сверху
        hp_text = self.font.render(f'HP: {base.hp} / 1000', True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(hp_text, text_rect)

    def draw_menu(self):
        self.screen.fill((0, 0, 0))  # Черный фон или можно фоновое изображение
        self.screen.blit(self.button_img, self.button_rect)
        pygame.display.flip()

    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.screen.blit(self.background, (0, 0))

            player_width = self.base_player_img.get_width()
            player_height = self.base_player_img.get_height()
            enemy_width = self.base_enemy_img.get_width()
            enemy_height = self.base_enemy_img.get_height()

            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2

            offset = (SCREEN_WIDTH // 2) - 50 - (player_width // 2)

            player_x = center_x - offset - player_width // 2
            player_y = center_y - player_height // 2

            enemy_x = center_x + offset - enemy_width // 2
            enemy_y = center_y - enemy_height // 2

            # Отрисовка замков
            self.screen.blit(self.base_player_img, (player_x, player_y))
            self.screen.blit(self.base_enemy_img, (enemy_x, enemy_y))

            # Отрисовка HP баров над замками (немного выше замка)
            hp_bar_y_offset = 30
            self.draw_hp_bar(self.player_base, player_x, player_y - hp_bar_y_offset)
            self.draw_hp_bar(self.enemy_base, enemy_x, enemy_y - hp_bar_y_offset)

            pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

