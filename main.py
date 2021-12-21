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

camera_x = 0
camera_walk = 8

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

tile_map = [
    '.......................................................',
    '.......................................................',
    '.......................................................',
    '.......................................................',
    '.......................................................',
    '.......................................................',
    '.......................................................',
    '.............................XXXXXX....................',
    '...........................XXXXXXXXXX..................',
    '.........XXXXXXX..........XXXXXXXXXXXX.................',
    '.........................XXXXXXXXXXXXXXX...............',
    'XXXXXXXX.........XXXXXXXXXXXXXXXXXXXXXXXX..............',
    'XXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

def colliding(rect1, rect2):
    if not(rect1.x + rect1.width <= rect2.x or rect2.x + rect2.width <= rect1.x):
        if not(rect1.y + rect1.height <= rect2.y or rect2.y + rect2.height <= rect1.y):
            return True
    return False

class Character:
    def __init__(self, x, y, width, height, speed, image, looking):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.image = image
        self.looking = looking

    def would_collide(self, x, y, current_map):
        character_rect = pygame.Rect(self.x + x, self.y + y, self.width, self.height)

        for y in range(len(current_map)):
            for x in range(camera_x, len(current_map[y])):
                if current_map[y][x] == 'X':
                    rect = pygame.Rect((x - camera_x) * 50, y * 50, 50, 50)
                    if colliding(character_rect, rect):
                        return True
        return False

class Player(Character):
    def __init__(self, x, y, width, height, image, looking):
        super().__init__(x, y, width, height, 5, image, looking)
        self.jumping = False
        self.falling = False
        self.max_jumps = 25
        self.jumps_left = self.max_jumps

    def handle_movement(self, key):
        global camera_x

        if self.jumping:
            if not(self.would_collide(0, -self.speed, tile_map)) and self.jumps_left != 0:
                self.y -= self.speed
            else:
                self.jumping = False
                self.falling = True
                self.jumps_left = self.max_jumps
            self.jumps_left -= 1

        if not(self.would_collide(0, self.speed, tile_map)) and not(self.jumping):
            self.falling = True
            self.y += self.speed
        else:
            self.falling = False

        if key[pygame.K_a] and not(self.would_collide(-self.speed, 0, tile_map)):
            if self.looking != 'L':
                self.looking = 'L'
                self.image = pygame.transform.flip(self.image, True, False)
            if self.x - self.speed >= 0:
                self.x -= self.speed
            if (self.x % (camera_walk * 50) == 0 or self.x - self.speed < 0) and camera_x - camera_walk >= 0:
                camera_x -= camera_walk
                self.x += (camera_walk * 50)
            elif (self.x % (camera_walk * 50) == 0 or self.x - self.speed < 0) and camera_x != 0:
                self.x += camera_x * 50
                camera_x = 0

        if key[pygame.K_d] and not(self.would_collide(self.speed, 0, tile_map)):
            if self.looking != 'R':
                self.looking = 'R'
                self.image = pygame.transform.flip(self.image, True, False)
            if self.x + self.speed + self.width <= width:
                self.x += self.speed
            if (self.x % (camera_walk * 50) == 0 or self.x + self.speed + self.width > width) and camera_x + camera_walk + 24 <= len(tile_map[0]):
                camera_x += camera_walk
                self.x -= (camera_walk * 50)
            elif (self.x % (camera_walk * 50) == 0 or self.x + self.speed + self.width > width) and camera_x != (len(tile_map[0]) - 24):
                self.x -= ((len(tile_map[0]) - 24) - camera_x) * 50
                camera_x = len(tile_map[0]) - 24

        if key[pygame.K_w] and not(self.jumping) and not(self.falling):
            self.jumping = True


def draw_window(current_map, player):
    surface.blit(background, (0, 0))

    for y in range(len(current_map)):
        for x in range(camera_x, len(current_map[y])):
            if current_map[y][x] == 'X':
                if y != 0 and current_map[y - 1][x] != 'X':
                    surface.blit(snow, ((x - camera_x) * 50, y * 50))
                else:
                    surface.blit(dirt, ((x - camera_x) * 50, y * 50))

    surface.blit(player.image, (player.x, player.y))

    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    fps = 60

    player = Player(50, 479, 47, 71, player_image, 'R')

    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        key_pressed = pygame.key.get_pressed()
        player.handle_movement(key_pressed)

        draw_window(tile_map, player)

if __name__ == '__main__':
    main()
