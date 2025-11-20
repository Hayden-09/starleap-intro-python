import pygame
import math
import random


class BossPart:
    def __init__(self, x, y, color=(90, 160, 70), max_health=12):
        self.base_x = x
        self.x = x
        self.y = y
        self.width = 64
        self.height = 56
        self.color = color
        self.attack_timer = 0.0
        self.attack_cooldown = 1.2 + random.random() * 0.6
        self.attacking = False
        self.attack_t = 0.0
        self.max_health = max_health
        self.health = max_health
        self.alive = True
        self.hurt_t = 0.0
        # independent movement parameters
        self.phase = random.random() * 10.0
        self.osc_amp = 48 + random.random() * 36
        self.osc_speed = 2.5 + random.random() * 2.0

        # sprite
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._make_sprite()

    def _make_sprite(self):
        s = self.sprite
        s.fill((0, 0, 0, 0))
        # body
        pygame.draw.ellipse(s, self.color, (6, 6, 52, 40))
        # head
        pygame.draw.circle(s, (200, 200, 200), (18, 18), 10)
        # antennae
        import pygame
        import math
        import random


        class BossPart:
            def __init__(self, x, y, color=(90, 160, 70), max_health=12):
                self.base_x = x
                self.x = x
                self.y = y
                self.width = 64
                self.height = 56
                self.color = color
                self.attack_timer = 0.0
                self.attack_cooldown = 1.2 + random.random() * 0.6
                self.attacking = False
                self.attack_t = 0.0
                self.max_health = max_health
                self.health = max_health
                self.alive = True
                self.hurt_t = 0.0
                # independent movement parameters
                self.phase = random.random() * 10.0
                self.osc_amp = 48 + random.random() * 36
                self.osc_speed = 2.5 + random.random() * 2.0

                # sprite
                self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self._make_sprite()

            def _make_sprite(self):
                s = self.sprite
                s.fill((0, 0, 0, 0))
                # body
                pygame.draw.ellipse(s, self.color, (6, 6, 52, 40))
                # head
                pygame.draw.circle(s, (200, 200, 200), (18, 18), 10)
                # antennae
                pygame.draw.line(s, (200, 200, 200), (10, 6), (4, -4), 3)
                pygame.draw.line(s, (200, 200, 200), (26, 6), (34, -4), 3)
                # eyes
                pygame.draw.circle(s, (10, 10, 10), (16, 16), 2)
                pygame.draw.circle(s, (10, 10, 10), (22, 16), 2)

            def update(self, dt, player_x=None):
                if not self.alive:
                    return

                self.hurt_t = max(0.0, self.hurt_t - dt)

                # independent faster horizontal oscillation around base_x
                t = pygame.time.get_ticks() / 1000.0 + self.phase
                target_x = self.base_x + math.sin(t * self.osc_speed) * self.osc_amp

                # lerp towards target_x for smooth quick movement
                self.x += (target_x - self.x) * min(1.0, dt * 8.0)

                # slight bias to approach player if far
                if player_x is not None:
                    if abs(player_x - self.x) > 120:
                        dir_sign = 1 if player_x > self.x else -1
                        self.x += dir_sign * 60 * dt

                # attack logic
                self.attack_timer += dt
                if not self.attacking and self.attack_timer >= self.attack_cooldown:
                    self.attacking = True
                    self.attack_t = 0.0
                    self.attack_timer = 0.0
                if self.attacking:
                    self.attack_t += dt
                    if self.attack_t > 0.45:
                        self.attacking = False

            def get_sword_hitbox(self, facing=1):
                if not self.alive:
                    return None
                # when attacking produce a short-lived arc/hitbox in front of the boss
                if not self.attacking:
                    return None
                power = min(1.0, self.attack_t / 0.25)
                w = 28 + int(20 * power)
                h = 20
                if facing >= 0:
                    hx = int(self.x + self.width - 8)
                else:
                    hx = int(self.x - w + 8)
                hy = int(self.y + 18 - h // 2)
                return pygame.Rect(hx, hy, w, h)

            def take_damage(self, amount):
                if not self.alive:
                    return
                self.health -= amount
                self.hurt_t = 0.25
                if self.health <= 0:
                    self.health = 0
                    self.alive = False

            def get_rect(self):
                return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

            def draw(self, surface):
                if not self.alive:
                    # draw a faint corpse or nothing
                    return
                # hurt flash
                if self.hurt_t > 0:
                    temp = self.sprite.copy()
                    temp.fill((255, 120, 120, 80), special_flags=pygame.BLEND_RGBA_ADD)
                    surface.blit(temp, (int(self.x), int(self.y)))
                else:
                    surface.blit(self.sprite, (int(self.x), int(self.y)))

                # draw sword when attacking
                if self.attacking:
                    hb = self.get_sword_hitbox()
                    if hb:
                        pygame.draw.rect(surface, (180, 180, 60), hb)


        class DoubleBoss:
            """Manages two boss parts attacking in offset patterns"""
            def __init__(self, x, y):
                # left and right parts
                self.left = BossPart(x - 88, y, color=(100, 150, 90), max_health=16)
                self.right = BossPart(x + 24, y, color=(130, 110, 90), max_health=14)
                # offset their cooldowns so attacks are interleaved
                self.right.attack_timer = 0.6
                self.left.attack_timer = 0.0

            def update(self, dt, player):
                # update parts independently and pass player's x for minor chasing
                self.left.update(dt, player_x=player.x)
                self.right.update(dt, player_x=player.x)

            def get_active_hitboxes(self):
                h = []
                for part, f in ((self.left, -1), (self.right, 1)):
                    hb = part.get_sword_hitbox(facing=f)
                    if hb:
                        h.append(hb)
                return h

            def hit_by_player(self, rect, damage):
                """Apply damage if the player's attack rect overlaps a living part."""
                hit = False
                for part in (self.left, self.right):
                    if not part.alive:
                        continue
                    if rect.colliderect(part.get_rect()):
                        part.take_damage(damage)
                        hit = True
                return hit

            def draw(self, surface):
                # draw simple shadows under each alive part
                if self.left.alive:
                    pygame.draw.ellipse(surface, (10, 10, 10, 80), (self.left.x + 8, self.left.y + self.left.height - 6, 64, 16))
                if self.right.alive:
                    pygame.draw.ellipse(surface, (10, 10, 10, 80), (self.right.x + 8, self.right.y + self.right.height - 6, 64, 16))
                self.left.draw(surface)
                self.right.draw(surface)
