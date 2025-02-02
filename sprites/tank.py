import math
import sys
import time
import pygame

from common import load_image


def terminate():
    pygame.quit()
    sys.exit()


class Tank(pygame.sprite.Sprite):
    image = load_image("tank.png")

    def __init__(self, group, x, y, move_sound, health_upgrade, speed_upgrade, reload_upgrade):
        super().__init__(group)
        self.og_surf = pygame.transform.smoothscale(load_image(
            "tank.png", colorkey=(0, 255, 0)).convert(), (60, 111))
        self.shoot_sound = pygame.mixer.Sound('data/shoot.wav')
        self.shoot_sound.set_volume(0.1)
        self.move_sound = move_sound
        self.move_sound.set_volume(0.02)
        self.zombie_kill_sound = pygame.mixer.Sound('data/zombie_kill.wav')
        self.zombie_kill_sound.set_volume(0.1)
        self.move_chanel = pygame.mixer.find_channel(True)
        self.move_chanel.play(move_sound)
        self.moved = False
        self.rotated = False
        self.surf = self.og_surf
        self.rect = self.surf.get_rect()
        self.tank_angle = 0
        self.change_angle = 0
        self.acceleration = 0.08 + (0.08 * speed_upgrade)
        self.max_speed = 3 + (3 * speed_upgrade)
        self.current_speed = 0
        self.bullet_speed = 100
        self.reload_time = 3 - (1 * reload_upgrade)
        self.last_shot_time = 0
        self.bullet_speed = 10
        self.bullets = []
        self.bullet_info = None  # None - не было выстрела; иначе данные о выстреле
        self.mask = pygame.mask.from_surface(Tank.image)
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        self.hp = 3 + health_upgrade
        # длина ствола
        self.barrel_length = 1

        # скорость вращения башни
        self.turret_rotation_speed = 0.03

        # скорость вращения при езде
        self.tank_rotation_speed = 0.03

        # скорость вращения на месте
        self.tank_rotation_speed_stationary = 0.06

        # self.turret_offset = 100 // 2 - 30

        # движется ли танк вперед
        self.moving_forward = False

        # прошлое направление движения (1 = прямо, -1 = назад)
        self.last_direction = 0

        self.rect.x = x
        self.rect.y = y
        self.change_angle = 0

    def control_speed(self, keys):
        if keys[pygame.K_w]:
            self.current_speed = min(
                self.current_speed + self.acceleration, self.max_speed)
            self.moving_forward = True

            self.last_direction = 1
        elif keys[pygame.K_s]:
            self.current_speed = max(
                self.current_speed - self.acceleration, -(self.max_speed / 1.7))
            self.moving_forward = False
            self.last_direction = -1
        else:
            if self.current_speed > 0:
                self.current_speed = max(
                    self.current_speed - self.acceleration, 0)
            elif self.current_speed < 0:
                self.current_speed = min(
                    self.current_speed + self.acceleration, 0)

    def control_rotation_speed(self, keys):
        if self.current_speed == 0:
            self.tank_rotation_speed_actual = self.tank_rotation_speed_stationary
        else:
            self.tank_rotation_speed_actual = self.tank_rotation_speed

    def control_rotation(self, keys, block_sprites, water_sprites):
        tank_angle_change_old = 0
        tank_angle_change = 0
        if self.current_speed < 0:  # если движение назад, то инвертированный поворот
            if keys[pygame.K_w]:
                if (keys[pygame.K_a] and keys[pygame.K_w]):
                    tank_angle_change = -self.tank_rotation_speed_actual * 0.3
                if (keys[pygame.K_d] and keys[pygame.K_w]):
                    tank_angle_change = self.tank_rotation_speed_actual * 0.3
            else:
                if keys[pygame.K_a]:
                    tank_angle_change = self.tank_rotation_speed_actual  # повернуть влево
                if keys[pygame.K_d]:
                    tank_angle_change = -self.tank_rotation_speed_actual  # повернуть вправо
        else:  # если движение вперед, то обычный поворот
            if keys[pygame.K_s]:
                if (keys[pygame.K_a] and keys[pygame.K_s]):
                    tank_angle_change = self.tank_rotation_speed_actual * 0.3
                if (keys[pygame.K_d] and keys[pygame.K_s]):
                    tank_angle_change = -self.tank_rotation_speed_actual * 0.3
            else:
                if keys[pygame.K_a]:
                    tank_angle_change = -self.tank_rotation_speed_actual  # повернуть влево
                if keys[pygame.K_d]:
                    tank_angle_change = self.tank_rotation_speed_actual  # повернуть вправо
        test_surf = self.og_surf
        test_tank_angle = self.tank_angle
        test_tank_angle += tank_angle_change
        rotate_degrees = -math.degrees(test_tank_angle)
        test_surf = pygame.transform.rotate(test_surf, rotate_degrees)
        if not self.block_collide(block_sprites, surface=test_surf):
            self.tank_angle += tank_angle_change
            rotate_degrees = -math.degrees(self.tank_angle)
            self.surf = pygame.transform.rotate(self.og_surf, rotate_degrees)
            self.rect = self.surf.get_rect(center=self.rect.center)
        if tank_angle_change_old != tank_angle_change:
            self.rotated = True
        else:
            self.rotated = False

    def move_tank(self):
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        new_x = self.rect.x + self.current_speed * math.sin(self.tank_angle)
        new_y = self.rect.y - self.current_speed * math.cos(self.tank_angle)

        if new_x <= -40:
            self.rect.x = 1120
        if new_x >= 1120:
            self.rect.x = -40
        if new_y <= -40:
            self.rect.y = 760
        if new_y >= 760:
            self.rect.y = -40

        if -40 < new_x < 1120:
            self.rect.x = new_x
        if -40 < new_y < 760:
            self.rect.y = new_y

        if self.old_x == new_x and self.old_y == new_y:
            self.moved = False
        else:
            self.moved = True

    def rotate_turret(self, mouse_x, mouse_y, turret: "Turret"):
        desired_angle = math.atan2(
            turret.rect.y - mouse_y, mouse_x - turret.rect.x) % (2 * math.pi)
        angle_difference = (desired_angle - turret.angle) % (2 * math.pi)
        if angle_difference > math.pi:
            angle_difference -= 2 * math.pi

        turret.angle += (angle_difference *
                         self.turret_rotation_speed) % (2 * math.pi)
        turret.angle %= 2 * math.pi
        rotate_degrees = math.degrees(turret.angle) - 90
        turret.surf = pygame.transform.rotate(turret.og_surf, rotate_degrees)
        turret.rect.x = self.rect.center[0] + 10 * math.sin(self.tank_angle)
        turret.rect.y = self.rect.center[1] - 10 * math.cos(self.tank_angle)
        turret.rect = turret.surf.get_rect(
            center=(turret.rect.x, turret.rect.y))

    def shoot_bullet(self, keys, turret: "Turret"):
        current_time = time.time()
        if pygame.mouse.get_pressed()[0] and current_time - self.last_shot_time > self.reload_time:
            bullet_dx = self.bullet_speed * math.cos(turret.angle)
            bullet_dy = -self.bullet_speed * math.sin(turret.angle)
            end_x = (turret.rect.x + 5) + \
                self.barrel_length * math.cos(turret.angle)
            end_y = (turret.rect.y + 5) - \
                self.barrel_length * math.sin(turret.angle)
            self.last_shot_time = current_time
            self.shoot_sound.play()
            return [end_x, end_y, bullet_dx, bullet_dy, turret.angle]

    def block_collide(self, block_sprites, surface=None):
        if surface is None:
            surface = self.surf
        self.mask = pygame.mask.from_surface(surface)
        for elem in block_sprites:
            if pygame.sprite.collide_mask(self, elem):
                self.rect.x = self.old_x
                self.rect.y = self.old_y
                return True

    def water_collide(self, water_sprites, speed_upgrade, surface=None):
        if surface is None:
            surface = self.surf
        self.mask = pygame.mask.from_surface(surface)
        if any(pygame.sprite.collide_mask(self, elem) for elem in water_sprites):
            # self.rect.x = self.old_x
            # self.rect.y = self.old_y
            # return True
            self.acceleration = 0.02 + (0.02 * speed_upgrade)
            self.tank_rotation_speed_stationary = 0.03
            self.max_speed = 1.5 + (1.5 * speed_upgrade)
        else:
            self.acceleration = 0.08 + (0.08 * speed_upgrade)
            self.tank_rotation_speed_stationary = 0.06
            self.max_speed = 3 + (3 * speed_upgrade)

    def zombie_collide(self, zombie_sprites):
        self.mask = pygame.mask.from_surface(self.surf)
        for elem in zombie_sprites:
            if pygame.sprite.collide_mask(self, elem):
                if not elem.killed:
                    self.hp -= 1
                    elem.killed = True
                    self.zombie_kill_sound.play()
                    elem.surf = pygame.transform.smoothscale(
                        elem.blood_image.convert(), (40, 48))
                    elem.zombies_list.remove(elem)
                    elem.start = pygame.time.get_ticks()

    def zombie_boss_collide(self, zombie_boss_sprites):
        self.mask = pygame.mask.from_surface(self.surf)
        for elem in zombie_boss_sprites:
            if pygame.sprite.collide_mask(self, elem):
                if not elem.killed:
                    self.hp = 0

    def draw_hp(self, screen):
        font = pygame.font.Font('./data/TeletactileRus.ttf', 50)
        text = font.render('Здоровье: ' + str(self.hp), True, (255, 0, 0))
        text_x = 20
        text_y = 20
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (255, 0, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)

    def show_cooldown(self, screen):
        current_time = time.time()
        if current_time - self.last_shot_time < self.reload_time:
            cooldown_text = f"{self.reload_time -
                               (current_time - self.last_shot_time):.2f}с"
            font = pygame.font.Font('./data/TeletactileRus.ttf', 30)
            text = font.render(cooldown_text, True, (255, 255, 255))
            screen.blit(text, (self.rect.x, self.rect.y - 30))

    def update(self, keys, mouse_x, mouse_y, block_sprites, turret: "Turret", zombie_sprites, water_sprites, speed_upgrade,
               zombie_boss_sprites=None):
        # логика скорости
        self.control_speed(keys)

        # управление скоростью вращения танка на месте
        self.control_rotation_speed(keys)

        # управление поворотом танка
        self.control_rotation(keys, block_sprites, water_sprites)

        # проверка столкновений с блоками

        self.block_collide(block_sprites)

        # проверка столкновений с водой

        self.water_collide(water_sprites, speed_upgrade)

        # проверка столкновений с зомби

        self.zombie_collide(zombie_sprites)

        if zombie_boss_sprites:
            self.zombie_boss_collide(zombie_boss_sprites)

        # перемещение танка
        self.move_tank()

        if self.moved or self.rotated:
            self.move_chanel.unpause()
        else:
            self.move_chanel.pause()

        # turret.update()

        # управление поворотом башни
        self.rotate_turret(mouse_x, mouse_y, turret=turret)

        # проверка на въезд в воду
        ...

        # логика стрельбы
        self.bullet_info = self.shoot_bullet(keys, turret=turret)


