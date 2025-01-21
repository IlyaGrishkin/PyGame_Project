import pygame

from common import load_image


class Water(pygame.sprite.Sprite):
    image = load_image('water.png')

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Water.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Block(pygame.sprite.Sprite):
    image = load_image('block.jpg')

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Block.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    # def update(self):
    #     if pygame.sprite.collide_mask(self, arrow):
    #         print('Block')


class Ground(pygame.sprite.Sprite):
    image = load_image('ground.jpg')

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Ground.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Bush(pygame.sprite.Sprite):
    image = load_image('bush.png')

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Bush.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
