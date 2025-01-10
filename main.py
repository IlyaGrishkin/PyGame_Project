import pygame, os, sys

pygame.init()
size = width, height = 1280, 720
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


all_sprites = pygame.sprite.Group()


class Arrow(pygame.sprite.Sprite):
    image = load_image("crosshair.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        self.rect.x = -100
        self.rect.y = -100

    def update(self, *args):
        self.rect.x = x
        self.rect.y = y


if __name__ == '__main__':
    pygame.display.set_caption('Танкокалипсис')
    fps = 100
    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)
    Arrow(all_sprites)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                all_sprites.update(event)
            else:
                for elem in all_sprites:
                    elem.rect.x = -100
                    elem.rect.y = -100
        screen.fill((140, 200, 130))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
