import pygame

from constants import *
from level import *
from level_config import *

from game_sprites import *
from gamesingle import game


game.start()
hero = game.start_level(0)

game.show_menu()

# На UBUNTU сборка pygame содержит ошибку, из-за которой не распознаются нажатые буквы...
# Это обходится проверкой поля unicode, но такого поля нет у события KEYUP. 
# Поэтому будем получать у системы коды нужных букв по их нажатию и сохранять.
# Заводим нужные переменные (буквы, отжатие которых обязательно отслеживать):

key_a = pygame.K_a
key_d = pygame.K_d
key_h = pygame.K_h # режим help включается по отжатию клавиши h 




while game.run:
    # Ввод данных (обработка событий)
    for event in pygame.event.get():
        #событие нажатия на крестик окошка
        if event.type == pygame.QUIT:
            game.stop() # цикл перестанет повторяться, программа завершится
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                hero.move_left(HERO_STEP)
            elif event.unicode == 'a':
                hero.move_left(HERO_STEP)
                key_a = event.key
            elif event.key == pygame.K_RIGHT:
                hero.move_right(HERO_STEP)
            elif event.unicode == 'd':
                hero.move_right(HERO_STEP)
                key_d = event.key
            elif event.key == pygame.K_UP or event.unicode == 'w':
                hero.jump(HERO_JUMP)
            elif event.unicode == 'h':
                key_h = event.key
            elif event.unicode == 'm':
                game.music.change()
            elif event.unicode == 'u':
                game.music.volume_up()
            elif event.unicode == 'j':
                game.music.volume_down()
            elif event.key == pygame.K_SPACE:
                game.music.good_fire()
                hero.fire()
            elif event.key == pygame.K_q:
                game.stop()

        elif event.type == pygame.KEYUP:
            if game.is_help:
                game.resume()
            else:
                if event.key == pygame.K_LEFT or event.key == key_a:
                    hero.stop()
                elif event.key == pygame.K_RIGHT or event.key == key_d:
                    hero.stop()
                elif event.key == key_h:
                    game.show_menu()

    if game.in_game():
        # Вычисления:
        game.all_sprites.update()  # перемещение игровых объектов, 

        # Если нужно, переместим камеру перед окончательной отрисовкой спрайтов: 
        if hero.rect.left < win_leftbound or hero.rect.right > win_rightbound:
            offset_x = game.hero_pos.x - hero.rect.x
            game.camera.move(offset_x, 0, game.all_sprites)
        # запоминаем место героя, чтобы крутить камеру относительно него:
        game.hero_pos.x = hero.rect.x
        game.hero_pos.y = hero.rect.y

        # Вывод данных (отрисовка)
        game.draw_back_with_shift()
        game.window.blit(game.help.line(points=game.points, lives=game.lives), (0, 10))
        game.all_sprites.draw(game.window)

    pygame.display.update()
    if game.goal_touched(hero):
        game.next_level()

    if hero not in game.all_sprites: # Проиграли!
        if game.lives > 0:
            # перезапуск уровня:
            game.timer.tick(1)
            hero = game.restart_level()
        else:
            game.lose()

    # Пауза
    game.timer.tick(FPS)

