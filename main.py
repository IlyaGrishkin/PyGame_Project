import pygame, os, sys

pygame.init()
size = width, height = 1080, 720
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


map_sprites = pygame.sprite.Group()
block_sprites = pygame.sprite.Group()
tank_sprites = pygame.sprite.Group()


class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tank_sprites)
        self.og_surf = pygame.transform.smoothscale(load_image("tank.png", colorkey=(0, 255, 0)).convert(), (60, 111))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect()
        self.angle = 0
        self.rect.x = x
        self.rect.y = y
        self.change_angle = 0

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=self.rect.center)

    def update(self, *args):
        self.change_angle = 0
        if keys[pygame.K_LEFT]:
            self.change_angle = 10
        elif keys[pygame.K_RIGHT]:
            self.change_angle = -10
        self.rot()


class Turret(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(tank_sprites)
        self.og_surf = pygame.transform.smoothscale(load_image("turret.png", (0, 0, 0)).convert(), (40, 74))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect(center=tank.rect.center)
        self.angle = 0
        self.change_angle = 0

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=tank.rect.center)

    def update(self, *args):
        self.change_angle = 0
        if keys[pygame.K_LEFT]:
            self.change_angle = 10
        elif keys[pygame.K_RIGHT]:
            self.change_angle = -10
        self.rot()


class Water(pygame.sprite.Sprite):
    image = load_image('water.png')

    def __init__(self, x, y):
        super().__init__(map_sprites)
        self.image = Water.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Block(pygame.sprite.Sprite):
    image = load_image('block.jpg')

    def __init__(self, x, y):
        super().__init__(block_sprites)
        self.image = Block.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    # def update(self):
    #     if pygame.sprite.collide_mask(self, arrow):
    #         print('Block')


class Ground(pygame.sprite.Sprite):
    image = load_image('ground.png')

    def __init__(self, x, y):
        super().__init__(map_sprites)
        self.image = Ground.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Bush(pygame.sprite.Sprite):
    image = load_image('bush.png')

    def __init__(self, x, y):
        super().__init__(map_sprites)
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
    blocks = []
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
                block = Block(x, y)
                blocks.append(block)
            x += 40
        y += 40
    return map_sprites, blocks


all_sprites = pygame.sprite.Group()


class Arrow(pygame.sprite.Sprite):
    image = load_image("crosshair.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = -100
        self.rect.y = -100

    def update(self, *args):
        self.rect.x = x
        self.rect.y = y


class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet.png")
    boom_image = load_image("boom.png")

    def __init__(self, x, y):
        super().__init__(bullet_sprite)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.time = 0  # счетчик времени до взрыва

    def update(self, dx, dy):
        if not pygame.sprite.spritecollideany(self, block_sprites):
            self.rect.x += dx
            self.rect.y += dy
        else:
            self.image = self.boom_image
            self.time += clock.get_time() / 10
        if self.time >= 30:  # если время вышло объект удаляется
            self.kill()


bullet_sprite = pygame.sprite.Group()

if __name__ == '__main__':

    surf_alpha = pygame.Surface((width, height))

    map_sprite, blocks = generate_map(read_map('level1.txt'))

    pygame.display.set_caption('Танкокалипсис')
    fps = 100
    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)
    arrow = Arrow(all_sprites)
    tank = Tank(300, 300)
    turret = Turret()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            keys = pygame.key.get_pressed()
            if keys:
                tank_sprites.update(keys)
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                arrow.update(event)
            else:
                arrow.rect.x = -100
                arrow.rect.y = -100

        map_sprite.draw(surf_alpha)
        block_sprites.draw(surf_alpha)
        screen.blit(surf_alpha, (0, 0))
        screen.blit(tank.surf, tank.rect)
        screen.blit(turret.surf, turret.rect)
        all_sprites.draw(screen)
        map_sprite.update()
        block_sprites.update()
        bullet_sprite.draw(screen)
        bullet_sprite.update(5, 0)
        pygame.display.flip()
        clock.tick(fps)
