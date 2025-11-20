import pygame
from dataclasses import dataclass


@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0


class Player:
    def __init__(self, x, y, world, tile_size=32):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.world = world
        self.tile_size = tile_size
        self.width = int(tile_size * 0.8)
        self.height = int(tile_size * 1.6)
        self.on_ground = False
        self.camera = Camera(x, y)

    def handle_input(self, keys, dt):
        accel = 800
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -200
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 200
        else:
            self.vx = 0

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy = -420
            self.on_ground = False

    def update(self, dt):
        # gravity
        self.vy += 1000 * dt
        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt

        # simple collision with world tiles (AABB vs tiles)
        # horizontal
        if not self._collides_at(nx, self.y):
            self.x = nx
        else:
            self.vx = 0

        # vertical
        if not self._collides_at(self.x, ny):
            self.y = ny
            self.on_ground = False
        else:
            # hit ground or ceiling
            if self.vy > 0:
                # landed
                self.on_ground = True
            self.vy = 0

        # update camera to follow player
        self.camera.x = int(self.x)
        self.camera.y = int(self.y)

    def _collides_at(self, px, py):
        # check corners
        tw = self.tile_size
        left = int(px - self.width//2)
        right = int(px + self.width//2 - 1)
        top = int(py - self.height)
        bottom = int(py - 1)

        # check tiles overlapped
        for sx in (left, right):
            for sy in (top, bottom):
                tx = sx // tw
                ty = sy // tw
                if tx < 0 or ty < 0 or tx >= self.world.width or ty >= self.world.height:
                    continue
                if self.world.tiles[tx][ty] != None and self.world.tiles[tx][ty].is_solid:
                    return True
        return False

    def draw(self, surface):
        cx = surface.get_width()//2
        cy = surface.get_height()//2
        rect = pygame.Rect(cx - self.width//2, cy - self.height, self.width, self.height)
        pygame.draw.rect(surface, (255, 100, 100), rect)
        pygame.draw.rect(surface, (0,0,0), rect, 2)
