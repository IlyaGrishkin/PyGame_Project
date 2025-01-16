import os
import sys

import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


all_sprites = pygame.sprite.Group()


class Water(pygame.sprite.Sprite):
    image = load_image('water.png')

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Water.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Block(pygame.sprite.Sprite):
    image = load_image('block.jpg')

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Block.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Ground(pygame.sprite.Sprite):
    image = load_image('ground.png')

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Ground.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Bush(pygame.sprite.Sprite):
    image = load_image('bush.png')

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Bush.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


def read_map(filename):
    fullname = os.path.join('levels', filename)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    array = []
    with open(f'levels/{filename}') as file:
        for line in file:
            array.append(list(line.strip()))
    return array


def generate_map(array):
    """
    Возвращает группу спрайтов (карта), которую можно
    (и нужно) отрисовать на экране
    """
    x, y = 0, 0
    for k in range(len(array)):
        x = 0
        for m in range(len(array[0])):
            if array[k][m] == 'W':
                Water(x, y)
            elif array[k][m] == 'G':
                Ground(x, y)
            elif array[k][m] == 'B':
                Bush(x, y)
            elif array[k][m] == 'b':
                Block(x, y)
            x += 40
        y += 40
    return all_sprites


