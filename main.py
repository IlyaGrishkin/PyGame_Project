from random import randint
import time

import pygame
import os
import sys
import random
import sqlite3

from map_logic import generate_map, read_map
from sprites.tank import Bullet, Tank, Turret  # , Turret
from sprites.zombie import Zombie, ZombieBoss
from sql import CREATE_RECORD_TABLE, GET_TOP_3_RECORDS, INSERT_RECORD

# инициализация Pygame
pygame.init()
size = width, height = 1080, 720
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 100
move_sound = pygame.mixer.Sound('data/move.wav')
health_upgrade = 0
speed_upgrade = 0
reload_upgrade = 0
cursor = sqlite3.connect('db.db')
cursor.execute(CREATE_RECORD_TABLE)
if True:
    from common import load_image


class Stopwatch:  # секундомер
    elapsed_time = 0
    start_time = 0
    is_running = False

    def turn_on(self):
        self.is_running = True
        if not self.start_time:
            self.start_time = pygame.time.get_ticks()
        else:
            self.elapsed_time += pygame.time.get_ticks() - self.start_time
            self.start_time = pygame.time.get_ticks()
        # return self.elapsed_time

    def turn_off(self):
        self.is_running = False
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = 0


def draw_cur_time(screen, stopwatch: Stopwatch):
    font = pygame.font.Font('./data/TeletactileRus.ttf', 40)
    text = font.render(f'{stopwatch.elapsed_time /
                       1000:.2f} сек', True, (255, 255, 255))
    text_x = 700
    text_y = 20
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (255, 255, 255), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)


def fon_screen(intro_text, level, stopwatch: Stopwatch):
    global health_upgrade, speed_upgrade, reload_upgrade
    stopwatch.turn_off()
    fon = pygame.transform.scale(load_image('start.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        pygame.draw.rect(screen, (152, 251, 152), (intro_rect.x - 10, intro_rect.y - 10,
                                                   intro_rect.width + 20, intro_rect.height + 20))
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif level != 0 and level != 3 and alive:
                if keys[pygame.K_1]:
                    health_upgrade += 1
                    return health_upgrade
                elif keys[pygame.K_2]:
                    speed_upgrade += 1
                    return
                elif keys[pygame.K_3]:
                    reload_upgrade += 1
                    return
            elif (level == 0 or level == 3 or not alive) and (event.type == pygame.KEYDOWN or
                                                              event.type == pygame.MOUSEBUTTONDOWN):
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


arrow_sprites = pygame.sprite.Group()


# прицел


class Arrow(pygame.sprite.Sprite):
    image = load_image("crosshair.png")

    def __init__(self):
        super().__init__(arrow_sprites)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = -100
        self.rect.y = -100

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y


