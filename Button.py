import pygame


class Button:
	def __init__(self, surface, x, y, width, height, text=""):
		self.surface = surface
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text


	def is_hovered(self):
		cursorX, cursorY = pygame.mouse.get_pos()
		return (self.x <= cursorX <= self.x + self.width) and \
			(self.y <= cursorY <= self.y + self.height)


	def display(self, hovered_bg_color):
		if self.is_hovered():
			bg_color = hovered_bg_color
		else:
			bg_color = (255, 255, 255)
		
		surface = self.surface
		x = self.x
		y = self.y
		width = self.width
		height = self.height

		# Border and background for the text
		pygame.draw.rect(surface, (50, 50, 50), (x-2, y-2, width+4, height+4))
		pygame.draw.rect(surface, bg_color, (x, y, width, height))

		font = pygame.font.SysFont("Courier", 32)
		text = font.render(self.text, True, (0, 0, 0))
		text_x = x + (width - text.get_width())/2
		text_y = y + (height - text.get_height())/2
		surface.blit(text, (text_x, text_y))


