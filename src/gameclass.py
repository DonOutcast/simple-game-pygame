import pygame
from constants import *
from graphics_config import *
from game_help import *
from game_music import *

class Camera():
    def __init__(self):
        self.rect = pygame.Rect(0, 0, win_width, win_height)
        # положение камеры относительно всего большого уровня (может влиять на рисунок фона)

    def move(self, offset_x, offset_y, group):
        ''' смещение камеры относительно уровня '''
        self.rect.move_ip(-1 * offset_x, -1 * offset_y)
        for s in group:
            s.rect.move_ip(offset_x, offset_y)
            s.area.move_ip(offset_x, offset_y)
    
    def back_shift(self):
        ''' возвращает число от 0 до win_width, на которое по оси X надо сдвинуть фон '''
        # return self.rect.x % win_width 
        # попробуем сдвигать фон в 2 раза медленнее, чем движется камера.
        # тогда должна возникнуть глубина:
        return (self.rect.x // 2) % win_width 

class Game():
    def __init__(self):
        self.run = True
        # список всех персонажей игры:
        self.all_sprites = pygame.sprite.Group()
        # список опор (платформ):
        self.barriers = pygame.sprite.Group()
        # список врагов:
        self.enemies = pygame.sprite.Group()
        # список снарядов героя (убивают врагов):
        self.fires = pygame.sprite.Group()
        # список целей (переключают на следующий уровень):
        self.goals = pygame.sprite.Group()
        # в игре одна камера, из которой смотрим:
        self.camera = Camera()
        self.hero_pos = pygame.Rect(0, 0, 0, 0) # здесь запоминаем место героя на предыдущем цикле
        # список уровней игры:
        self.levels = []  # этот список заполнится при загрузке уровней (level_config)
        self.current_level = -1
        # список используемых костюмов:
        self.costumes = []
        # переменные для числа очков и жизней:
        self.lives = HERO_START_LIVES
        self.points = 0

    def start(self):
        pygame.init()
        self.timer = pygame.time.Clock()
        pygame.display.set_caption("DINO")
        self.window = pygame.display.set_mode([win_width, win_height])
        self.costumes = file_images()
        self.help = Help()
        self.is_help = False
        self.is_finished = False
        self.music = Music()
        self.back_image = pygame.Surface([win_width, win_height])
        self.back_image.fill(C_GREEN) # по умолчанию фон - зелёный прямоугольник

    def set_back(self, filename):
        if len(filename) > 0: # если в уровне не прописан фон, то соотв. свойство - пустая строка
            self.back_image = pygame.transform.scale(pygame.image.load(filename).convert(), [win_width, win_height])
        else:
            self.back_image = pygame.Surface([win_width, win_height])
            self.back_image.fill(C_GREEN) # по умолчанию фон - зелёный прямоугольник

    def clear(self):
        for s in self.all_sprites: 
            s.kill()
        self.camera = Camera()
        self.hero_pos = pygame.Rect(0, 0, 0, 0) 
    
    def start_level(self, level_no):
        self.current_level = level_no
        hero_of_the_level = self.levels[level_no].load()
        self.all_sprites.add(hero_of_the_level)
        self.hero_pos = hero_of_the_level.rect.copy()

        return hero_of_the_level # возвращает спрайт героя

    def restart_level(self):
        self.clear()
        return self.start_level(self.current_level) # возвращает спрайт героя

    def next_level(self):
        ''' переключает на следующий уровень, если он есть, а если нет - то вызывает метод "победа" '''
        if self.current_level + 1 >= len(self.levels): 
            # следующего уровня нет
            self.win_game()
        else:
            self.current_level += 1
            self.restart_level()

    def draw_back(self, x=0, y=0):
        ''' заливает окно фоновым изображением'''
        self.window.blit(self.back_image, (x, y))

    def draw_back_with_shift(self):
        local_shift = self.camera.back_shift()
        self.draw_back(local_shift)
        if local_shift != 0:
            self.draw_back(local_shift - win_width + 1) # сдвиг на 1 пиксел позволяет некоторые картинки "склеить" лучше 

    def end_game(self):
        ''' вызывается после победы или поражения'''
        self.is_finished = True
        self.clear()
        self.draw_back()

    def win_game(self):
        ''' победа'''
        # картинка победы:
        self.set_back(background_win)
        self.end_game()
        

    def lose(self):
        # картинка проигрыша:
        self.set_back(background_fail)
        self.end_game()

    def stop(self):
        self.run = False

    def in_game(self):
        ''' проверяет флаги, которые останавливают игру. 
        Если не вызвался метод "старт", то флагов не будет, сгенерируется ошибка (это ок, невозможно быть в игре до её старта)'''
        return not (self.is_help or self.is_finished) 

    def goal_touched(self, hero):
        goals_touched = pygame.sprite.spritecollide(hero, self.goals, False)
        if len(goals_touched) > 0:
            return True
        return False

    def add_barrier(self, platform):
        self.barriers.add(platform)
        self.all_sprites.add(platform)

    def add_enemy(self, enemy):
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def add_fire(self, fire):
        self.fires.add(fire)
        self.all_sprites.add(fire)

    def add_goal(self, goal):
        self.goals.add(goal)
        self.all_sprites.add(goal)

    def show_menu(self):
        w = win_width / 8
        h = win_height / 8
        self.window.blit(self.help.img, (w, h))
        self.is_help = True
    
    def resume(self):
        self.is_help = False

    def change_points(self, change=1):
        self.points += change
    
    def minus_lives(self, change=1):
        self.lives -= change
