import math
import time
import pygame

from common import load_image


class Tank(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.og_surf = pygame.transform.smoothscale(load_image(
            "tank.png", colorkey=(0, 255, 0)).convert(), (60, 111))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect()
        self.tank_angle = 0
        self.change_angle = 0
        self.acceleration = 0.08
        self.max_speed = 3
        self.current_speed = 0
        self.bullet_speed = 10
        self.reload_time = 3
        self.last_shot_time = 0

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
                self.current_speed - self.acceleration, -self.max_speed)
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

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=self.rect.center)

    def control_rotation(self, keys):
        if self.current_speed < 0:  # если движение назад, то инвертированный поворот
            if keys[pygame.K_w]:
                if (keys[pygame.K_a] and keys[pygame.K_w]):
                    self.tank_angle -= self.tank_rotation_speed_actual * 0.3
                if (keys[pygame.K_d] and keys[pygame.K_w]):
                    self.tank_angle += self.tank_rotation_speed_actual * 0.3
            else:
                if keys[pygame.K_a]:
                    self.tank_angle += self.tank_rotation_speed_actual  # повернуть влево
                if keys[pygame.K_d]:
                    self.tank_angle -= self.tank_rotation_speed_actual  # повернуть вправо
        else:  # если движение вперед, то обычный поворот
            if keys[pygame.K_s]:
                if (keys[pygame.K_a] and keys[pygame.K_s]):
                    self.tank_angle += self.tank_rotation_speed_actual * 0.3
                if (keys[pygame.K_d] and keys[pygame.K_s]):
                    self.tank_angle -= self.tank_rotation_speed_actual * 0.3
            else:
                if keys[pygame.K_a]:
                    self.tank_angle -= self.tank_rotation_speed_actual  # повернуть влево
                if keys[pygame.K_d]:
                    self.tank_angle += self.tank_rotation_speed_actual  # повернуть вправо
        rotate_degrees = -math.degrees(self.tank_angle)
        self.surf = pygame.transform.rotate(self.og_surf, rotate_degrees)
        self.rect = self.surf.get_rect(center=self.rect.center)

    def move_tank(self):
        new_x = self.rect.x + self.current_speed * math.sin(self.tank_angle)
        new_y = self.rect.y - self.current_speed * math.cos(self.tank_angle)
        if 0 <= new_x <= 1080 - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= 720 - self.rect.height:
            self.rect.y = new_y

    def rotate_turret(self, mouse_x, mouse_y, turret: "Turret"):
        desired_angle = math.atan2(
            turret.rect.y - mouse_y, mouse_x - turret.rect.x) % (2 * math.pi)
        angle_difference = (desired_angle - turret.angle) % (2 * math.pi)
        if angle_difference > math.pi:
            angle_difference -= 2 * math.pi

        turret.angle += (angle_difference *
                         self.turret_rotation_speed) % (2 * math.pi)
        turret.angle %= 2 * math.pi
        print(desired_angle, turret.angle)
        rotate_degrees = math.degrees(turret.angle) - 90
        turret.surf = pygame.transform.rotate(turret.og_surf, rotate_degrees)
        turret.rect.x = self.rect.center[0]
        turret.rect.y = self.rect.center[1]
        turret.rect = turret.surf.get_rect(
            center=(turret.rect.x, turret.rect.y))

    # def shoot_bullet(self, turret: "Turret"):
    #     current_time = time.time()
    #     if pygame.mouse.get_pressed()[0] and current_time - self.last_shot_time > self.reload_time:
    #         bullet_dx = bullet_speed * math.cos(turret.angle)
    #         bullet_dy = -bullet_speed * math.sin(turret.angle)
    #         turret_x = tank_x + turret_offset * math.sin(self.tank_angle)
    #         turret_y = tank_y - turret_offset * math.cos(self.tank_angle)
    #         end_x = turret_x + barrel_length * math.cos(turret.angle)
    #         end_y = turret_y - barrel_length * math.sin(turret.angle)
    #         bullets.append([end_x, end_y, bullet_dx, bullet_dy])
    #         last_shot_time = current_time

    def update(self, keys, mouse_x, mouse_y, turret: "Turret"):
        # логика скорости
        self.control_speed(keys)

        # управление скоростью вращения танка на месте
        self.control_rotation_speed(keys)

        # управление поворотом танка
        self.control_rotation(keys)

        # перемещение танка
        self.move_tank()

        # turret.update()

        # управление поворотом башни
        self.rotate_turret(mouse_x, mouse_y, turret=turret)

        # проверка на въезд в воду
        ...

        # логика стрельбы
        ...


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

    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle
        self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=tank.rect.center)

    def update(self):
        self.rect.x = self.tank.rect.x
        self.rect.y = self.tank.rect.y


class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet.png")
    boom_image = load_image("boom.png")

    def __init__(self, group, x, y, dx, dy):
        super().__init__(group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.dx = dx
        self.dy = dy
        self.time = 0  # счетчик времени до взрыва

    def update(self, block_sprites, clock):
        if not pygame.sprite.spritecollideany(self, block_sprites):
            self.rect.x += self.dx
            self.rect.y += self.dy
        else:
            self.image = self.boom_image
            self.time += clock.get_time() / 10
        if self.time >= 30:  # если время вышло объект удаляется
            self.kill()
