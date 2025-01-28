from pickletools import pyfloat
import random
import pygame

from common import load_image


class Zombie(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = load_image("zombie.png")
        self.blood_image = load_image("blood.png")
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
        self.mask = pygame.mask.from_surface(self.image)

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=self.rect.center)

    def zombie_kill(self, start):
        self.time = (pygame.time.get_ticks() - start) / 1000
        if self.time > 3:
            self.kill()

    def update(self, bullet_sprites, tank, block_sprites, water_sprites):
        if pygame.sprite.spritecollideany(self, bullet_sprites) and not self.killed:
            self.killed = True
            self.start = pygame.time.get_ticks()
            self.surf = pygame.transform.smoothscale(
                load_image("blood.png", (0, 0, 0)).convert(), (40, 48))
        if self.killed:
            self.zombie_kill(self.start)
        
        else:
            test_surf = self.og_surf
            if tank.rect.x > self.rect.x and tank.rect.y > self.rect.y:
                self.rect.x += 1 * random.random()
                self.rect.y += 1 * random.random()
            elif tank.rect.x < self.rect.x and tank.rect.y > self.rect.y:
                self.rect.x -= 1 * random.random()
                self.rect.y += 1 * random.random()
            elif tank.rect.x > self.rect.x and tank.rect.y < self.rect.y:
                self.rect.x += 1 * random.random()
                self.rect.y -= 1 * random.random()
            elif tank.rect.x < self.rect.x and tank.rect.y < self.rect.y:
                self.rect.x -= 1 * random.random()
                self.rect.y -= 1 * random.random()
            
        
