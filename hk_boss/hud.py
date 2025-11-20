import pygame


class HUD:
	def __init__(self, player, bosses):
		self.player = player
		self.bosses = bosses

	def draw(self, surface):
		# draw player health
		x = 12
		y = 12
		for i in range(self.player.health):
			pygame.draw.rect(surface, (200, 80, 80), (x + i * 14, y, 12, 12))
		# boss name
		font = pygame.font.SysFont('arial', 18)
		text = font.render('DOUBLE HOLLOW-BUG', True, (230, 230, 230))
		surface.blit(text, (surface.get_width() - text.get_width() - 12, 12))

		# draw boss health bars (left and right)
		left = self.bosses.left
		right = self.bosses.right
		bar_w = 140
		bar_h = 10
		gap = 8
		sx = surface.get_width() // 2 - (bar_w + gap // 2)
		sy = 12

		def draw_bar(part, x, y):
			# background
			pygame.draw.rect(surface, (40, 40, 40), (x, y, bar_w, bar_h))
			if part.alive:
				frac = max(0.0, part.health / part.max_health)
				pygame.draw.rect(surface, (180, 50, 50), (x, y, int(bar_w * frac), bar_h))
			else:
				pygame.draw.rect(surface, (90, 90, 90), (x, y, bar_w, bar_h))

		draw_bar(left, sx - bar_w - gap, sy)
		draw_bar(right, sx + gap, sy)

