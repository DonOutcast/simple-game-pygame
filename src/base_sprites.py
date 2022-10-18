import pygame
from constants import *
from gamesingle import game

class BaseSprite(pygame.sprite.Sprite):
    ''' базовый класс для персонажа игры
    image - картинка персонажа (готовый pygame surface!)
    x, y - место появления (левый верхний угол)
    x_speed, y_speed - скорость - число  пикселей (по горизонтали и по вертикали), 
    которой спрайт проходит за один раз
    area - "место обитания" - готовый прямоугольник (pygame rect), внутри которого спрайт должен оставаться
     '''
    # конструктор :
    def __init__(self, image, x, y, area, x_speed=0, y_speed=0):
        # Вызываем конструктор класса (Sprite):
        super().__init__()

        # каждый спрайт должен хранить свойство image - картинка. Берем переданную сюда:
        self.image = image
        # каждый спрайт должен хранить свойство rect - прямоугольник. Это свойство нужно для определения касаний спрайтов. 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # эти свойства просто запоминаем:       
        self.area = area
        self.x_speed = x_speed
        self.y_speed = y_speed
        # для тех, кто смещается вместе с этим спрайтом, нужно знать, насколько спрайту удалось 
        # переместиться за последний update:
        self.x_changed = 0
        self.y_changed = 0        
        # направление: вправо = 1, влево = -1 :       
        self.direction = 1
        if self.x_speed < 0:
            self.direction = -1

    def change_dir(self): 
        self.x_speed *= -1
        self.direction *= -1 

    def change_ydir(self): 
        self.y_speed *= -1

    def outside(self):
        ''' проверяет, не вышел ли спрайт за пределы отведенного ему ареала'''
        return not self.area.contains(self.rect)

    def update(self):
        ''' метод изменения позиции; может вызываться из группы спрайтов
        сначала применяет изменение по x, 
        проверяет, не надо ли подкорректировать
        потом применяет изменение по y и тоже проверяет'''
        self.rect.x += self.x_speed
        self.x_changed = self.x_speed

        if self.outside():
            self.rect.x -= self.x_speed
            self.x_changed = 0
            self.change_dir()

        self.rect.y += self.y_speed
        self.y_changed = self.y_speed
        if self.outside():
            self.rect.y -= self.y_speed
            self.y_changed = 0
            self.change_ydir()

