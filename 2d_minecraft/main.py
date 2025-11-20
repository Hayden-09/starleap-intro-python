"""Minimal 2D side-view block game using pygame"""
import pygame
from world import World
from player import Player

SCREEN_W, SCREEN_H = 800, 600
TILE = 32

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    world = World(width=200, height=60, tile_size=TILE)
    player = Player(x=100, y=100, world=world, tile_size=TILE)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                world.handle_mouse(event.button, mx, my, screen.get_size(), player)

        keys = pygame.key.get_pressed()
        player.handle_input(keys, dt)
        player.update(dt)

        screen.fill((135, 206, 235))  # sky color
        world.draw(screen, camera=player.camera)
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
