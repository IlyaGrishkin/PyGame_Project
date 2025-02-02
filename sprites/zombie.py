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
        self.zombie_kill_sound = pygame.mixer.Sound('data/zombie_kill.wav')
        self.zombie_kill_sound.set_volume(0.005)
        self.zombie_nearby_sound = pygame.mixer.Sound('data/zombie_nearby.wav')
        self.zombie_nearby_sound.set_volume(0.01)
        self.sound_played = False
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
        self.next_point = (random.randint(200, 700), random.randint(150, 400))
        self.collide_behavior = random.choice([-1, 1])

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
                self.rect.x += self.collide_behavior
                return True
        return False

    def level0_zombi(self, tank, block_sprites):
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

    def tank_nearby(self, tank, distance):
        return abs(tank.rect.x - self.rect.x) <= distance and abs(tank.rect.y - self.rect.y) <= distance

    def zombie_move(self, goalX, goalY, block_sprites):
        test_rect = self.rect.copy()
        self.rotate_zombie_sprite(goalX, goalY)
        if goalX >= self.rect.x and goalY >= self.rect.y:
            test_rect.x += self.speed
            test_rect.y += self.speed  # Минимальное движение вправо
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x += self.speed  # Минимальное движение вправо
                self.rect.y += self.speed
            else:
                self.next_point = (random.randint(0, 1080),
                                   random.randint(0, 720))

        elif goalX >= self.rect.x and goalY <= self.rect.y:
            test_rect.x += self.speed
            test_rect.y -= self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x += self.speed  # Минимальное движение влево
                self.rect.y -= self.speed
            else:
                self.next_point = (random.randint(0, 1080),
                                   random.randint(0, 720))

        elif goalX <= self.rect.x and goalY >= self.rect.y:
            test_rect.x -= self.speed
            test_rect.y += self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x -= self.speed  # Минимальное движение влево
                self.rect.y += self.speed
            else:
                self.next_point = (random.randint(0, 1080),
                                   random.randint(0, 720))

        else:
            test_rect.x -= self.speed
            test_rect.y -= self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x -= self.speed  # Минимальное движение влево
                self.rect.y -= self.speed
            else:
                self.next_point = (random.randint(0, 1080),
                                   random.randint(0, 720))

    def level1_zombi(self, tank, block_sprites):

        if self.tank_nearby(tank, distance=400):
            if not self.sound_played:
                self.zombie_nearby_sound.play()
                self.sound_played = True
            self.zombie_move(tank.rect.x, tank.rect.y, block_sprites)

        else:
            if abs(self.next_point[0] - self.rect.x) <= 5 and abs(self.next_point[1] - self.rect.y) <= 5:
                self.next_point = (random.randint(0, 1080),
                                   random.randint(0, 720))
                self.rotate_zombie_sprite(*self.next_point)

            self.zombie_move(
                self.next_point[0], self.next_point[1], block_sprites)
            self.sound_played = False

    def rotate_zombie_sprite(self, pointX, pointY):
        rad = math.atan2(pointY - self.rect.y,
                         pointX - self.rect.x)
        self.angle = 270 - math.degrees(rad)
        self.rot()

    def update(self, bullet_sprites, tank, block_sprites, water_sprites):
        if pygame.sprite.spritecollideany(self, bullet_sprites) and not self.killed:
            self.killed = True
            self.zombie_kill_sound.play()
            self.start = pygame.time.get_ticks()
            self.surf = pygame.transform.smoothscale(
                self.blood_image.convert(), (40, 48))
            self.zombies_list.remove(self)
        if self.killed:
            self.zombie_kill(self.start)
        else:
            self.level1_zombi(tank, block_sprites)


