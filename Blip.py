import sys
from NeuralNetwork import NeuralNetwork
import random
import math
import numpy as np
from scipy.special import expit

screenSize = 1000
class Blip:
    forcedYPos = int(screenSize / 1.15)
    xVelocity = 10
    def __init__(self):
        self.brain = NeuralNetwork(3,7,2)
        self.xPos = random.randint(100, screenSize - 100)
        self.hitbox = []
        self.fitness = 0
        self.alive = True

    def move(self, decision): #controlls blip movment, called every frame
        if decision == 0: #left
            self.xPos = self.xPos - self.xVelocity
        elif decision == 1: #right
            self.xPos += self.xVelocity

    def think(self, focusBar): #Standardizes and sends all relevant information to brain. Changes position accordingly
        vision = np.array([(self.xPos / screenSize), (focusBar[0] / screenSize), (focusBar[1] / screenSize)]) #Standardize information (position, bar distance, and gap location)
        decision = self.brain.query(vision) #query network based on standardized data
        self.move(decision) #move based on query result

    def mutate(self, rate): #preps and sends for neural network mutation
        newBlip = Blip() #random new blip
        newBrain = self.brain.mutate(rate) #get mutated brain
        newBlip.brain = newBrain #apply new brain to newBlip
        return newBlip

    def updateHitbox(self): #controls the points on each blip that trigger collisions
        self.hitbox = []
        self.hitbox.append([(self.xPos + (50 / 2)), self.forcedYPos])
        self.hitbox.append([(self.xPos + (35.355 / 2)), (self.forcedYPos - (35.355 / 2))])
        self.hitbox.append([(self.xPos + 0), (self.forcedYPos - (50 / 2))])
        self.hitbox.append([(self.xPos - (35.355 / 2)), (self.forcedYPos - (35.355 / 2))])
        self.hitbox.append([(self.xPos -(50 / 2)), (self.forcedYPos + 0)])
        self.hitbox.append([(self.xPos -(35.355 / 2)), (self.forcedYPos + (35.355 / 2))])
        self.hitbox.append([(self.xPos + 0), (self.forcedYPos + (50 / 2))])
        self.hitbox.append([(self.xPos + (35.355 / 2)), (self.forcedYPos + (35.355 / 2))])
