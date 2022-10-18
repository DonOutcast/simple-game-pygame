import pygame
from base_sprites import *
from level import *
from gamesingle import game
from takeimages import *
from random import randint

class Platform(BaseSprite):
    ''' класс для платформы - это BaseSprite с изображением платформы, растянутым на нужно число клеток.  '''
    def __init__(self, length, x, y, area, x_speed=0, y_speed=0):
        ''' получает длину платформы, генерирует нужной длины картинку'''
        img_l = game.costumes[gr_plat_l]
        img_m = game.costumes[gr_plat_m]
        img_r = game.costumes[gr_plat_r]        
        image = append_img3(img_l, img_m, img_r, length)

        # создаем BaseSprite с нужным 
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed)
        game.add_barrier(self)

class Goal(BaseSprite):
    ''' класс для цели - это BaseSprite '''
    def __init__(self, x, y, x_speed=0, y_speed=0):
        ''' картинка - костюм цели '''
        image = game.costumes[gr_goal]
        area = pygame.Rect(0, 0, win_width, win_height)
        # создаем BaseSprite  
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed)
        game.add_goal(self) # регистрируемся как цель

class Fire(Character):
    ''' Снаряды - могут двигаться, как платформы
    при этом получат возможность анимации, если её прописать в Character
    умирают, пролетев определенное расстояние'''
    def __init__(self, image, x, y, area, x_speed=0, graph_index=gr_fire):
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=0, die_x=True, die_y=False, heavy=0, graph_index=graph_index)
        # снаряд имеет начальную скорость только по x, не подвержен гравитации,
        # исчезает, как только пролетел нужную дистанцию

class Actor(Character):
    ''' персонажи, которые могут действовать сами (в отличие от снарядов) '''
    def stop(self):
        self.x_speed = 0

    def move(self, x):
        self.x_speed = self.direction * x

    def move_left(self, x):
        self.direction = -1
        self.move(x)

    def move_right(self, x):
        self.direction = 1
        self.move(x)

    def jump(self, y):
        if self.stands_on:
            self.y_speed = y

    def fire(self, img, is_Enemy):
        rect = img.get_rect() # приложим прямоугольник для снаряда с нужной стороны того, кто стреляет: 
        rect.y = self.rect.centery # это можно менять в зависимости от соотношения картинок
        if self.direction > 0:
                rect.left = self.rect.right
                area = pygame.Rect(rect.left, rect.top, FIRE_DISTANCE, win_height-rect.top)
                f_speed = FIRE_SPEED
        else:
                rect.right = self.rect.left
                area = pygame.Rect(rect.right - FIRE_DISTANCE, rect.top, FIRE_DISTANCE, win_height-rect.top)
                f_speed = -1 * FIRE_SPEED
        if is_Enemy:
            game.add_enemy(Fire(img, rect.x, rect.y, area, f_speed, graph_index=gr_enemyfire)) # создаем снаряд с вычисленными параметрами 
                                                                   # и прописываем как врага
        else:
            game.add_fire(Fire(img, rect.x, rect.y, area, f_speed)) # создаем снаряд с вычисленными параметрами 
              # и сразу прописываем как снаряд (методом класса Game, который запишет во все нужные)


class Enemy(Actor):
    ''' Полноценный персонаж.
    Прописывается в список врагов. Его снаряды прописываются в список врагов.
    Умирает от снарядов героя.'''
    def __init__(self, image, x, y, area, x_speed=0, y_speed=0, die_x=False, die_y=True, heavy=GRAVITY, graph_index=gr_enemy):
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed, die_x=die_x, die_y=die_y, heavy=heavy, graph_index=graph_index)
        game.enemies.add(self)
        game.all_sprites.add(self)

    def fire(self):
        img = game.costumes[gr_enemyfire] #generate_image(1, 1, C_WHITE) # тут нужна картинка для снаряда врага
        super().fire(img, True)

    def update(self):
        ''' двигается как обычный персонаж, при касании со снарядами героя - умирает '''
        super().update()
        fires_touched = pygame.sprite.spritecollide(self, game.fires, True)
        if fires_touched:
            self.die()

class Hero(Actor):
    ''' Главный персонаж. Умирает от врагов. Снаряды добавляет в список, убивающий врагов. '''
    def fire(self):
        img = game.costumes[gr_fire] #generate_image(1, 1, C_DARK) # тут нужна картинка для снаряда героя
        super().fire(img, False)
    
    def update(self):
        super().update()
        enemies_touched = pygame.sprite.spritecollide(self, game.enemies, False)
        if enemies_touched:
            self.die()
    
    def die(self):
        game.minus_lives()
        super().die()

class Enemy1(Enemy):
    ''' враг вида 1, умеет стрелять '''
    def __init__(self, image, x, y, area, x_speed=0, y_speed=0, die_x=False, die_y=True, heavy=GRAVITY, graph_index=gr_enemy):
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed, die_x=die_x, die_y=die_y, heavy=heavy, graph_index=graph_index)
        if self.x_speed == 0:
            self.change_dir()

    def update(self):
        ''' добавим стрельбу с некоторой вероятностью, если спрайт виден на экране:'''
        super().update()
        if self.rect.x > 0 and self.rect.x < win_width:
            f = randint(1, 150)
            if f < 2:
                game.music.evil_fire()
                self.fire()

    def die(self):
        game.change_points(2)
        super().die()

class Enemy2(Enemy):
    ''' враг вида 2, не умеет стрелять '''
    def __init__(self, image, x, y, area, x_speed=0, y_speed=0, die_x=False, die_y=True, heavy=GRAVITY, graph_index=gr_enemy2):
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed, die_x=die_x, die_y=die_y, heavy=heavy, graph_index=graph_index)

    def die(self):
        game.change_points()
        super().die()
