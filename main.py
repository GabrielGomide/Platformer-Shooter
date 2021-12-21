import pygame
import os

pygame.init()
width, height = 1200, 700
surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('Cold Adventures')

assets = os.path.join(os.getcwd(), 'Assets')
background = pygame.transform.scale(pygame.image.load(os.path.join(assets, 'background.jpg')), (width, height))
dirt = pygame.transform.scale(pygame.image.load(os.path.join(assets, 'dirt.png')), (50, 50))
snow = pygame.transform.scale(pygame.image.load(os.path.join(assets, 'dirt_with_snow.png')), (50, 50))
player_image = pygame.transform.scale(pygame.image.load(os.path.join(assets, 'player.png')), (47, 71))
enemy_image = pygame.transform.scale(pygame.image.load(os.path.join(assets, 'enemy.png')), (47, 71))

camera_x = 0
camera_walk = 8

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 180, 0)

tile_map = [
    '....................................................................',
    '....................................................................',
    '....................................................................',
    '....................................................................',
    '....................................................................',
    '....................................................................',
    '........................................XXXXXXX.....................',
    '.....................................XXXXXXXXXXXX...................',
    '...................................XXXXXXXXXXXXXXXX.................',
    '.........XXXXXXX..................XXXXXXXXXXXXXXXXXXXX..............',
    '................................XXXXXXXXXXXXXXXXXXXXXXXX............',
    'XXXXXXXX.........XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'XXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

def colliding(rect1, rect2):
    if not(rect1.x + rect1.width <= rect2.x or rect2.x + rect2.width <= rect1.x):
        if not(rect1.y + rect1.height <= rect2.y or rect2.y + rect2.height <= rect1.y):
            return True
    return False

def would_collide(rect1, current_map, camera=False):
    for y in range(len(current_map)):
        for x in range(camera_x if camera else 0, len(current_map[y])):
            if current_map[y][x] == 'X':
                x = (x - camera_x) if camera else x
                map_rect = pygame.Rect(x * 50, y * 50, 50, 50)
                if colliding(rect1, map_rect):
                    return True
    return False


class Bullet:
    def __init__(self, color, x, y, direction, fired_at, damage):
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
        self.fired_at = fired_at
        self.damage = damage

    def move(self):
        if self.direction == 'L':
            self.x -= 10
        else:
            self.x += 10

    def would_collide(self, x, current_map):
        rect = pygame.Rect(self.x + x, self.y, 10, 3)
        return would_collide(rect, current_map)

    def touched_enemy(self, enemies):
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            bullet_rect = pygame.Rect(self.x, self.y, 10, 3)
            if colliding(enemy_rect, bullet_rect):
                return enemy
        return False

class Character:
    def __init__(self, x, y, width, height, speed, image, looking, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.image = image
        self.looking = looking
        self.max_health = health
        self.health = health
        self.last_bullet = None
        self.bullets = []

    def shoot(self, color, y, damage):
        x = self.x
        if self.looking == 'R':
            x += self.width
        else:
            x -= 10
        x += (camera_x * 50)
        bullet = Bullet(GREEN, x, self.y + y, self.looking, pygame.time.get_ticks(), damage)
        x = 10 if bullet.direction == 'R' else (-10)
        
        if not bullet.would_collide(x, tile_map):
            self.bullets.append(bullet)
            self.last_bullet = bullet

    def would_collide(self, x, y, current_map, camera):
        character_rect = pygame.Rect(self.x + x, self.y + y, self.width, self.height)
        return would_collide(character_rect, current_map, camera=camera)

class Player(Character):
    def __init__(self, x, y, width, height, image, looking, health):
        super().__init__(x, y, width, height, 5, image, looking, health)
        self.jumping = False
        self.falling = False
        self.max_jumps = 25
        self.jumps_left = self.max_jumps

    def handle_movement(self, key):
        global camera_x

        if self.jumping:
            if not(self.would_collide(0, -self.speed, tile_map, True)) and self.jumps_left != 0:
                self.y -= self.speed
            else:
                self.jumping = False
                self.falling = True
                self.jumps_left = self.max_jumps
            self.jumps_left -= 1

        if not(self.would_collide(0, self.speed, tile_map, True)) and not(self.jumping):
            self.falling = True
            self.y += self.speed
        else:
            self.falling = False

        if key[pygame.K_a] and not(self.would_collide(-self.speed, 0, tile_map, True)):
            if self.looking != 'L':
                self.looking = 'L'
                self.image = pygame.transform.flip(self.image, True, False)
            if self.x - self.speed >= 0:
                self.x -= self.speed
            if (self.x % (camera_walk * 50) == 0 or self.x - self.speed < 0) and camera_x - camera_walk >= 0:
                camera_x -= camera_walk
                self.x += camera_walk * 50
            elif (self.x % (camera_walk * 50) == 0 or self.x - self.speed < 0):
                self.x += camera_x * 50
                camera_x = 0

        if key[pygame.K_d] and not(self.would_collide(self.speed, 0, tile_map, True)):
            if self.looking != 'R':
                self.looking = 'R'
                self.image = pygame.transform.flip(self.image, True, False)
            if self.x + self.speed + self.width <= width:
                self.x += self.speed
            if (self.x % (camera_walk * 50) == 0 or self.x + self.speed + self.width > width) and camera_x + camera_walk + 24 <= len(tile_map[0]):
                camera_x += camera_walk
                self.x -= camera_walk * 50
            elif (self.x % (camera_walk * 50) == 0 or self.x + self.speed + self.width > width):
                self.x -= ((len(tile_map[0]) - 24) - camera_x) * 50
                camera_x = len(tile_map[0]) - 24

        if key[pygame.K_w] and not(self.jumping) and not(self.falling):
            self.jumping = True

class Enemy(Character):
    def __init__(self, x, y, width, height, speed, image, looking, r, health):
        super().__init__(x, y, width, height, speed, image, looking, health)
        self.initial_x = x
        self.range = r

    def handle_movement(self, player):
        if player.x >= (self.initial_x - self.range) - (camera_x * 50) and player.x <= (self.initial_x + self.range * 2) - (camera_x * 50) and self.y == player.y:
            enemy_x = (self.x - (camera_x * 50))
            if enemy_x <= player.x:
                if self.looking != 'R':
                    self.looking = 'R'
                    self.image = pygame.transform.flip(self.image, True, False)
            else:
                if self.looking != 'L':
                    self.looking = 'L'
                    self.image = pygame.transform.flip(self.image, True, False)
        else:
            if self.looking == 'R':
                self.x += self.speed
                if self.x + self.speed > self.initial_x + self.range:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.looking = 'L'
            else:
                self.x -= self.speed
                if self.x - self.speed < self.initial_x:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.looking = 'R'

def draw_window(current_map, player, enemies):
    surface.blit(background, (0, 0))

    for y in range(len(current_map)):
        for x in range(camera_x, len(current_map[y])):
            if current_map[y][x] == 'X':
                if y != 0 and current_map[y - 1][x] != 'X':
                    surface.blit(snow, ((x - camera_x) * 50, y * 50))
                else:
                    surface.blit(dirt, ((x - camera_x) * 50, y * 50))

    for bullet in player.bullets:
        rect = pygame.Rect(bullet.x - (camera_x * 50), bullet.y, 10, 3)
        pygame.draw.rect(surface, bullet.color, rect)

    for enemy in enemies:
        for bullet in enemy.bullets:
            rect = pygame.Rect(bullet.x - (camera_x * 50), bullet.y, 10, 3)
            pygame.draw.rect(surface, bullet.color, rect)

        enemy_health_background = pygame.Rect(enemy.x - (camera_x * 50), enemy.y - 20, enemy.width, 10)
        enemy_health_bar = pygame.Rect(enemy.x - (camera_x * 50), enemy.y - 20, enemy.width * (enemy.health / enemy.max_health), 10)

        pygame.draw.rect(surface, RED, enemy_health_background)
        pygame.draw.rect(surface, DARKGREEN, enemy_health_bar)
        surface.blit(enemy.image, (enemy.x - (camera_x * 50), enemy.y))

    player_health_background = pygame.Rect(player.x, player.y - 20, player.width, 10)
    player_health_bar = pygame.Rect(player.x, player.y - 20, player.width * (player.health / player.max_health), 10)

    pygame.draw.rect(surface, RED, player_health_background)
    pygame.draw.rect(surface, DARKGREEN, player_health_bar)

    surface.blit(player.image, (player.x, player.y))

    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    fps = 60

    player = Player(50, 479, 47, 71, player_image, 'R', 100)

    enemies = []
    enemies.append(Enemy(500, 379, 47, 71, 3, enemy_image, 'R', 200, 50))

    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        key_pressed = pygame.key.get_pressed()
        player.handle_movement(key_pressed)

        for bullet in player.bullets:
            if bullet.x + 10 < 0 or bullet.x > (len(tile_map[0]) * 50):
                player.bullets.remove(bullet)
            bullet.move()

            x = 10 if bullet.direction == 'R' else (-10)
            if bullet.would_collide(x, tile_map):
                player.bullets.remove(bullet)

            enemy = bullet.touched_enemy(enemies)
            if enemy:
                enemy.health -= bullet.damage
                player.bullets.remove(bullet)
                if enemy.health <= 0:
                    enemies.remove(enemy)

        if key_pressed[pygame.K_SPACE] and (player.last_bullet == None or player.last_bullet.fired_at + 200 < pygame.time.get_ticks()):
            player.shoot(GREEN, 34, 25)

        for enemy in enemies:
            enemy.handle_movement(player)
            for bullet in enemy.bullets:
                if bullet.x + 10 < 0 or bullet.x > (len(tile_map[0]) * 50):
                    enemy.bullets.remove(bullet)
                bullet.move()

                x = 10 if bullet.direction == 'R' else (-10)
                if bullet.would_collide(x, tile_map):
                    enemy.bullets.remove(bullet)

        draw_window(tile_map, player, enemies)

if __name__ == '__main__':
    main()
