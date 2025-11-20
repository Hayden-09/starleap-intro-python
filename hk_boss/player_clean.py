import pygame


class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0.0
		self.vy = 0.0
		self.width = 40
		self.height = 56
		self.on_ground = False
		self.facing = 1
		self.health = 12
		self.invuln = 0.0

		# dash and attack
		self.dash_cooldown = 1.0
		self.dash_timer = 0.0
		self.is_dashing = False
		self.dash_time = 0.2
		self.dash_t = 0.0
		self.dash_speed = 700

		self.attack_cooldown = 0.5
		self.attack_timer = 0.0
		self.attacking = False
		self.attack_time = 0.18
		self.attack_t = 0.0
		self.attack_damage = 2

		# create a simple Hollow Knight-like sprite as a surface
		self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		self._make_sprite()

	def _make_sprite(self):
		s = self.sprite
		s.fill((0, 0, 0, 0))
		# mask / head
		pygame.draw.ellipse(s, (240, 240, 240), (6, 0, 28, 28))
		# eyes
		pygame.draw.rect(s, (20, 20, 20), (18, 8, 4, 4))
		pygame.draw.rect(s, (20, 20, 20), (24, 8, 4, 4))
		# body
		pygame.draw.rect(s, (200, 200, 200), (10, 24, 20, 28))
		# cloak
		pygame.draw.polygon(s, (40, 40, 60), [(8, 30), (32, 30), (24, 56), (16, 56)])

	def handle_input(self, keys, dt):
		speed = 220
		if keys[pygame.K_a] or keys[pygame.K_LEFT]:
			self.vx = -speed
			self.facing = -1
		elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
			self.vx = speed
			self.facing = 1
		else:
			self.vx = 0

		if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
			self.vy = -420
			self.on_ground = False

		# dash: Shift or K
		if (keys[pygame.K_LSHIFT] or keys[pygame.K_k]) and self.dash_timer <= 0 and not self.is_dashing:
			self.is_dashing = True
			self.dash_t = 0.0
			self.dash_timer = self.dash_cooldown

		# attack: J
		if keys[pygame.K_j] and self.attack_timer <= 0 and not self.attacking:
			self.attacking = True
			self.attack_t = 0.0
			self.attack_timer = self.attack_cooldown

	def update(self, dt):
		# gravity
		self.vy += 1000 * dt
		nx = self.x + self.vx * dt
		ny = self.y + self.vy * dt

		# ground at y=500
		ground_y = 500
		if ny + self.height >= ground_y:
			ny = ground_y - self.height
			self.vy = 0
			self.on_ground = True

		self.x = nx
		self.y = ny

		if self.invuln > 0:
			self.invuln = max(0.0, self.invuln - dt)

		# dash update
		if self.dash_timer > 0:
			self.dash_timer = max(0.0, self.dash_timer - dt)

		if self.is_dashing:
			self.dash_t += dt
			# during dash override horizontal velocity
			self.x += self.facing * self.dash_speed * dt
			# small vertical stability
			self.vy = 0
			if self.dash_t >= self.dash_time:
				self.is_dashing = False

		# attack update
		if self.attack_timer > 0:
			self.attack_timer = max(0.0, self.attack_timer - dt)
		if self.attacking:
			self.attack_t += dt
			if self.attack_t >= self.attack_time:
				self.attacking = False

	def draw(self, surface):
		# draw player at its position
		rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
		# flash when invulnerable
		if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
			temp = self.sprite.copy()
			temp.fill((255, 180, 180, 100), special_flags=pygame.BLEND_RGBA_ADD)
			surface.blit(temp, rect)
		else:
			surface.blit(self.sprite, rect)

		# draw attack hitbox briefly
		if self.attacking:
			ah = self.get_attack_hitbox()
			pygame.draw.rect(surface, (255, 200, 60), ah, 2)

	def get_hitbox(self):
		return pygame.Rect(int(self.x + 6), int(self.y + 6), self.width - 12, self.height - 12)

	def get_attack_hitbox(self):
		# short rectangle in front of player
		w = 40
		h = 22
		if self.facing >= 0:
			ax = int(self.x + self.width - 6)
		else:
			ax = int(self.x - w + 6)
		ay = int(self.y + self.height // 2 - h // 2)
		return pygame.Rect(ax, ay, w, h)

	def take_damage(self, amount):
		if self.invuln > 0:
			return
		self.health = max(0, self.health - amount)
		self.invuln = 0.8