class Turret(pygame.sprite.Sprite):
    def __init__(self, group, tank: Tank):
        super().__init__(group)
        self.og_surf = pygame.transform.smoothscale(
            load_image("turret.png", (0, 0, 0)).convert(), (40, 74))
        self.surf = self.og_surf
        self.tank = tank
        self.rect = self.surf.get_rect(center=tank.rect.center)
        self.rect.x = 0
        self.rect.y = 0
        self.angle = 0
        self.change_angle = 0

    def update(self, tank: Tank):
        self.rect.x = self.tank.rect.x + math.sin(tank.tank_angle)
        self.rect.y = self.tank.rect.y - math.cos(tank.tank_angle)


class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet.png")
    boom_image = load_image("boom.png")

    def __init__(self, group, x, y, dx, dy, turret_angle):
        super().__init__(group)
        self.og_surf = pygame.transform.smoothscale(self.image, (25, 25))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)

        # взрывные картинки
        self.boom_images = []
        for num in range(1, 6):
            img = pygame.image.load(f"data/explosion/exp{num}.png")
            img = pygame.transform.scale(img, (50, 50))
            self.boom_images.append(img)
        self.boom_index = 0
        self.boom_image = self.boom_images[self.boom_index]
        self.boom_rect = self.image.get_rect()
        self.boom_rect.center = [x, y]
        self.boom_counter = 0
        self.explosion_speed = 4

        self.rect.x = x
        self.rect.y = y
        self.dx = dx
        self.dy = dy
        self.angle = turret_angle
        self.time = 0  # счетчик времени до взрыва
        self.rotate()

    def rotate(self):
        rotate_degrees = math.degrees(self.angle)
        self.surf = pygame.transform.rotate(self.og_surf, rotate_degrees)
        self.rect = self.surf.get_rect(center=self.rect.center)

    def update(self, block_sprites, clock):
        if not pygame.sprite.spritecollideany(self, block_sprites):
            self.rect.x += self.dx
            self.rect.y += self.dy
        else:
            self.boom_counter += 1
            if self.boom_counter >= self.explosion_speed and self.boom_index < len(self.boom_images) - 1:
                self.boom_counter = 0
                self.boom_index += 1
                self.surf = self.boom_images[self.boom_index]
        if self.boom_index >= len(
                self.boom_images) - 1 and self.boom_counter >= self.explosion_speed:  # если время вышло объект удаляется
            self.kill()
