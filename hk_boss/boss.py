import pygame
import math
import random
from projectiles import spawn_volley


class BossPart:
	def __init__(self, x, y, color=(90, 160, 70), max_health=90):
		self.base_x = x
		self.base_y = y
		self.x = x
		self.y = y
		self.width = 64
		self.height = 56
		self.color = color
		self.attack_timer = 0.0
		# attack more frequently for higher difficulty
		self.attack_cooldown = 1.1 + random.random() * 0.6
		self.attacking = False
		self.attack_t = 0.0
		# telegraph (brief warning) before the attack begins
		self.telegraph = False
		self.telegraph_t = 0.0
		# whether next attack will be a projectile volley (set at telegraph start)
		self.next_attack_is_projectile = False
		# configurable projectile chance per attack (default 25%)
		self.projectile_chance = 0.25
		# make telegraph area smaller visually by reducing predicted radius multiplier and keep length short
		self.telegraph_len = 0.14
		self.max_health = max_health
		self.health = max_health
		self.alive = True
		# death / defeated animation state
		self.dead_anim = False
		self.dead_t = 0.0
		self.dead_duration = 1.6
		self.finished_death = False
		self.hurt_t = 0.0
		# independent movement parameters (horizontal + vertical)
		self.phase = random.random() * 10.0
		# horizontal movement: larger but slower overall
		self.osc_amp = 60 + random.random() * 30
		self.osc_speed = 1.6 + random.random() * 1.2
		# vertical movement parameters so parts can move up/down across the room
		self.phase_y = random.random() * 10.0
		self.osc_amp_y = 80 + random.random() * 100
		self.osc_speed_y = 0.7 + random.random() * 0.9

		# erratic jitter parameters (random impulses to make movement less predictable)
		self.jitter_next = random.uniform(0.6, 1.4)
		self.jitter_offset_x = 0.0
		self.jitter_offset_y = 0.0
		# reduce jitter strength to make movement less twitchy
		self.jitter_strength = 10 + random.random() * 30
		# small continuous noise to vary oscillation speed slightly
		self.osc_speed_variance = random.random() * 0.2

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
		# If currently running a death animation, progress it (even if not `alive`)
		if getattr(self, 'dead_anim', False):
			self.dead_t += dt
			# float upward a little and fade/scale handled in draw
			self.y -= 24 * dt
			if self.dead_t >= self.dead_duration:
				self.finished_death = True
				self.dead_anim = False
			return

		# skip normal updates if already marked not alive (shouldn't normally happen)
		if not self.alive:
			return

		self.hurt_t = max(0.0, self.hurt_t - dt)

		# independent faster horizontal oscillation around base_x
		t = pygame.time.get_ticks() / 1000.0 + self.phase
		target_x = self.base_x + math.sin(t * self.osc_speed) * self.osc_amp

		# add a small random variance to osc speed so each update feels different
		self.osc_speed += (random.random() - 0.5) * self.osc_speed_variance * dt

		# apply jitter impulses occasionally
		self.jitter_next -= dt
		if self.jitter_next <= 0:
			# pick a new random offset and reset timer
			self.jitter_offset_x = (random.random() * 2.0 - 1.0) * self.jitter_strength
			self.jitter_offset_y = (random.random() * 2.0 - 1.0) * (self.jitter_strength * 0.6)
			self.jitter_next = random.uniform(0.25, 1.2)

		# roaming: occasionally pick a roam target across the room
		if not hasattr(self, 'roam_target_x'):
			# default roam target is base_x
			self.roam_target_x = self.base_x
			self.roam_target_y = self.base_y
		# occasionally change roam target
		if random.random() < dt * 0.2:
			# choose a new roam point within room bounds (assume screen ~960x640)
			self.roam_target_x = random.uniform(100, 860)
			self.roam_target_y = random.uniform(80, 520)
		# blend base oscillation target with roam target so bosses cross the room
		blend_t = 0.35
		target_x = (target_x * (1.0 - blend_t)) + (self.roam_target_x * blend_t) + self.jitter_offset_x
		# lerp towards target_x but slower (more floaty)
		self.x += (target_x - self.x) * min(1.0, dt * 6.0)

		# vertical target and smoother movement vertically
		target_y = (self.base_y * (1.0 - blend_t)) + (self.roam_target_y * blend_t) + math.sin(t * self.osc_speed_y + self.phase_y) * self.osc_amp_y + self.jitter_offset_y
		self.y += (target_y - self.y) * min(1.0, dt * 4.0)

		# slight bias to approach player if far
		if player_x is not None:
			# only slightly bias toward the player; less teleport-y chase
			if abs(player_x - self.x) > 160:
				dir_sign = 1 if player_x > self.x else -1
				# gentler approach speed
				self.x += dir_sign * 80 * dt

		# attack logic (with a short telegraph before the actual swing)
		# increase attack cooldown by 150% (make cd 2.5x of original 1.1 base used earlier)
		self.attack_timer += dt
		if not hasattr(self, '_scaled_cd_done'):
			self.attack_cooldown = self.attack_cooldown * 2.5
			self._scaled_cd_done = True
		# slower attacks overall for clearer windows
		if not self.attacking and not self.telegraph and self.attack_timer >= self.attack_cooldown:
			# start telegraph (very brief) before the swing
			self.telegraph = True
			self.telegraph_t = 0.0
			self.attack_timer = 0.0

		# telegraph counting -> convert into actual attack when it ends
		if self.telegraph:
			self.telegraph_t += dt
			if self.telegraph_t >= self.telegraph_len:
				self.telegraph = False
				# decide attack type: 25% chance to use projectile volley instead of melee
				self.next_attack_is_projectile = (random.random() < 0.25)
				# reset spawned flag
				self.projectile_spawned = False
				# mark attacking state
				self.attacking = True
				self.attack_t = 0.0

		if self.attacking:
			self.attack_t += dt
			# slower attacks: give a longer active but less frequent strike
			if self.attack_t > 0.9:
				# finish attack; if it was a projectile attack we already spawned them at the start
				self.attacking = False
				self.attack_t = 0.0

	def get_sword_hitbox(self, facing=1):
		# legacy single-side sword hitbox (kept for compatibility) -> replaced by circular hitbox
		if not self.alive:
			return None
		if not self.attacking:
			return None
		# power scales the final attack radius; make radius 200% larger overall
		# if this was a projectile attack, the melee hitbox is ignored
		if getattr(self, 'is_projectile_attack_active', False):
			return None
		power = min(1.0, self.attack_t / 0.25)
		base_radius = 28 + int(28 * power)
		radius = int(base_radius * 3.0)
		# center of the part
		cx = int(self.x + self.width / 2)
		cy = int(self.y + self.height / 2)
		# return a rect that bounds the circular area (main code expects rects)
		return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

	def get_predicted_sword_hitbox(self, facing=1):
		"""Return the hitbox position the boss will use when it swings.
		Useful for drawing a telegraph even before `attacking` is True.
		"""
		if not self.alive:
			return None
		# estimate power based on telegraph progress (0..1)
		if self.telegraph:
			power = min(1.0, max(0.0, self.telegraph_t / max(1e-6, self.telegraph_len)))
		else:
			power = 0.0
		radius = 28 + int(28 * power)
		cx = int(self.x + self.width / 2)
		cy = int(self.y + self.height / 2)
		return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

	def take_damage(self, amount):
		if not self.alive:
			return
		self.health -= amount
		self.hurt_t = 0.25
		if self.health <= 0:
			self.health = 0
			# begin death animation rather than instantly vanishing
			self.alive = False
			self.dead_anim = True
			self.dead_t = 0.0
			self.projectile_spawned = False

	def get_rect(self):
		return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

	def draw(self, surface):
		# if fully finished death animation, draw nothing
		if getattr(self, 'finished_death', False):
			return

		# if in death animation, draw faded/scaled sprite with simple particle ring
		if getattr(self, 'dead_anim', False):
			p = min(1.0, max(0.0, self.dead_t / max(1e-6, self.dead_duration)))
			alpha = int(255 * (1.0 - p))
			scale = max(0.1, 1.0 - 0.6 * p)
			w = max(1, int(self.width * scale))	
			h = max(1, int(self.height * scale))
			# scaled sprite
			temp = pygame.transform.smoothscale(self.sprite, (w, h))
			temp.set_alpha(alpha)
			# center the scaled sprite on the original center
			cx = int(self.x + self.width / 2)
			cy = int(self.y + self.height / 2)
			surface.blit(temp, (cx - w // 2, cy - h // 2))
			# simple expanding ring particles
			r = int((self.width * 0.5) + p * 48)
			surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
			pygame.draw.circle(surf, (220, 180, 80, int(160*(1-p))), (r, r), r, width=3)
			surface.blit(surf, (cx - r, cy - r))
			return
		# hurt flash
		if self.hurt_t > 0:
			temp = self.sprite.copy()
			temp.fill((255, 120, 120, 80), special_flags=pygame.BLEND_RGBA_ADD)
			surface.blit(temp, (int(self.x), int(self.y)))
		else:
			surface.blit(self.sprite, (int(self.x), int(self.y)))


		# draw telegraph (brief translucent circle) before the attack
		if self.telegraph:
			hb = self.get_predicted_sword_hitbox()
			if hb:
				# pulsing alpha based on telegraph progress
				p = min(1.0, max(0.0, self.telegraph_t / max(1e-6, self.telegraph_len)))
				alpha = int(80 + 175 * p)
				d = hb.width
				surf = pygame.Surface((d, d), pygame.SRCALPHA)
				pygame.draw.circle(surf, (255, 200, 60, alpha), (d//2, d//2), d//2)
				# blit centered
				surface.blit(surf, (hb.x, hb.y))

		# draw circular attack when attacking
		if self.attacking:
			hb = self.get_sword_hitbox()
			if hb:
				d = hb.width
				surf = pygame.Surface((d, d), pygame.SRCALPHA)
				pygame.draw.circle(surf, (200, 180, 80, 200), (d//2, d//2), d//2)
				surface.blit(surf, (hb.x, hb.y))


class DoubleBoss:
	"""Manages two boss parts attacking in offset patterns"""
	def __init__(self, x, y):
		# left and right parts
		# give each part much more health so defeating both requires many attacks
		# double the base health so they require twice as many hits
		self.left = BossPart(x - 88, y, color=(100, 150, 90), max_health=90 * 2)
		self.right = BossPart(x + 24, y, color=(130, 110, 90), max_health=90 * 2)
		# ensure initial health values reflect doubled max
		self.left.health = self.left.max_health
		self.right.health = self.right.max_health
		# ensure both parts share the exact same cooldown window
		base_cd = 1.1 + random.random() * 0.6
		self.left.attack_cooldown = base_cd
		self.right.attack_cooldown = base_cd
		# offset their timers so attacks are interleaved (right will attack halfway through the cooldown)
		self.right.attack_timer = base_cd * 0.5
		self.left.attack_timer = 0.0
		# projectile list for boss volleys
		self.projectiles = []
		# win animation state
		self.win = False
		self.win_t = 0.0
		self.win_duration = 3.0

	def update(self, dt, player):
		# update parts independently and pass player's x for minor chasing
		self.left.update(dt, player_x=player.x)
		self.right.update(dt, player_x=player.x)

		# handle attacks that may spawn projectiles: if a part just entered attacking state and was flagged for projectile, spawn volley
		for part in (self.left, self.right):
			# if telegraph just finished and we've set next_attack_is_projectile, then at the moment attacking becomes True we should spawn
			if getattr(part, 'next_attack_is_projectile', False) and part.attacking and not getattr(part, 'projectile_spawned', False):
				# spawn volley centered on the part
				cx = int(part.x + part.width / 2)
				cy = int(part.y + part.height / 2)
				vol = spawn_volley(cx, cy, speed=260, count=7, spread=1.2)
				self.projectiles.extend(vol)
				part.projectile_spawned = True

		# update projectiles
		for p in list(self.projectiles):
			p.update(dt)
			if not p.alive:
				self.projectiles.remove(p)

		# check for win (both parts finished death)
		if not self.win and getattr(self.left, 'finished_death', False) and getattr(self.right, 'finished_death', False):
			self.win = True
			self.win_t = 0.0

		if self.win:
			self.win_t += dt

	def get_active_hitboxes(self):
		h = []
		for part in (self.left, self.right):
			hb = part.get_sword_hitbox()
			if hb:
				h.append(hb)
		return h

	def get_projectile_hitboxes(self):
		h = []
		for p in self.projectiles:
			h.append(p.get_rect())
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

		# draw projectiles
		for p in self.projectiles:
			p.draw(surface)

		# win animation: pulsing ring and floating text when both parts are defeated
		if self.win:
			p = min(1.0, max(0.0, self.win_t / max(1e-6, self.win_duration)))
			# pulsing ring at midpoint between parts
			cx = int((self.left.x + self.right.x) / 2 + (self.left.width/2))
			cy = int((self.left.y + self.right.y) / 2 + (self.left.height/2))
			radius = int(40 + p * 160)
			alpha = int(200 * (1.0 - abs(0.5 - p) * 2.0))
			surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
			pygame.draw.circle(surf, (240, 220, 140, alpha), (radius, radius), radius, width=6)
			surface.blit(surf, (cx - radius, cy - radius))
			# floating "Victory" text
			font = pygame.font.SysFont(None, 56)
			text = font.render("VICTORY", True, (240, 220, 160))
			# slight bobbing
			yoff = int(math.sin(self.win_t * 6.0) * 8)
			surface.blit(text, (cx - text.get_width()//2, cy - 24 + yoff))

