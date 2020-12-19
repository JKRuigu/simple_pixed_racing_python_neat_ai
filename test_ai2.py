"""
The classic game of Racing Game. Make with python
and pygame. Features pixel perfect collision using masks :o

Date Modified:  17 Dec 2020
Author: JKRuigu
Estimated Work Time: 48 hours (1 just for that damn collision)
"""

import pygame
import os
import random
import math
import neat
import pickle

WIDTH, HEIGHT = 500, 500
gen  =0
top  =0
g_top  =0
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

# collide function
def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# gets random range in x-axis
def getRandomX():
	return random.randrange(60, 363)

# gets random range in y-axis
def getRandomY():
	return random.randrange(-20, 0)
# set the background loaing stripes,car,traffice
def background(win,stripes,speed,car,traffic,distance,score):
	win.fill((0,0,0))		
	win.blit(BG, (0,0))	
	font = pygame.font.SysFont("comicsans", 30)	

	for stripe in stripes:
		if stripe.y >600:
			stripes.pop(stripes.index(stripe))			
		else:
			stripe.move(4)
			stripe.draw(win)	
		if stripe.y >50 and len(stripes) <6:
			stripes.append(Stripe(200,-150,STRIPE))	

	car.draw(win)

	for vehicle in traffic:
		vehicle.draw(win)		
	#displays information back to the user distance,score 
	distances = font.render(f"Distance: {distance}", 1, (255,255,255))	
	scores = font.render(f"Score: {score}", 1, (255,255,255))
	WIN.blit(distances, (50, 0))
	WIN.blit(scores, (50, 20))

	pygame.display.update()

# main function saved genomes for neat network
def eval_genomes(genomes, config):

	car = Car(getRandomX(),400,BLUE_CAR)
	run = True
	FPS = 60
	distance = 0
	score = 0
	speed = 3
	number_of_traffic = 2
	clock = pygame.time.Clock()
	#loaing the network
	nets = []

	for genome_id, genome in genomes:
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)

	#setting the traffic	
	traffic = [Car(getRandomX(),getRandomY(),GREEN_CAR),Car(getRandomX(),getRandomY(),GREEN_CAR)]
	stripes = [Stripe(200,50,STRIPE),Stripe(200,200,STRIPE),Stripe(200,350,STRIPE)]

	while run:
		clock.tick(FPS)
		distance+=1

		#MOVEMENTS
		keys = pygame.key.get_pressed()

		if keys[pygame.K_LEFT] and car.x > 32: # left
			car.x -= speed

		if keys[pygame.K_RIGHT] and car.x < 421: # left
			car.x += speed 

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		for vehicle in traffic:
			output = nets[0].activate((car.x, abs(car.x - vehicle.x), abs(car.y - vehicle.y)))
			print(output)
			if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
				car.move(-2)
			else:
				car.move(2)	
		
		for vehicle in traffic:
			if vehicle.y >500:
				traffic.pop(traffic.index(vehicle))
				score+=10			
			else:
				vehicle.vertical(speed)	
			if vehicle.y >350 and len(traffic) <number_of_traffic:
				traffic.append(Car(getRandomX(),getRandomY(),GREEN_CAR))
			col = collide(vehicle,car)
			if col == True:
				run = False
		if car.x < 50 or car.x>460:
			break

		background(WIN,stripes,speed,car,traffic,distance,score)



def replay_genome(config_path, genome_path="winner4.pkl"):
	# Load requried NEAT config
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	# Unpickle saved winner
	with open(genome_path, "rb") as f:
		genome = pickle.load(f)

	# Convert loaded genome into required data structure
	genomes = [(1, genome)]

	# Call game with only the loaded genome
	eval_genomes(genomes, config)

if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config-feedforward.txt')
	# run(config_path)
	replay_genome(config_path)