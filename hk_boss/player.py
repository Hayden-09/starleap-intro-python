

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
		# allow a single double-jump while airborne
		self.can_double_jump = True
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
		# directional attack: 'left','right','up','down'
		self.attack_dir = 'right'

		# jump tuning: base jump power and double-jump multiplier
		self.jump_power = 420
		self.double_jump_multiplier = 0.8
		# track previous jump key state to detect a press (edge) rather than held
		self._jump_was_pressed = False

		# create a simple Hollow Knight-like sprite as a surface
		self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		self._make_sprite()

		# death / game-over animation state
		self.dead_anim = False
		self.dead_t = 0.0
		self.dead_duration = 2.0
		self.finished_death = False

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

		# Jump (W or Space) - detect key press edge so double-jump requires a separate press
		jump_now = bool(keys[pygame.K_w] or keys[pygame.K_SPACE])
		jump_pressed = jump_now and not self._jump_was_pressed
		if jump_pressed:
			if self.on_ground:
				self.vy = -self.jump_power
				self.on_ground = False
				# allow a double-jump after leaving ground
				self.can_double_jump = True
			elif self.can_double_jump and not self.on_ground:
				# consume double-jump and give a smaller upward impulse (80% of normal)
				self.vy = -int(self.jump_power * self.double_jump_multiplier)
				self.can_double_jump = False
		# store state for edge detection next frame
		self._jump_was_pressed = jump_now

		# dash: Shift or K
		if (keys[pygame.K_LSHIFT] or keys[pygame.K_k]) and self.dash_timer <= 0 and not self.is_dashing:
			self.is_dashing = True
			self.dash_t = 0.0
			self.dash_timer = self.dash_cooldown

		# attack: J (directional)
		if keys[pygame.K_j] and self.attack_timer <= 0 and not self.attacking:
			# determine attack direction from input priority: up/down then left/right then facing
			if keys[pygame.K_w] or keys[pygame.K_UP]:
				self.attack_dir = 'up'
			elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
				self.attack_dir = 'down'
			elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
				self.attack_dir = 'left'
			elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
				self.attack_dir = 'right'
			else:
				self.attack_dir = 'left' if self.facing < 0 else 'right'
			self.attacking = True
			self.attack_t = 0.0
			self.attack_timer = self.attack_cooldown

	def update(self, dt):
		# if in death animation, progress sink/fade and skip normal physics
		if self.dead_anim:
			self.dead_t += dt
			# sink downward slowly
			self.y += 80 * dt
			if self.dead_t >= self.dead_duration:
				self.finished_death = True
				self.dead_anim = False
			return

		# gravity
		self.vy += 1000 * dt
		nx = self.x + self.vx * dt
		ny = self.y + self.vy * dt

		# ground at y=500
		ground_y = 500
		if ny + self.height >= ground_y:
			ny = ground_y - self.height
			self.vy = 0
			# landed -> restore ground state and allow double-jump again
			self.on_ground = True
			self.can_double_jump = True

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
		# if in death animation, draw faded/scaled sprite
		if getattr(self, 'dead_anim', False):
			p = min(1.0, max(0.0, self.dead_t / max(1e-6, self.dead_duration)))
			alpha = int(255 * (1.0 - p))
			scale = max(0.2, 1.0 - 0.5 * p)
			w = max(1, int(self.width * scale))
			h = max(1, int(self.height * scale))
			temp = pygame.transform.smoothscale(self.sprite, (w, h))
			temp.set_alpha(alpha)
			# center scaled sprite
			cx = int(self.x + self.width / 2)
			cy = int(self.y + self.height / 2)
			surface.blit(temp, (cx - w // 2, cy - h // 2))
		else:
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
		# compute hitbox from original base sizes (original_w=40, original_h=22)
		# Base sizes and cumulative scaling factors
		orig_w = 40
		orig_h = 22
		# Previous cumulative multipliers: horizontal had +10% then +35% -> 1.10 * 1.35
		# User requested: decrease vertical by another 15% and increase horizontal by 10%
		# We'll apply these deltas on top of previous multipliers.
		horiz_multiplier = 1.10 * 1.35 * 1.10  # additional +10%
		vert_multiplier = 2.50 * 0.80 * 0.85  # previous 2.5 then *0.8 then -15% -> *0.85
		w = max(1, int(orig_w * horiz_multiplier))
		h = max(1, int(orig_h * vert_multiplier))
		# for up/down attacks swap width/height when returned (handled below)
		# direction-specific placement
		if self.attack_dir == 'right':
			ax = int(self.x + self.width - 6)
			ay = int(self.y + self.height // 2 - h // 2)
			return pygame.Rect(ax, ay, w, h)
		elif self.attack_dir == 'left':
			ax = int(self.x - w + 6)
			ay = int(self.y + self.height // 2 - h // 2)
			return pygame.Rect(ax, ay, w, h)
		elif self.attack_dir == 'up':
			# swap w/h for vertical attacks
			ax = int(self.x + self.width // 2 - h // 2)
			ay = int(self.y - w + 6)
			return pygame.Rect(ax, ay, h, w)
		elif self.attack_dir == 'down':
			ax = int(self.x + self.width // 2 - h // 2)
			ay = int(self.y + self.height - 6)
			return pygame.Rect(ax, ay, h, w)
		# fallback
		ax = int(self.x + self.width - 6)
		ay = int(self.y + self.height // 2 - h // 2)
		return pygame.Rect(ax, ay, w, h)

	def take_damage(self, amount):
		if self.invuln > 0:
			return
		self.health = max(0, self.health - amount)
		self.invuln = 0.8
		if self.health <= 0 and not getattr(self, 'dead_anim', False):
			# start death animation
			self.health = 0
			self.dead_anim = True
			self.dead_t = 0.0
import math

