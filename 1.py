import pygame
import random
import time
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("World of Tanks")

GREEN = (128, 128, 128)
DARK_GREEN = (100, 100, 100)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BROWN = (150, 75, 0)
TRANSPARENT_GREEN = (34, 139, 34, 150)
MUD_COLOR = (139, 69, 19)  # Color for mud
SLOW_ZONE_COLOR = (139, 69, 19)  # Brownish color for slow zones (like mud)

# Tank parameters
tank_width = 20
tank_height = 60
acceleration = 0.08
max_speed = 2
current_speed = 0
bullet_speed = 10
bullet_length = 4  # Set the length of the bullet
barrel_length = 100
barrel_width = 6
turret_offset = tank_width // 2 - 30  # Small offset ahead of the tank's center
reload_time = 3
turret_rotation_speed = 0.03
tank_rotation_speed = 0.03  # Reduced rotation speed for tank turning
tank_rotation_speed_stationary = 0.06
max_angle = math.radians(75)

# Tank position and direction
tank_x = WIDTH // 2
tank_y = HEIGHT // 2
last_shot_time = 0
tank_angle = 0
turret_angle = 0  # Initialize turret_angle here
bullets = []
obstacles = []  # Will store obstacles with specific shapes and sizes
mud_zones = []  # Will store mud zones where speed is slowed
bushes = [(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
          for _ in range(10)]  # Increased number of bushes

clock = pygame.time.Clock()
running = True
invisible = False
inside_bush = False

# Function to draw tank
# aaaa


def draw_tank(x, y, tank_angle, turret_angle, invisible):
    if not invisible:
        # Create tank surface
        tank_surface = pygame.Surface((tank_width + 10, tank_height))
        tank_surface.set_colorkey((0, 0, 0))
        tank_surface.fill((0, 0, 0))

        # Draw tank body
        pygame.draw.rect(tank_surface, GREEN, (5, 0, tank_width, tank_height))

        # Draw tracks
        pygame.draw.rect(tank_surface, BROWN, (0, 0, 5, tank_height))
        pygame.draw.rect(tank_surface, BROWN,
                         (tank_width + 5, 0, 5, tank_height))

        # Rotate tank surface
        rotated_tank = pygame.transform.rotate(
            tank_surface, -math.degrees(tank_angle))
        screen.blit(rotated_tank, rotated_tank.get_rect(center=(x, y)))

        # Draw turret base - Position turret ahead of the tank's center
        turret_x = x + turret_offset * math.sin(tank_angle)
        turret_y = y - turret_offset * math.cos(tank_angle)

        pygame.draw.circle(screen, DARK_GREEN,
                           (int(turret_x), int(turret_y)), 10)

        # Draw turret barrel
        end_x = turret_x + barrel_length * math.cos(turret_angle)
        end_y = turret_y - barrel_length * math.sin(turret_angle)
        pygame.draw.line(screen, DARK_GREEN, (int(turret_x), int(
            turret_y)), (int(end_x), int(end_y)), barrel_width)

# Function to draw bullets


def draw_bullet(x, y, bullet_dx, bullet_dy):
    length = bullet_length
    angle = math.atan2(bullet_dy, bullet_dx)
    # Bullet is a rectangle, 5px wide
    bullet_rect = pygame.Surface((length, 5))
    bullet_rect.fill(RED)
    rotated_bullet = pygame.transform.rotate(bullet_rect, -math.degrees(angle))
    screen.blit(rotated_bullet, rotated_bullet.get_rect(center=(x, y)))

# Function to draw obstacles (variety of shapes)


def draw_obstacles():
    for obstacle in obstacles:
        color = obstacle["color"]
        shape = obstacle["shape"]
        x, y = obstacle["position"]
        if shape == "rect":
            width, height = obstacle["size"]
            pygame.draw.rect(screen, color, (x, y, width, height))
        elif shape == "circle":
            radius = obstacle["size"]
            pygame.draw.circle(screen, color, (x, y), radius)

# Function to draw mud zones (slow zones)


def draw_mud_zones():
    for zone in mud_zones:
        x, y, width, height = zone
        pygame.draw.rect(screen, SLOW_ZONE_COLOR, (x, y, width, height))

# Function to generate obstacles


def generate_obstacles(num_obstacles):
    for _ in range(num_obstacles):
        shape = random.choice(["rect", "circle"])
        # Black or gray obstacles
        color = random.choice([(0, 0, 0), (100, 100, 100), (120, 120, 120)])
        if shape == "rect":
            width = random.randint(40, 100)
            height = random.randint(40, 100)
            x = random.randint(0, WIDTH - width)
            y = random.randint(0, HEIGHT - height)
            obstacles.append({"shape": shape, "color": color,
                             "position": (x, y), "size": (width, height)})
        else:
            radius = random.randint(30, 50)
            x = random.randint(radius, WIDTH - radius)
            y = random.randint(radius, HEIGHT - radius)
            obstacles.append({"shape": shape, "color": color,
                             "position": (x, y), "size": radius})

# Function to generate mud zones


def generate_mud_zones(num_zones):
    for _ in range(num_zones):
        width = random.randint(100, 200)
        height = random.randint(50, 150)
        x = random.randint(0, WIDTH - width)
        y = random.randint(0, HEIGHT - height)
        mud_zones.append((x, y, width, height))


# Generate obstacles and mud zones
generate_obstacles(5)
generate_mud_zones(3)

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    moving_forward = False  # Track if moving forward or not
    last_direction = 0  # Track last direction (1 = forward, -1 = backward)
    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Tank movement logic (forward/backward)
    if keys[pygame.K_w]:
        current_speed = min(current_speed + acceleration, max_speed)
        moving_forward = True
        last_direction = 1
    elif keys[pygame.K_s]:
        current_speed = max(current_speed - acceleration, -max_speed)
        moving_forward = False
        last_direction = -1
    else:
        if current_speed > 0:
            current_speed = max(current_speed - acceleration, 0)
        elif current_speed < 0:
            current_speed = min(current_speed + acceleration, 0)

    # Handle tank rotation speed
    if current_speed == 0:
        tank_rotation_speed_actual = tank_rotation_speed_stationary
    else:
        tank_rotation_speed_actual = tank_rotation_speed

    # Turn tank left or right (rotation)
    if current_speed < 0:  # If moving backward, invert controls
        if keys[pygame.K_w]:
            if (keys[pygame.K_a] and keys[pygame.K_w]):
                tank_angle -= tank_rotation_speed_actual * 0.3
            if (keys[pygame.K_d] and keys[pygame.K_w]):
                tank_angle += tank_rotation_speed_actual * 0.3
        else:
            if keys[pygame.K_a]:
                tank_angle += tank_rotation_speed_actual  # Turn right
            if keys[pygame.K_d]:
                tank_angle -= tank_rotation_speed_actual  # Turn left
    else:  # If moving forward, normal controls
        if keys[pygame.K_s]:
            if (keys[pygame.K_a] and keys[pygame.K_s]):
                tank_angle += tank_rotation_speed_actual * 0.3
            if (keys[pygame.K_d] and keys[pygame.K_s]):
                tank_angle -= tank_rotation_speed_actual * 0.3
        else:
            if keys[pygame.K_a]:
                tank_angle -= tank_rotation_speed_actual  # Turn left
            if keys[pygame.K_d]:
                tank_angle += tank_rotation_speed_actual  # Turn right

    # Movement mechanics
    new_x = tank_x + current_speed * math.sin(tank_angle)
    new_y = tank_y - current_speed * math.cos(tank_angle)

    # Smooth turret rotation to follow mouse
    desired_angle = math.atan2(
        tank_y - mouse_y, mouse_x - tank_x) % (2 * math.pi)
    angle_difference = (desired_angle - turret_angle) % (2 * math.pi)
    if angle_difference > math.pi:
        angle_difference -= 2 * math.pi

    turret_angle += (angle_difference * turret_rotation_speed) % (2 * math.pi)
    turret_angle %= 2 * math.pi

    # Check for collision with obstacles
    can_move = True
    for obs in obstacles:
        if obs["shape"] == "rect":
            if pygame.Rect(obs["position"][0], obs["position"][1], obs["size"][0], obs["size"][1]).colliderect(pygame.Rect(new_x - tank_width // 2, new_y - tank_height // 2, tank_width, tank_height)):
                can_move = False
                break
        elif obs["shape"] == "circle":
            if math.sqrt((new_x - obs["position"][0])**2 + (new_y - obs["position"][1])**2) < obs["size"]:
                can_move = False
                break

    # Check for mud zone
    for zone in mud_zones:
        mud_rect = pygame.Rect(zone[0], zone[1], zone[2], zone[3])
        if mud_rect.colliderect(pygame.Rect(new_x - tank_width // 2, new_y - tank_height // 2, tank_width, tank_height)):
            current_speed *= 0.9  # Slow down in mud

    if can_move:
        tank_x, tank_y = new_x, new_y

    # Shooting logic
    current_time = time.time()
    if pygame.mouse.get_pressed()[0] and current_time - last_shot_time > reload_time:
        bullet_dx = bullet_speed * math.cos(turret_angle)
        bullet_dy = -bullet_speed * math.sin(turret_angle)
        turret_x = tank_x + turret_offset * math.sin(tank_angle)
        turret_y = tank_y - turret_offset * math.cos(tank_angle)
        end_x = turret_x + barrel_length * math.cos(turret_angle)
        end_y = turret_y - barrel_length * math.sin(turret_angle)
        bullets.append([end_x, end_y, bullet_dx, bullet_dy])
        last_shot_time = current_time

    # Draw bullets
    for bullet in bullets:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        draw_bullet(bullet[0], bullet[1], bullet[2], bullet[3])

    # Draw mud zones after all other objects
    draw_mud_zones()

    # Draw obstacles
    draw_obstacles()

    # Draw bushes and check if tank is inside
    inside_bush = False
    for bush in bushes:
        bush_rect = pygame.Surface((60, 60), pygame.SRCALPHA)
        bush_rect.fill(TRANSPARENT_GREEN)
        screen.blit(bush_rect, (bush[0], bush[1]))
        if pygame.Rect(bush[0], bush[1], 60, 60).colliderect(pygame.Rect(tank_x - tank_width // 2, tank_y - tank_height // 2, tank_width, tank_height)):
            inside_bush = True

    if inside_bush and not pygame.mouse.get_pressed()[0]:
        invisible = True
    else:
        invisible = False

    # Draw tank with rotating turret
    draw_tank(tank_x, tank_y, tank_angle, turret_angle, invisible)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
