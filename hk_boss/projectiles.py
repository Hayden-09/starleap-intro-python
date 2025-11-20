import pygame
import math

class Projectile:
	"""A small projectile spawned by bosses."""
	def __init__(self, x, y, vx, vy, radius=6, color=(200,160,60), life=3.0, damage=1):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.radius = radius
		self.color = color
		self.life = life
		self.damage = damage
		self.alive = True

	def update(self, dt):
		self.x += self.vx * dt
		self.y += self.vy * dt
		self.life -= dt
		if self.life <= 0:
			self.alive = False

	def draw(self, surface):
		r = int(self.radius)
		pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)

	def get_rect(self):
		return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), int(self.radius*2), int(self.radius*2))


def spawn_volley(center_x, center_y, speed=220, count=6, spread=0.6):
	"""Return a list of Projectile objects in a spread away from center.

	spread controls angle spread in radians; count is number of projectiles.
	They are emitted outward in an arc centered horizontally away from the boss.
	"""
	projs = []
	# emit in a semi-circle downward+outward pattern; we'll spread angles across [-spread, +spread]
	for i in range(count):
		t = -spread + (i / max(1, count - 1)) * (spread * 2)
		angle = math.pi/2 + t  # pi/2 is downward; tweak to bias outward
		vx = math.cos(angle) * speed
		vy = math.sin(angle) * speed
		p = Projectile(center_x, center_y, vx, vy, radius=6, color=(200,160,60), life=3.0, damage=1)
		projs.append(p)
	return projs

