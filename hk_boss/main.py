import pygame
import random
import pygame
import random
from player import Player
from boss import DoubleBoss
from hud import HUD

SCREEN_W, SCREEN_H = 960, 640


def create_boss(choice: int) -> DoubleBoss:
    """Create a DoubleBoss configured by preset choice (0 or 1)."""
    boss = DoubleBoss(620, 420)
    # preset 0: Hornet Twins — faster, lower HP, more projectiles
    if choice == 0:
        for part in (boss.left, boss.right):
            part.max_health = int(part.max_health * 0.8)
            part.health = part.max_health
            part.osc_speed *= 1.4
            part.osc_amp *= 1.1
            part.projectile_chance = 0.45
            part.attack_cooldown *= 0.9
    else:
        # preset 1: Mantis Overlords — bulkier, slower, big melee swings
        for part in (boss.left, boss.right):
            part.max_health = int(part.max_health * 1.6)
            part.health = part.max_health
            part.osc_speed *= 0.85
            part.osc_amp *= 1.0
            part.projectile_chance = 0.10
            part.attack_cooldown *= 1.2
    return boss


def draw_menu(surface, selection: int):
    surface.fill((12, 12, 18))
    # title
    font = pygame.font.SysFont(None, 64)
    t = font.render("Choose a Boss", True, (230, 220, 200))
    surface.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 48))

    small = pygame.font.SysFont(None, 24)
    desc0 = ["Hornet Twins", "Fast, lots of projectiles", "Lower HP, aggressive"]
    desc1 = ["Mantis Overlords", "High HP, big melee swings", "Slower movement"]

    # left panel
    lx = SCREEN_W // 4 - 160
    ly = 160
    pygame.draw.rect(surface, (40, 40, 60), (lx, ly, 320, 240))
    title = pygame.font.SysFont(None, 36).render(desc0[0], True, (240, 220, 200))
    surface.blit(title, (lx + 16, ly + 12))
    for i, line in enumerate(desc0[1:]):
        surface.blit(small.render(line, True, (200, 200, 200)), (lx + 16, ly + 60 + i * 22))

    # right panel
    rx = SCREEN_W * 3 // 4 - 160
    ry = 160
    pygame.draw.rect(surface, (40, 40, 60), (rx, ry, 320, 240))
    title2 = pygame.font.SysFont(None, 36).render(desc1[0], True, (240, 220, 200))
    surface.blit(title2, (rx + 16, ry + 12))
    for i, line in enumerate(desc1[1:]):
        surface.blit(small.render(line, True, (200, 200, 200)), (rx + 16, ry + 60 + i * 22))

    sel_x = lx if selection == 0 else rx
    pygame.draw.rect(surface, (200, 180, 60), (sel_x - 6, ly - 6, 332, 252), width=4)

    hint = small.render("Use ← → or A/D to choose, Enter to start", True, (180, 180, 180))
    surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 80))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    # game state: 'menu' or 'playing'
    game_state = 'menu'
    selection = 0

    player = None
    bosses = None
    hud = None

    # overlay state for game over / victory
    overlay_active = False
    overlay_t = 0.0
    overlay_duration = 1.6

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == 'menu':
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        selection = min(1, selection + 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        selection = max(0, selection - 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        player = Player(200, 450)
                        bosses = create_boss(selection)
                        hud = HUD(player, bosses)
                        game_state = 'playing'
                else:
                    # quick restart to menu
                    if event.key == pygame.K_r:
                        game_state = 'menu'
                        selection = 0
                        player = None
                        bosses = None
                        hud = None
                        overlay_active = False
                        overlay_t = 0.0

        keys = pygame.key.get_pressed()

        # update
        if game_state == 'playing' and player is not None and bosses is not None:
            # input only when player not in death animation
            if not getattr(player, 'dead_anim', False) and not getattr(player, 'finished_death', False):
                player.handle_input(keys, dt)
                player.update(dt)
            else:
                player.update(dt)

            bosses.update(dt, player)

            # collisions while alive
            if not getattr(player, 'dead_anim', False):
                for hb in bosses.get_active_hitboxes():
                    if hb.colliderect(player.get_hitbox()):
                        player.take_damage(1)
                for ph in bosses.get_projectile_hitboxes():
                    if ph.colliderect(player.get_hitbox()):
                        player.take_damage(1)

            # player's melee attack hitting bosses
            if getattr(player, 'attacking', False):
                ah = player.get_attack_hitbox()
                if bosses.hit_by_player(ah, player.attack_damage):
                    # small feedback could be added here
                    pass

            # overlay handling: if player finished death or bosses all finished, show overlay
            if getattr(player, 'finished_death', False) and not overlay_active:
                overlay_active = True
                overlay_t = 0.0
            if getattr(bosses, 'win', False) and not overlay_active:
                overlay_active = True
                overlay_t = 0.0

            if overlay_active:
                overlay_t += dt

        # draw background (simple cave gradient)
        for i in range(SCREEN_H):
            v = int(20 + (i / SCREEN_H) * 50)
            pygame.draw.line(screen, (v, v, v + 10), (0, i), (SCREEN_W, i))
        points = [(120, 40), (140, 20), (160, 40), (200, 10), (240, 40)]
        for x, y in points:
            pygame.draw.polygon(screen, (10, 10, 10), [(x, 0), (x + 20, y), (x - 20, y)])
        for x in range(80, SCREEN_W, 120):
            h = 30 + (x % 3) * 10
            pygame.draw.polygon(screen, (10, 10, 10), [(x, SCREEN_H), (x + 20, SCREEN_H - h), (x - 20, SCREEN_H - h)])

        # draw state-specific
        if game_state == 'menu':
            draw_menu(screen, selection)
        else:
            if bosses is not None:
                bosses.draw(screen)
            if player is not None:
                player.draw(screen)
            if hud is not None:
                hud.draw(screen)

            # show small hint to return to menu
            small = pygame.font.SysFont(None, 20)
            hint = small.render("Press R to return to menu", True, (160, 160, 160))
            screen.blit(hint, (SCREEN_W - hint.get_width() - 12, SCREEN_H - 28))

        # overlay (game over / victory)
        if overlay_active:
            p = min(1.0, overlay_t / max(1e-6, overlay_duration))
            alpha = int(220 * p)
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 72)
            if getattr(player, 'finished_death', False):
                text = font.render("GAME OVER", True, (240, 220, 200))
            else:
                text = font.render("VICTORY", True, (240, 220, 200))
            screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, SCREEN_H // 2 - 40))
            sub = pygame.font.SysFont(None, 28).render("Press R to return to menu", True, (220, 200, 180))
            screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 40))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()