if __name__ == '__main__':

    alive = True
    surf_alpha = pygame.Surface((width, height))
    pygame.mixer.music.load('data/soundtrack.mp3')
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)

    def level_run(level, stopwatch: Stopwatch):
        map_sprites = pygame.sprite.Group()
        water_sprites = pygame.sprite.Group()
        block_sprites = pygame.sprite.Group()
        tank_sprites = pygame.sprite.Group()
        turret_sprites = pygame.sprite.Group()
        bullet_sprites = pygame.sprite.Group()
        zombie_sprites = pygame.sprite.Group()
        zombieBoss_sprites = pygame.sprite.Group()
        zombies_list = list()
        # генерация карты и блоков
        level_file = 'level' + str(level) + '.txt'
        map_sprite, blocks, waters = generate_map(
            array=read_map(level_file),
            map_sprites=map_sprites,
        )

        block_sprites.add(*blocks)
        water_sprites.add(*waters)
        # базовые настройки
        pygame.display.set_caption('Танкокалипсис')
        running = True
        pygame.mouse.set_visible(False)

        # вызов спрайтов
        tank = Tank(tank_sprites, 300, 300, move_sound,
                    health_upgrade, speed_upgrade, reload_upgrade)
        turret = Turret(turret_sprites, tank=tank)
        arrow = Arrow()

        if level == 1:
            for i in range(23):
                zombie = Zombie(zombie_sprites, zombies_list, randint(300, 700), randint(
                    580, 630), speed=random.choice([1, 1.3]))
                zombies_list.append(zombie)
        elif level == 2:
            for i in range(7):
                zombie = Zombie(zombie_sprites, zombies_list, randint(450, 550), randint(
                    100, 180), speed=random.choice([1.1, 1.5]))
                zombies_list.append(zombie)
            for i in range(7):
                zombie = Zombie(zombie_sprites, zombies_list, randint(450, 550), randint(
                    580, 630), speed=random.choice([1.1, 1.5]))
                zombies_list.append(zombie)

        # игровой цикл
        while running:
            stopwatch.turn_on()
            keys = pygame.key.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if pygame.mouse.get_focused():
                    arrow.update(mouse_x, mouse_y)
                else:
                    arrow.rect.x = -100
                    arrow.rect.y = -100

            tank_sprites.update(keys, mouse_x, mouse_y, block_sprites,
                                turret, zombie_sprites, water_sprites, speed_upgrade, zombie_boss_sprites=zombieBoss_sprites)
            # отрисовка карты
            map_sprite.draw(surf_alpha)

            # отрисовка игровых объектов
            screen.blit(surf_alpha, (0, 0))
            global draw_cur_time
            draw_cur_time(screen, stopwatch=stopwatch)
            for zombie in zombie_sprites:
                screen.blit(zombie.surf, zombie.rect)

            screen.blit(tank.surf, tank.rect)
            screen.blit(turret.surf, turret.rect)
            tank.draw_hp(screen)
            tank.show_cooldown(screen)
            if tank.bullet_info:
                bullet = Bullet(bullet_sprites, *tank.bullet_info)
            for bullet in bullet_sprites:
                screen.blit(bullet.surf, bullet.rect)
            bullet_sprites.update(block_sprites, clock)

            map_sprite.update()
            zombie_sprites.update(bullet_sprites, tank,
                                  block_sprites, water_sprites)
            zombieBoss_sprites.update(bullet_sprites, tank,
                                      block_sprites, water_sprites, zombies_list, zombie_sprites)
            arrow_sprites.draw(screen)
            if tank.hp <= 0:
                intro_text = ["Танкокалипсис",
                              "О нет",
                              "ты проиграл!"]
                global alive
                alive = False
                fon_screen(intro_text, level, stopwatch=stopwatch)
                running = False
            elif not zombies_list:
                intro_text = ["Танкокалипсис",
                              "Уровень пройден!!!",
                              "Выбери усиление:",
                              "1 - Увеличить прочность",
                              "2 - Увеличить скорость",
                              "3 - Увеличить скорость перезарядки"]
                fon_screen(intro_text, level, stopwatch=stopwatch)
                running = False
            pygame.display.flip()
            clock.tick(fps)

    def run_boss_level(stopwatch: Stopwatch):
        stopwatch.turn_on()
        map_sprites = pygame.sprite.Group()
        water_sprites = pygame.sprite.Group()
        block_sprites = pygame.sprite.Group()
        tank_sprites = pygame.sprite.Group()
        turret_sprites = pygame.sprite.Group()
        bullet_sprites = pygame.sprite.Group()
        zombie_sprites = pygame.sprite.Group()
        zombieBoss_sprites = pygame.sprite.Group()
        zombies_list = list()
        # генерация карты и блоков
        level_file = 'level' + '3' + '.txt'
        map_sprite, blocks, waters = generate_map(
            array=read_map(level_file),
            map_sprites=map_sprites,
        )

        block_sprites.add(*blocks)
        water_sprites.add(*waters)
        # базовые настройки
        pygame.display.set_caption('Танкокалипсис')
        running = True
        pygame.mouse.set_visible(False)

        # вызов спрайтов
        tank = Tank(tank_sprites, 300, 300, move_sound,
                    health_upgrade, speed_upgrade, reload_upgrade)
        turret = Turret(turret_sprites, tank=tank)
        arrow = Arrow()

        for i in range(3):
            zombie = Zombie(zombie_sprites, zombies_list, randint(100, 700), randint(
                550, 600), speed=random.choice([1.2, 1.7]))
            zombies_list.append(zombie)
        zombie_boss = ZombieBoss(zombieBoss_sprites, 700, 380, 1)
        # zombies_list.append(zombie_boss)

        # intro_text = ["Танкокалипсис", "", "", "",
        #               "Правила игры:",
        #               "Уничтожь всех зомби на уровне!",
        #               "Не дай зомби к тебе прикоснуться"]
        # fon_screen(intro_text)

        # игровой цикл
        while running:

            keys = pygame.key.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if pygame.mouse.get_focused():
                    arrow.update(mouse_x, mouse_y)
                else:
                    arrow.rect.x = -100
                    arrow.rect.y = -100

            tank_sprites.update(keys, mouse_x, mouse_y, block_sprites,
                                turret, zombie_sprites, water_sprites, speed_upgrade, zombie_boss_sprites=zombieBoss_sprites)
            # отрисовка карты
            map_sprite.draw(surf_alpha)

            # отрисовка игровых объектов
            screen.blit(surf_alpha, (0, 0))
            for zombie in zombie_sprites:
                screen.blit(zombie.surf, zombie.rect)

            screen.blit(zombie_boss.surf, zombie_boss.rect)
            screen.blit(tank.surf, tank.rect)
            screen.blit(turret.surf, turret.rect)
            tank.draw_hp(screen)
            zombie_boss.draw_hp(screen)
            tank.show_cooldown(screen)
            if tank.bullet_info:
                bullet = Bullet(bullet_sprites, *tank.bullet_info)
            for bullet in bullet_sprites:
                screen.blit(bullet.surf, bullet.rect)
            bullet_sprites.update(block_sprites, clock)

            map_sprite.update()
            zombie_sprites.update(bullet_sprites, tank,
                                  block_sprites, water_sprites)
            zombieBoss_sprites.update(bullet_sprites, tank,
                                      block_sprites, water_sprites, zombies_list, zombie_sprites)
            arrow_sprites.draw(screen)
            if tank.hp <= 0:
                intro_text = ["Танкокалипсис",
                              "О нет",
                              "ты проиграл!"]
                fon_screen(intro_text, 3, stopwatch=stopwatch)
                running = False
            elif not zombies_list and zombie_boss.killed:
                intro_text = ["Танкокалипсис",
                              "Поздравляем, ты прошел игру!!!"]
                fon_screen(intro_text, health_upgrade, stopwatch=stopwatch)
                running = False
            pygame.display.flip()
            clock.tick(fps)

    intro_text = ["Танкокалипсис",
                  "Правила игры:",
                  "Уничтожь всех зомби на уровне!",
                  "Не дай зомби к тебе прикоснуться",
                  "Движение - W, A, S, D",
                  "Стрельба - ЛКМ"]

    stopwatch = Stopwatch()
    fon_screen(intro_text, 0, stopwatch=stopwatch)
    level_run(1, stopwatch)

    arrow_sprites = pygame.sprite.Group()
    if alive:
        level_run(2, stopwatch=stopwatch)
    else:
        time_end = pygame.time.get_ticks()

    arrow_sprites = pygame.sprite.Group()
    if alive:
        run_boss_level(stopwatch=stopwatch)
        cursor.execute(INSERT_RECORD.format(
            time=f'{stopwatch.elapsed_time / 1000:.2f} сек'))
        cursor.commit()
    res = cursor.execute(GET_TOP_3_RECORDS).fetchall()
    cursor.close()

    print(res)
