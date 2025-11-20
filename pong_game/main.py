import pygame
import random
import sys

SCREEN_W, SCREEN_H = 960, 640


class Paddle:
    def __init__(self, x, y, w=12, h=100):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = 420

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def move(self, dy, dt):
        self.y += dy * self.speed * dt
        self.y = max(0, min(SCREEN_H - self.h, self.y))


class Ball:
    def __init__(self, x, y, vx=240, vy=0, radius=8):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def get_rect(self):
        r = int(self.radius)
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt


def spawn_ball(center=True):
    angle = random.uniform(-0.6, 0.6)
    speed = random.uniform(200, 320)
    vx = speed * (1 if random.random() < 0.5 else -1) * abs(math_cos(angle))
    vy = speed * math_sin(angle)
    if center:
        return Ball(SCREEN_W / 2, SCREEN_H / 2, vx, vy)
    else:
        # spawn randomly near center
        return Ball(random.uniform(SCREEN_W*0.3, SCREEN_W*0.7), random.uniform(SCREEN_H*0.25, SCREEN_H*0.75), vx, vy)


def math_cos(a):
    import math
    return math.cos(a)


def math_sin(a):
    import math
    return math.sin(a)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    left = Paddle(20, SCREEN_H / 2 - 50)
    right = Paddle(SCREEN_W - 32, SCREEN_H / 2 - 50)

    # initial ball
    balls = [Ball(SCREEN_W / 2, SCREEN_H / 2, vx=260 * (1 if random.random() < 0.5 else -1), vy=random.uniform(-120, 120))]

    score = [0, 0]

    bounce_streak = 0  # consecutive bounces without any ball leaving bounds

    font = pygame.font.SysFont(None, 36)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # reset
                    balls = [Ball(SCREEN_W / 2, SCREEN_H / 2, vx=260 * (1 if random.random() < 0.5 else -1), vy=random.uniform(-120, 120))]
                    score = [0, 0]
                    bounce_streak = 0

        keys = pygame.key.get_pressed()
        # left paddle
        ly = 0
        if keys[pygame.K_w]:
            ly = -1
        elif keys[pygame.K_s]:
            ly = 1
        left.move(ly, dt)

        # right paddle
        ry = 0
        if keys[pygame.K_UP]:
            ry = -1
        elif keys[pygame.K_DOWN]:
            ry = 1
        right.move(ry, dt)

        # update balls; collect outs
        outs = []
        any_out = False
        new_bounce_events = 0
        for b in list(balls):
            b.update(dt)

            # top/bottom collision
            if b.y - b.radius <= 0:
                b.y = b.radius
                b.vy *= -1
                new_bounce_events += 1
            elif b.y + b.radius >= SCREEN_H:
                b.y = SCREEN_H - b.radius
                b.vy *= -1
                new_bounce_events += 1

            # paddle collisions (AABB approximations)
            if b.vx < 0:
                if b.get_rect().colliderect(left.get_rect()):
                    b.x = left.x + left.w + b.radius
                    b.vx *= -1.03
                    # add some spin based on where it hit
                    offset = (b.y - (left.y + left.h / 2)) / (left.h / 2)
                    b.vy += offset * 180
                    new_bounce_events += 1
            else:
                if b.get_rect().colliderect(right.get_rect()):
                    b.x = right.x - b.radius
                    b.vx *= -1.03
                    offset = (b.y - (right.y + right.h / 2)) / (right.h / 2)
                    b.vy += offset * 180
                    new_bounce_events += 1

            # out of bounds
            if b.x < -50:
                score[1] += 1
                balls.remove(b)
                any_out = True
            elif b.x > SCREEN_W + 50:
                score[0] += 1
                balls.remove(b)
                any_out = True

        # bounce streak handling
        if any_out:
            bounce_streak = 0
        else:
            if new_bounce_events > 0:
                bounce_streak += new_bounce_events
                # spawn a ball every 10 bounces
                while bounce_streak >= 10:
                    # add a new ball near center with random direction
                    balls.append(Ball(SCREEN_W / 2, SCREEN_H / 2, vx=260 * (1 if random.random() < 0.5 else -1), vy=random.uniform(-140, 140)))
                    bounce_streak -= 10

        # ensure at least one ball exists
        if len(balls) == 0:
            balls.append(Ball(SCREEN_W / 2, SCREEN_H / 2, vx=260 * (1 if random.random() < 0.5 else -1), vy=random.uniform(-120, 120)))

        # draw
        screen.fill((10, 10, 30))
        # center line
        for i in range(0, SCREEN_H, 24):
            pygame.draw.rect(screen, (70, 70, 90), (SCREEN_W // 2 - 4, i + 8, 8, 12))

        # paddles
        pygame.draw.rect(screen, (200, 200, 200), left.get_rect())
        pygame.draw.rect(screen, (200, 200, 200), right.get_rect())

        # balls
        for b in balls:
            pygame.draw.circle(screen, (240, 200, 60), (int(b.x), int(b.y)), b.radius)

        # HUD
        t = font.render(f"{score[0]}  -  {score[1]}", True, (220, 220, 220))
        screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 20))
        info = font.render(f"Balls: {len(balls)}  Bounces to next: {max(0, 10 - (bounce_streak % 10))}", True, (180, 180, 180))
        screen.blit(info, (20, 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
