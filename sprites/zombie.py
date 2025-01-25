import pygame

from common import load_image


class Zombie(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
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
    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=self.rect.center)

    def update(self, bullet_sprites, clock):
        if pygame.sprite.spritecollideany(self, bullet_sprites):
            self.surf = pygame.transform.smoothscale(
                load_image("blood.png", (0, 0, 0)).convert(), (40, 48))
            self.killed = True
        if self.killed:
            self.time -= clock.get_time() / 100
        if self.time <= 0:
            self.kill()