class ZombieBoss(pygame.sprite.Sprite):
    def __init__(self, group, x, y, speed):
        super().__init__(group)
        self.image = load_image("zombie_boss.png")
        self.blood_image = load_image("destroyed_boss.png")
        self.og_surf = pygame.transform.smoothscale(
            load_image("zombie_boss.png", (0, 0, 0)).convert(), (250, 250))
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
        self.next_point = (300, 300)
        self.hp = 10
        self.gen_zombie_count = 0

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.rect = self.surf.get_rect(center=self.rect.center)

    def rotate_zombie_sprite(self, pointX, pointY):
        rad = math.atan2(pointY - self.rect.y,
                         pointX - self.rect.x)
        self.angle = 270 - math.degrees(rad)
        self.rot()
        self.mask = pygame.mask.from_surface(self.surf)

    def zombie_kill(self, start):
        self.time = (pygame.time.get_ticks() - start) / 1000
        if self.time > 3:
            self.kill()

    def block_collide(self, block_sprites, rect):
        for block in block_sprites:
            if rect.colliderect(block.rect):
                return True
        return False

    def tank_nearby(self, tank, distance):
        return abs(tank.rect.x - self.rect.x) <= distance and abs(tank.rect.y - self.rect.y) <= distance

    def zombie_move(self, goalX, goalY, block_sprites):
        test_rect = self.rect.copy()
        self.rotate_zombie_sprite(goalX, goalY)

        if goalX >= self.rect.x and goalY >= self.rect.y:
            test_rect.x += self.speed
            test_rect.y += self.speed  # Минимальное движение вправо
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x += self.speed  # Минимальное движение вправо
                self.rect.y += self.speed
            else:
                self.next_point = self.gen_next_point(*self.next_point)

        elif goalX >= self.rect.x and goalY <= self.rect.y:
            test_rect.x += self.speed
            test_rect.y -= self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x += self.speed  # Минимальное движение влево
                self.rect.y -= self.speed
            else:
                self.next_point = self.gen_next_point(*self.next_point)

        elif goalX <= self.rect.x and goalY >= self.rect.y:
            test_rect.x -= self.speed
            test_rect.y += self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x -= self.speed  # Минимальное движение влево
                self.rect.y += self.speed
            else:
                self.next_point = self.gen_next_point(*self.next_point)

        else:
            test_rect.x -= self.speed
            test_rect.y -= self.speed
            if not self.block_collide(block_sprites, test_rect):
                self.rect.x -= self.speed  # Минимальное движение влево
                self.rect.y -= self.speed
            else:
                self.next_point = self.gen_next_point(*self.next_point)

    def gen_next_point(self, curX, curY) -> tuple:
        angle_points = [(120, 60), (120, 450), (760, 60), (760, 450)]
        if 350 < curX < 550 and 200 < curY < 320:
            return random.choice(angle_points)
        points = [(random.randint(110, 350), random.randint(50, 330)),
                  (random.randint(110, 350), random.randint(330, 470)),
                  (random.randint(550, 780), random.randint(50, 330)),
                  (random.randint(550, 780), random.randint(330, 470))]
        if curX <= 350 and curY <= 200:
            points.pop(0)
        elif curX <= 400 and curY >= 320:
            points.pop(1)
        elif curX >= 400 and curY <= 200:
            points.pop(2)
        else:
            points.pop(3)
        return random.choice(points)

    def level1_zombi(self, tank, block_sprites):
        if self.tank_nearby(tank, 200):
            self.zombie_move(tank.rect.x, tank.rect.y, block_sprites)
            self.speed = 1.3

        else:

            if abs(self.next_point[0] - self.rect.x) <= 10 and abs(self.next_point[1] - self.rect.y) <= 10:
                self.next_point = self.gen_next_point(
                    # (random.randint(0, 1080), random.randint(0, 720))
                    *self.next_point)
                self.rotate_zombie_sprite(*self.next_point)
            self.zombie_move(
                self.next_point[0], self.next_point[1], block_sprites)
            self.speed = 1

    def handle_bullet_collide(self, bullet_sprites):
        if not self.killed:
            for b in bullet_sprites:
                if pygame.sprite.collide_mask(self, b):
                    b.kill()
                    self.hp -= 1
                    if self.hp <= 0:
                        self.killed = True
                        self.start = pygame.time.get_ticks()
                        self.surf = self.blood_image

    def gen_small_zombies(self, zombies_list, zombie_sprites):
        self.gen_zombie_count += 1
        if self.gen_zombie_count >= 420:
            for i in range(4):
                zombie = Zombie(zombie_sprites, zombies_list, self.rect.x - 3 + random.randint(-5, 5),
                                self.rect.y - 3 + random.randint(-5, 5), speed=random.choice([1.1, 1.3]))
                zombies_list.append(zombie)
            self.gen_zombie_count = 0

    def draw_hp(self, screen):
        font = pygame.font.Font('./data/TeletactileRus.ttf', 50)
        text = font.render('БОСС: ' + self.hp * '*', True, (255, 0, 0))
        text_x = 370
        text_y = 20
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (255, 0, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)

    def update(self, bullet_sprites, tank, block_sprites, water_sprites, zombies_list, zombie_sprites):
        self.handle_bullet_collide(bullet_sprites)
        if self.killed:
            self.zombie_kill(self.start)
        else:
            self.gen_small_zombies(zombies_list, zombie_sprites)
            self.level1_zombi(tank, block_sprites)
