import pygame
import random
import time
import sys
from Button import *


SCREEN_WIDTH = 450
SCREEN_HEIGHT = 600

BASE_HEIGHT = 75

PIPE_WIDTH = 55
PIPE_HEIGHT = 275

SPACE_BETW_PIPES_X = 250
SPACE_BETW_PIPES_Y = 150

BIRD_WIDTH = 40
BIRD_HEIGHT = 28

GRAVITY = 0.075
FLYING_SPEED = 3



class Image:
	def __init__(self, image, x, y):
		self.image = image
		self.rect = self.image.get_rect(topleft=(x, y))

	def collide(self, other):
		return self.rect.colliderect(other.rect)

	def display(self, surface):
		surface.blit(self.image, self.rect)



class Bird(Image):
	def __init__(self, images, x, y):
		self.start_y = y
		self.images = images
		self.img_ind = 0
		self.image = self.images[0]
		self.is_flying = False
		self.dy = 0
		self.rect = self.image.get_rect(topleft=(x, y))

	def move(self, fly_sound):
		if self.is_flying:
			self.dy = 0
			self.dy -= FLYING_SPEED
			fly_sound.play()

		self.dy += GRAVITY
		self.rect.centery += self.dy

	def pass_through(self, pipe):
		return self.rect.left == pipe.rect.left and \
				self.rect.top > pipe.rect.bottom and \
				self.rect.bottom < pipe.rect.bottom+SPACE_BETW_PIPES_Y

	def display(self, surface):
		self.image = pygame.transform.rotate(self.images[self.img_ind], -self.dy * 8)
		super().display(surface)

	def reset(self):
		self.img_ind = 0
		self.image = self.images[0]
		self.is_flying = False
		self.dy = 0
		self.rect.top = self.start_y


def load_image(filename, size=None):
	image = pygame.image.load(filename).convert_alpha()
	if size is not None:
		image = pygame.transform.scale(image, size)
	return image


def display_text(surface, x, y, text, font_size, font_color):
	font = pygame.font.Font("game_font.ttf", font_size)
	text = font.render(text, True, font_color)
	surface.blit(text, (x, y))


def random_pipe_y():
	return random.randint(-8, 0) * 20


def get_pipes(num_pipes, start_x, pipe_image):
	pipes = []
	
	for i in range(num_pipes):
		x = i*SPACE_BETW_PIPES_X + start_x
		y = random_pipe_y()
		
		pipe = Image(pipe_image, x, y)
		pipes.append(pipe)
		
		flipped_pipe_img = pygame.transform.flip(pipe.image, False, True)
		flipped_pipe = Image(flipped_pipe_img, x, pipe.rect.bottom+SPACE_BETW_PIPES_Y)
		pipes.append(flipped_pipe)
	
	return pipes


def add_new_pipe(pipes):
	top_pipe = pipes.pop(0)
	bottom_pipe = pipes.pop(0)
	
	x = pipes[-2].rect.left + SPACE_BETW_PIPES_X
	top_pipe.rect.left = x
	bottom_pipe.rect.left = x
	
	y = random_pipe_y()
	top_pipe.rect.top = y
	bottom_pipe.rect.top = top_pipe.rect.bottom+SPACE_BETW_PIPES_Y
	
	pipes.append(top_pipe)
	pipes.append(bottom_pipe)


def draw_window(surface, background, pipes, bases, bird, score, game_state):
	background.display(surface)
	
	for pipe in pipes:
		pipe.display(surface)

	bird.display(surface)
	
	for base in bases:
		if game_state != "retry":
			if base.rect.left == -SCREEN_WIDTH:
				base.rect.left = SCREEN_WIDTH
			base.rect.left -= 1
		base.display(surface)
		
	if game_state != "retry":
		score_text = f"Score : {str(score).rjust(2, ' ')}"
		display_text(surface, 215, 25, score_text, 40, (255, 255, 255))


def draw_retry_box(surface, score, retry_button, quit_button):
	# border and background for retry window
	pygame.draw.rect(surface, (80, 80, 80), (90-4, 155-4, 270+8, 300+8))
	pygame.draw.rect(surface, (150, 150, 150), (90, 155, 270, 300))
	
	display_text(surface, 115, 190, "Game Over!!!", 35, (255, 255, 255))
	display_text(surface, 135, 240, f"Your Score: {score}", 25, (255, 255, 255))
	
	retry_button.display((100, 255, 100))
	quit_button.display((255, 100, 100))


def play_game():
	pygame.mixer.pre_init()
	pygame.init()

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Flappy Bird")
	pygame.display.set_icon(load_image("imgs/bird1.png"))
	
	clock = pygame.time.Clock()

	background_img = load_image("imgs/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
	base_img = load_image("imgs/base.png", (SCREEN_WIDTH, BASE_HEIGHT))
	pipe_img = load_image("imgs/pipe.png", (PIPE_WIDTH, PIPE_HEIGHT))
	pipe_img = pygame.transform.flip(pipe_img, False, True)
	bird_imgs = [pygame.transform.scale(
		load_image(f"imgs/bird{i}.png"), (BIRD_WIDTH, BIRD_HEIGHT)) for i in range(1, 4)]
	
	background = Image(background_img, 0, 0)
	bases = [Image(base_img, i, SCREEN_HEIGHT-BASE_HEIGHT) for i in (0, SCREEN_WIDTH)]
	pipes = get_pipes(3, SCREEN_WIDTH+100, pipe_img)
	bird = Bird(bird_imgs, SCREEN_WIDTH/2.5, (SCREEN_HEIGHT-BASE_HEIGHT)/2)

	fly_sound = pygame.mixer.Sound("sounds/fly.wav")
	hit_sound = pygame.mixer.Sound("sounds/hit.wav")
	score_sound = pygame.mixer.Sound("sounds/score.wav")

	retry_button = Button(screen, 120, 295, 200, 50, "Try Again")
	quit_button = Button(screen, 120, 370, 200, 50, "Quit")

	score = 0
	game_state = "start"   # game_states = ('start', 'play', 'retry')

	BIRDFLAP = pygame.USEREVENT
	pygame.time.set_timer(BIRDFLAP, 200)


	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
				elif event.key == pygame.K_SPACE:
					if game_state == "start":
						game_state = "play"
					if game_state == "play":
						bird.is_flying = True
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_SPACE:
					if game_state == "play":
						bird.is_flying = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if game_state == "retry":
					if retry_button.is_hovered():
						score = 0
						bird.reset()
						pipes = get_pipes(3, SCREEN_WIDTH+100, pipe_img)
						game_state = "start"
					elif quit_button.is_hovered():
						pygame.quit()
						sys.exit()
			if event.type == BIRDFLAP:
				if game_state != "retry":
					bird.img_ind += 1
					bird.img_ind %= 3


		draw_window(screen, background, pipes, bases, bird, score, game_state)
		
		if game_state == "play":
			for base in bases:
				if base.collide(bird):
					game_state = "retry"
					hit_sound.play()
			
			for pipe in pipes:
				if bird.pass_through(pipe):
					score += 1
					score_sound.play()
				elif pipe.collide(bird):
					game_state = "retry"
					hit_sound.play()
				pipe.rect.left -= 1
			
			if pipes[0].rect.left < -PIPE_WIDTH:
				add_new_pipe(pipes)

			bird.move(fly_sound)
		
		elif game_state == "retry":
			draw_retry_box(screen, score, retry_button, quit_button)

		pygame.display.update()
		clock.tick(120)



if __name__ == "__main__":
	play_game()


