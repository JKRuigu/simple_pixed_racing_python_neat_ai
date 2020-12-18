import pygame
import os
import random
import math

WIDTH, HEIGHT = 500, 500
# LOAD ASSETS
BLUE_CAR = pygame.image.load(os.path.join("imgs", "blue_car-removebg-preview.png"))
GREEN_CAR = pygame.image.load(os.path.join("imgs", "green_car-removebg-preview.png"))
STRIPE = pygame.image.load(os.path.join("imgs", "stripe.jpg"))
IMG_ICON = pygame.image.load(os.path.join("imgs", "icon.png"))

# BACKGROUND
BG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg3-removebg-preview.png")), (WIDTH, HEIGHT))
BG_START = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "background-black.png")), (WIDTH, HEIGHT))


# SETUP GAME
pygame.font.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")
pygame.display.set_icon(IMG_ICON)

class Car:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.x += vel
	def vertical(self,vel):
		self.y += vel
	def collision(self,x,y):
		distance = math.sqrt((math.pow(self.x - x,2))+(math.pow(self.y - y,2)))

		if distance <27:
			print('------YESS------')
			return True
		else:
			return False

class Stripe:
	def __init__(self, x,y,img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self,win):
		win.blit(self.img,(self.x,self.y))
	
	def move(self,vel):
		self.y+=vel

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def getRandomX():
	return random.randrange(60, 363)

def getRandomY():
	return random.randrange(-20, 0)

def background(win,stripes,speed):
	win.fill((0,0,0))		
	win.blit(BG, (0,0))	

	for stripe in stripes:
		if stripe.y >600:
			stripes.pop(stripes.index(stripe))			
		else:
			stripe.move(4)
			stripe.draw(win)	
		if stripe.y >50 and len(stripes) <6:
			stripes.append(Stripe(200,-150,STRIPE))	
	# pygame.display.update()


def main():
	run = True
	FPS = 60
	distance = 0
	score = 0
	font = pygame.font.SysFont("comicsans", 20)

	# 60,
	car = Car(363,400,BLUE_CAR)
	clock = pygame.time.Clock()
	traffic = [Car(getRandomX(),getRandomY(),GREEN_CAR),Car(getRandomX(),getRandomY(),GREEN_CAR)]
	stripes = [Stripe(200,50,STRIPE),Stripe(200,200,STRIPE),Stripe(200,350,STRIPE)]
	speed = 2
	while run:
		clock.tick(FPS)
		distance+=1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		#MOVEMENTS
		keys = pygame.key.get_pressed()

		if keys[pygame.K_LEFT] and car.x > 32: # left
			car.x -= speed

		if keys[pygame.K_RIGHT] and car.x < 421: # left
			car.x += speed 

		background(WIN,stripes,speed)

			#MOVE TRAFFIC
		for vehicle in traffic:
			if vehicle.y >500:
				traffic.pop(traffic.index(vehicle))
				score+=10			
			else:
				vehicle.vertical(speed)
				vehicle.draw(WIN)	
			if vehicle.y >250 and len(traffic) <3:
				traffic.append(Car(getRandomX(),getRandomY(),GREEN_CAR))
			col = collide(vehicle,car)
			if col == True:
				lost = font.render("You Lost!", 1, (255,255,255))
				WIN.blit(lost, (WIDTH/2 - lost.get_width()/2, 350))
				run = False



		car.draw(WIN)
		distances = font.render(f"Distance: {distance}", 1, (255,255,255))	
		scores = font.render(f"Score: {score}", 1, (255,255,255))	
		WIN.blit(distances, (50, 0))
		WIN.blit(scores, (50, 20))

		pygame.display.update()


def main_menu():
	title_font = pygame.font.SysFont("comicsans", 20)
	run = True
	while run:
		WIN.blit(BG_START, (0,0))
		title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()				
	pygame.quit()

main_menu()