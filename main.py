from random import randint

import pygame
import os
import sys
import random

from map_logic import generate_map, read_map
from sprites.tank import Tank, Turret  # , Turret
from sprites.zombie import Zombie

arrow_sprites = pygame.sprite.Group()
map_sprites = pygame.sprite.Group()
block_sprites = pygame.sprite.Group()
tank_sprites = pygame.sprite.Group()
turret_sprites = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()
zombie_sprites = pygame.sprite.Group()


# инициализация Pygame
pygame.init()
size = width, height = 1080, 720
screen = pygame.display.set_mode(size)
if True:
    from common import load_image


# прицел
class Arrow(pygame.sprite.Sprite):
    image = load_image("crosshair.png")

    def __init__(self):
        super().__init__(arrow_sprites)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = -100
        self.rect.y = -100

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y


if __name__ == '__main__':

    surf_alpha = pygame.Surface((width, height))

    # генерация карты и блоков
    map_sprite, blocks = generate_map(
        array=read_map('level1.txt'),
        map_sprites=map_sprites,
    )

    # базовые настройки
    pygame.display.set_caption('Танкокалипсис')
    fps = 100
    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)

    # вызов спрайтов
    tank = Tank(tank_sprites, 300, 300)
    turret = Turret(turret_sprites, tank=tank)
    arrow = Arrow()

    for i in range(10):
        zombie = Zombie(zombie_sprites, randint(10, 700), randint(10, 600))

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

        tank_sprites.update(keys, mouse_x, mouse_y, turret)
        # turret.update()
        # отрисовка карты
        map_sprite.draw(surf_alpha)
        # block_sprites.draw(surf_alpha)

        # отрисовка игровых объектов
        screen.blit(surf_alpha, (0, 0))
        screen.blit(tank.surf, tank.rect)
        screen.blit(turret.surf, turret.rect)
        arrow_sprites.draw(screen)
        # screen.blit(arrow.image, arrow.rect)
        for zombie in zombie_sprites:
            screen.blit(zombie.surf, zombie.rect)

        map_sprite.update()
        # block_sprites.update()

        # тестовая пулька
        bullet_sprite.draw(screen)
        bullet_sprite.update(5, 0)

        pygame.display.flip()
        clock.tick(fps)
