import math
from pickletools import pyfloat
import random
import pygame

from common import load_image


class Zombie(pygame.sprite.Sprite):
    def __init__(self, group, zombies_list, x, y, speed):
        self.zombies_list = zombies_list
        super().__init__(group)
        self.image = load_image("zombie.png")
        self.blood_image = load_image("blood.png", colorkey=-1)
        self.og_surf = pygame.transform.smoothscale(
            load_image("zombie.png", (0, 0, 0)).convert(), (40, 48))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect()
        self.angle = 0
        self.rect.x = x
        self.rect.y = y
        self.change_angle = 0
        self.time = 150
        self.killed = False
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.rect = self.surf.get_rect(center=self.rect.center)

    def zombie_kill(self, start):
        self.time = (pygame.time.get_ticks() - start) / 1000
        if self.time > 3:
            self.kill()

    def block_collide(self, block_sprites, rect):
        for block in block_sprites:
            if rect.colliderect(block.rect):
                return True
        return False

    def level1_zombi(self, tank, block_sprites):
        test_rect = self.rect.copy()

        if tank.rect.x > self.rect.x:
            test_rect.x += 1  # Минимальное движение вправо
            if not self.block_collide(block_sprites, test_rect):

                self.rect.x += self.speed  # Минимальное движение вправо

        elif tank.rect.x < self.rect.x:
            test_rect.x -= 1  # Минимальное движение влево
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x -= self.speed  # Минимальное движение влево

        if tank.rect.y > self.rect.y:
            test_rect.y += 1  # Минимальное движение вниз
            if not self.block_collide(block_sprites, test_rect):
                self.rect.y += self.speed  # Минимальное движение вниз
        elif tank.rect.y < self.rect.y:
            test_rect.y -= 1  # Минимальное движение вверх
            if not self.block_collide(block_sprites, test_rect):
                self.rect.y -= self.speed  # Минимальное движение вверх

            # Случайное движение для разнообразия
        if random.random() < 0.5:
            if random.random() < 0.5:
                test_rect.x += 2 * random.random() - 1
                if not self.block_collide(block_sprites, test_rect):
                    self.rect.x += 2 * random.random() - 1
                else:
                    self.rect.x -= 6 * random.random() - 1
            else:
                test_rect.x -= 2 * random.random() - 1
                if not self.block_collide(block_sprites, test_rect):

                    self.rect.x -= 2 * random.random() - 1
                else:
                    self.rect.x += 6 * random.random() - 1
        else:
            if random.random() < 0.5:
                test_rect.y += 2 * random.random() - 1
                if not self.block_collide(block_sprites, test_rect):
                    self.rect.y += 2 * random.random() - 1
                else:
                    self.rect.y -= 6 * random.random() - 1
            else:
                test_rect.y -= 2 * random.random() - 1
                if not self.block_collide(block_sprites, test_rect):

                    self.rect.y -= 2 * random.random() - 1
                else:
                    self.rect.y += 6 * random.random() - 1

    def update(self, bullet_sprites, tank, block_sprites, water_sprites):
        if pygame.sprite.spritecollideany(self, bullet_sprites) and not self.killed:
            self.killed = True
            self.start = pygame.time.get_ticks()
            self.surf = pygame.transform.smoothscale(
                self.blood_image.convert(), (40, 48))
            self.zombies_list.remove(self)
        if self.killed:
            self.zombie_kill(self.start)
        else:
            self.level1_zombi(tank, block_sprites)
            rad = math.atan2(tank.rect.y - self.rect.y,
                             tank.rect.x - self.rect.x)
            self.angle = 270 - math.degrees(rad)
            self.rot()
