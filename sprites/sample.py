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
