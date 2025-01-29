from random import randint

import pygame
import os
import sys
import random

from map_logic import generate_map, read_map
from sprites.tank import Bullet, Tank, Turret  # , Turret
from sprites.zombie import Zombie

arrow_sprites = pygame.sprite.Group()
map_sprites = pygame.sprite.Group()
water_sprites = pygame.sprite.Group()
block_sprites = pygame.sprite.Group()
tank_sprites = pygame.sprite.Group()
turret_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
zombie_sprites = pygame.sprite.Group()

# инициализация Pygame
pygame.init()
size = width, height = 1080, 720
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 100
if True:
    from common import load_image


def terminate():
    pygame.quit()
    sys.exit()


def fon_screen(intro_text):
    fon = pygame.transform.scale(load_image('start.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


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


intro_text = ["Танкокалипсис", "", "", "",
              "Правила игры:",
              "Уничтожь всех зомби на уровне!",
              "Не дай зомби к тебе прикоснуться"]
fon_screen(intro_text)
if __name__ == '__main__':

    surf_alpha = pygame.Surface((width, height))

    # генерация карты и блоков
    map_sprite, blocks, waters = generate_map(
        array=read_map('level1.txt'),
        map_sprites=map_sprites,
    )

    block_sprites.add(*blocks)
    water_sprites.add(*waters)
    # базовые настройкиas
    pygame.display.set_caption('Танкокалипсис')
    running = True
    pygame.mouse.set_visible(False)

    # вызов спрайтов
    tank = Tank(tank_sprites, 300, 300)
    turret = Turret(turret_sprites, tank=tank)
    arrow = Arrow()

    # for i in range(40):
    #     zombie = Zombie(zombie_sprites, randint(300, 700), randint(
    #         500, 600), speed=random.choice([1, 1.3]))

    # игровой цикл
    while running:

        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_focused():
                arrow.update(mouse_x, mouse_y)
            else:
                arrow.rect.x = -100
                arrow.rect.y = -100

        tank_sprites.update(keys, mouse_x, mouse_y, block_sprites,
                            turret, zombie_sprites, water_sprites)
        # отрисовка карты
        map_sprite.draw(surf_alpha)

        # отрисовка игровых объектов
        screen.blit(surf_alpha, (0, 0))
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
        arrow_sprites.draw(screen)
        if tank.hp <= 0:
            intro_text = ["Танкокалипсис", "",
                          "О нет",
                          "ты проиграл!"]
            fon_screen(intro_text)
            running = False
        pygame.display.flip()
        clock.tick(fps)
