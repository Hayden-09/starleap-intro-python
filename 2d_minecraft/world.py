import random
import pygame
from tiles import TileType

class World:
    def __init__(self, width=200, height=60, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = [[TileType.AIR for _ in range(height)] for _ in range(width)]
        self.generate_heightmap()

    def generate_heightmap(self):
        ground_height = self.height // 3
        noise = [0] * self.width
        for x in range(self.width):
            if x == 0:
                noise[x] = ground_height
            else:
                noise[x] = max(3, noise[x-1] + random.randint(-1, 2))

        for x in range(self.width):
            h = min(self.height-1, noise[x] + random.randint(0, 3))
            for y in range(self.height):
                if y >= h:
                    # top layers different types
                    if y == h:
                        self.tiles[x][y] = TileType.GRASS
                    elif y < h + 4:
                        self.tiles[x][y] = TileType.DIRT
                    else:
                        self.tiles[x][y] = TileType.STONE

    def draw(self, surface, camera):
        tw = self.tile_size
        cols = surface.get_width() // tw + 3
        rows = surface.get_height() // tw + 3
        start_x = max(0, camera.x // tw - cols//2)
        start_y = max(0, camera.y // tw - rows//2)

        for i in range(start_x, min(self.width, start_x + cols)):
            for j in range(start_y, min(self.height, start_y + rows)):
                tile = self.tiles[i][j]
                if tile != TileType.AIR:
                    rect = pygame.Rect((i * tw) - camera.x + surface.get_width()//2,
                                       (j * tw) - camera.y + surface.get_height()//2,
                                       tw, tw)
                    pygame.draw.rect(surface, tile.color, rect)
                    pygame.draw.rect(surface, (0,0,0), rect, 1)

    def world_to_tile(self, wx, wy, screen_size, camera):
        sw, sh = screen_size
        tx = (wx - sw//2 + camera.x) // self.tile_size
        ty = (wy - sh//2 + camera.y) // self.tile_size
        return int(tx), int(ty)

    def handle_mouse(self, button, mx, my, screen_size, player):
        tx, ty = self.world_to_tile(mx, my, screen_size, player.camera)
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return
        if button == 1:
            # left click: remove
            self.tiles[tx][ty] = TileType.AIR
        elif button == 3:
            # right click: place dirt if empty
            if self.tiles[tx][ty] == TileType.AIR:
                self.tiles[tx][ty] = TileType.DIRT
