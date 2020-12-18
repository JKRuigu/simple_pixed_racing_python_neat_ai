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

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def getRandomX():
	return random.randrange(0, 500)

def getRandomY():
	return random.randrange(-20, 0)

def background(win,stripes,speed,cars,traffic,distance,score,gen,top,g_top):
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

	for car in cars:
		car.draw(win)

	for vehicle in traffic:
		vehicle.draw(win)		

	distances = font.render(f"Distance: {distance}", 1, (255,255,255))	
	scores = font.render(f"Score: {score}", 1, (255,255,255))
	score_label = font.render("Alive: " + str(len(cars)),1,(255,255,255))
	gen_label = font.render("GEN: " + str(gen-1),1,(255,255,255))
	gen_h_label = font.render(f"HIGHEST: {top}  {g_top}", 1, (255,255,255))
	WIN.blit(distances, (50, 0))
	WIN.blit(scores, (50, 20))
	win.blit(score_label, (50, 40))	
	win.blit(gen_label, (50, 60))			
	win.blit(gen_h_label, (50, 80))			

	pygame.display.update()


def eval_genomes(genomes, config):
	"""
	runs the simulation of the current population of
	cars and sets their fitness based on the distance they
	reach in the game.
	"""
	global WIN,gen,top,g_top
	win = WIN
	gen += 1

	# start by creating lists holding the genome itself, the
	# neural network associated with the genome and the
	# car object that uses that network to play
	nets = []
	cars = []
	ge = []
	for genome_id, genome in genomes:
		genome.fitness = 0  # start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		cars.append(Car(getRandomX(),400,BLUE_CAR))
		ge.append(genome)

	run = True
	FPS = 60
	distance = 0
	score = 0
	speed = 20
	number_of_traffic = 2
	clock = pygame.time.Clock()

	traffic = [Car(getRandomX(),getRandomY(),GREEN_CAR),Car(getRandomX(),getRandomY(),GREEN_CAR)]
	stripes = [Stripe(200,50,STRIPE),Stripe(200,200,STRIPE),Stripe(200,350,STRIPE)]

	while run and len(cars) > 0:
		clock.tick(FPS)
		distance+=1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		for x, car in enumerate(cars):  # give each car a fitness of 0.1 for each frame it stays alive
			ge[x].fitness += 0.1

		for vehicle in traffic:	
			# send car location, top pipe location and bottom pipe location and determine from network whether to jump or not
			for car in cars:
				output = nets[cars.index(car)].activate((car.x, abs(car.x - vehicle.x), abs(car.y - vehicle.y)))
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
				for genome in ge:
					genome.fitness += 5
			for car in cars:
				col = collide(vehicle,car)
				if col == True:
					ge[cars.index(car)].fitness -= 1
					nets.pop(cars.index(car))
					ge.pop(cars.index(car))
					cars.pop(cars.index(car))

		for car in cars:
			if car.x <95 or car.x >450:
				ge[cars.index(car)].fitness -= 1

			if car.x < 10 or car.x >460:
				nets.pop(cars.index(car))
				ge.pop(cars.index(car))
				cars.pop(cars.index(car))



		# break if score gets large enough
		if score > 500 or score > top:
			with open("best.pkl","wb") as f:
				pickle.dump(nets[0],open("best.pkl", "wb"))
				f.close()
		# if score > 500 or score > top:
				top = score
				g_top = gen

		background(WIN,stripes,speed,cars,traffic,distance,score,gen,top,g_top)


def run(config_file):
	"""
	runs the NEAT algorithm to train a neural network to play flappy car.
	:param config_file: location of config file
	:return: None
	"""
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#p.add_reporter(neat.Checkpointer(5))

	# Run for up to 50 generations.
	winner = p.run(eval_genomes, 30)

	with open("winner.pkl","wb") as f:
		pickle.dump(winner,f)
		f.close()

	# show final stats
	print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config-feedforward.txt')
	run(config_path)