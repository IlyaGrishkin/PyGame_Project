import os
import sys
from common import load_image
from sprites.map import Block, Ground, Water


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


def generate_map(array, map_sprites):
    """
    Возвращает группу спрайтов (карта), которую можно
    (и нужно) отрисовать на экране
    """
    blocks = []
    waters = []
    x, y = 0, 0
    for k in range(len(array)):
        x = 0
        for m in range(len(array[0])):
            if array[k][m] == 'W':
                water = Water(map_sprites, x, y)
                waters.append(water)
            elif array[k][m] == 'G':
                Ground(map_sprites, x, y)
            elif array[k][m] == 'b':
                block = Block(map_sprites, x, y)
                blocks.append(block)
            x += 40
        y += 40
    return map_sprites, blocks, waters
