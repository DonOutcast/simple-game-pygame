import pygame
from game_sprites import *
from graphics_config import *

def get_platform(p):
    x = p[0]
    y = p[1]
    area = pygame.Rect(x, y, p[2], p[3])
    length = p[4]
    x_speed = p[5] 
    y_speed = p[6]
    return (length, x, y, area, x_speed, y_speed)

class Level():
    ''' каждый экземпляр этого класса - это описание одного уровня
    для описания игры нужно в файле level_config создавать экземпляры Level()
    и добавлять в них методами add и set нужную информацию. 
    '''
    def __init__(self):
        self.platforms = []
        self.enemies = []
        self.goal = [] # цель уровня (картинка и координаты спрайта)
        self.hero_x = 0 # координаты, в которых появляется игрок
        self.hero_y = 0
        self.background_img = '' # картинка фона уровня
        self.min_x = 0 # левая граница уровня
        self.max_x = 0 # правая граница уровня (герой дальше пройти не сможет)

    def set_back(self, filename):
        self.background_img = filename

    def add_platform(self, x, y, w, h, length, x_speed, y_speed):
        ''' добавляем в описание уровня платформу'''
        p = [x, y, w, h, length, x_speed, y_speed]
        self.platforms.append(p)

    def add_enemy(self, enemy_type, x, y, x_min, x_max, x_speed):
        ''' тип врага будет определять, какая у него картинка'''
        e = [enemy_type, x, y, x_min, x_max, x_speed]
        self.enemies.append(e)

    def set_hero(self, x, y):
        self.hero_x = x
        self.hero_y = y
    
    def set_goal(self, x, y):
        self.goal = [x, y]

    def load_back(self):
        game.set_back(self.background_img)

    def load_platforms(self):
        for p in self.platforms:
            Platform(*get_platform(p))

    def load_enemies(self):
        # img = generate_image(3, 3, C_WHITE) # Оставляем временно стандартную картинку 
        img = game.costumes[gr_enemy]
        for enemy_info in self.enemies:
            # (enemy_type, x, y, x_min, x_max, x_speed)
            enemy_type = enemy_info[0]
            x, y, x_min, x_max, x_speed = enemy_info[1], enemy_info[2], enemy_info[3], enemy_info[4], enemy_info[5]
            area = pygame.Rect(x_min, 0, x_max - x_min, win_height)
            if enemy_type == 1:
                Enemy2(img, x, y, area, x_speed=x_speed) 
            else:
                Enemy1(img, x, y, area, x_speed=x_speed) 

    def load_goal(self):
        Goal(self.goal[0], self.goal[1])

    def load_hero(self):
        # img = generate_image(3, 3, C_YELLOW) # Оставляем тут временно стандартную картинку для героя
        img = game.costumes[gr_hero]
        x = self.hero_x 
        y = self.hero_y
        area = pygame.Rect(self.min_x, -win_height, self.max_x, 2 * win_height)
        return Hero(img, x, y, area)

    def load(self):
        self.load_back()
        self.load_platforms()
        self.load_enemies()
        self.load_goal()
        return self.load_hero()