class Character(BaseSprite):
    ''' Игровые персонажи'''
    def __init__(self, image, x, y, area, x_speed=0, y_speed=0, die_x=False, die_y=True, heavy=GRAVITY, graph_index=gr_hero):
        ''' дополнительные параметры: что делать при выходе их ареала, сила притяжения 
        heavy - число пикселей, на которые персонаж падает вниз
        die_x - умирает ли персонаж, если оказывается вне ареала по x (снаряды умирают)
        die_y - умирает ли персонаж, если оказывается ВНИЗУ ареала 
        (считаем, что вверху никогда не умирает, просто возвращается вниз)'''
        # конструктор базового класса:
        super().__init__(image, x, y, area, x_speed=x_speed, y_speed=y_speed)
        # старое направление движения:
        self.old_direction = 0
        # эти свойства просто запоминаем:       
        self.die_x = die_x
        self.die_y = die_y
        self.heavy = heavy
        self.graph_index = graph_index
        # здесь будет ссылка на платформу, на которой стоит персонаж:
        self.stands_on = False

    def check_dir(self):
        ''' проверяет, поменялось ли направление. Подкачивает новую картинку, если да.'''
        if self.old_direction != self.direction:
            if self.direction > 0:
                self.image = game.costumes[self.graph_index]
            else:
                self.image = game.costumes[self.graph_index + gr_total] # вторая копия списка содержит зеркальные копии
        self.old_direction = self.direction # обработали и запомнили

    def gravitate(self):
        self.y_speed += self.heavy

    def die(self):
        ''' убивает персонажа '''
        self.kill() # можно поменять на анимацию гибели персонажа!

    def update(self):
        ''' метод изменения позиции
        первым делом проверяет, не заехали ли на место персонажа платформы (пока он "стоял")
        перемещения всех таких платформ двигают и персонажа тоже 
        применяет гравитацию
        применяет изменения по x и по y
        после изменений по x проверяет, не зашел ли за барьеры и за "ареал"
        после изменений по y то же самое, но может оказаться, что приземлился на барьер'''

        # 1. Для совместимости с базовым классом тоже будем подсчитывать x_changed и y_changed:
        old_x = self.rect.x
        old_y = self.rect.y

        # 2. Покатаем спрайт со всеми платформами, которые на него успели заехать до его изменений,
        # в том числе и той, на которой он стоит:
        # 2A. Применяем изменения координат платформ, которых коснулись.
        platforms_touched = pygame.sprite.spritecollide(self, game.barriers, False)
        for p in platforms_touched:
            self.rect.x += p.x_changed
            self.rect.y += p.y_changed
        # 2Б. Платформы, на которой персонаж стоит, он может не касаться, но она должна двигать персонажа точно так же:
        if self.stands_on and self.stands_on not in platforms_touched:
            p = self.stands_on
            self.rect.x += p.x_changed
            self.rect.y += p.y_changed
        # 2В. Если после всех этих преобразований персонаж все еще кого-то касается, значит, его раздавило! 
        platforms_touched = pygame.sprite.spritecollide(self, game.barriers, False)
        if len(platforms_touched) > 0:
            self.die()

        # 3. Применим гравитацию.  
        self.gravitate()  
        # теперь в x_speed и y_speed те изменения, которые нужно применить

        # 4. Теперь движение самого спрайта. Сначала учитываем изменение по x:
        self.rect.x += self.x_speed

        # 4А. Если зашли за стенку, то встанем вплотную к стене
        platforms_touched = pygame.sprite.spritecollide(self, game.barriers, False)
        if self.x_speed > 0: # идем направо, правый край персонажа - вплотную к левому краю стены
            for p in platforms_touched:
                self.rect.right = min(self.rect.right, p.rect.left) # если коснулись сразу нескольких, то правый край - минимальный из возможных
        elif self.x_speed < 0: # идем налево, ставим левый край персонажа вплотную к правому краю стены
            for p in platforms_touched:
                self.rect.left = max(self.rect.left, p.rect.right) # если коснулись нескольких стен, то левый край - максимальный

        # 4Б. Проверяем, не вышли ли за пределы ареала:
        if self.outside():
            if self.die_x:
                self.die()
            else:
                self.rect.x -= self.x_speed
                self.change_dir()

        # 5. Теперь изменения по y:
        self.rect.y += self.y_speed

        # 5А. Проверим, не ушли ли с платформы, на которой стояли:
        if self.stands_on:
            if (
                self.y_speed < 0  # оттолкнулись от платформы и ушли на y_speed относительно неё
                or self.rect.right < self.stands_on.rect.left # оказались левее левого края опоры 
                or self.rect.left > self.stands_on.rect.right # оказались правее опоры
            ):
                self.stands_on = False # больше ни на чем не стоим

        # 5Б. Проверим, не коснулись ли платформ:

        platforms_touched = pygame.sprite.spritecollide(self, game.barriers, False)

        if self.y_speed > 0: # идем вниз
            for p in platforms_touched:
                if self.heavy > 0:
                    self.y_speed = 0 # при касании с препятствием по y вертикальная скорость пропадает:
                # персонаж, который управляется не гравитацией, а "ареалом", продолжает попытки пройти

                # проверяем, какая из платформ снизу самая высокая, выравниваемся по ней, запоминаем её как свою опору:
                if p.rect.top < self.rect.bottom: 
                    self.rect.bottom = p.rect.top
                    self.stands_on = p

        elif self.y_speed < 0: # идем вверх
            self.stands_on = False # пошли наверх, значит, ни на чем уже не стоим!
            for p in platforms_touched:
                if self.heavy > 0:
                    self.y_speed = 0 # при касании с препятствием по y вертикальная скорость пропадает:
                self.rect.top = max(self.rect.top, p.rect.bottom) # выравниваем верхний край по нижним краям стенок, на которые наехали

        # 5В. Проверка выхода за пределы ареала:

        if self.outside():
            if self.die_y and self.rect.bottom > self.area.bottom:
                # провалились вниз:
                self.die() 
            else:
                self.rect.y -= self.y_speed
                self.change_ydir()

        # 6. Запомнили изменения (завершение п.1):
        self.x_changed = old_x - self.rect.x
        self.y_changed = old_y - self.rect.y 

        # 7. Отображает зеркально, если нужно:
        self.check_dir()

