import random
import numpy as np
import scipy.special

class NeuralNetwork:
    def __init__(self, inputnodes, hiddennodes, outputnodes):
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes
        self.wih = np.random.normal(0.0, pow(self.inodes, -0.5), (self.hnodes, self.inodes)) #create random weight matrix (hidden layer)
        self.who = np.random.normal(0.0, pow(self.hnodes, -0.5), (self.onodes, self.hnodes)) #create random weight matrix (output layer)
        self.sigmoidSquish = lambda x: scipy.special.expit(x) #declare activiation function (sigmoid squish) squishes every element in a n array

    def query(self, inputsList): #gets network results based on an input array
        inputs = np.array(inputsList, ndmin=2).T #convert inputs to a 2d array
        preSquishedHidden = np.dot(self.wih, inputs) #calculate hidden weights
        squishedHidden = self.sigmoidSquish(preSquishedHidden) #squish hidden weights
        preSquishedOutputs = np.dot(self.who, squishedHidden) #calculate final outputs
        squishedOutputs = self.sigmoidSquish(preSquishedOutputs) #sigmoid squish final outputs
        return np.argmax(squishedOutputs) #return the index of the greatest entry (left or right)

    def mutate(self, rate): #
        wihCopy = np.zeros(shape=(self.hnodes,self.inodes))
        whoCopy = np.zeros(shape=(self.onodes,self.hnodes))
        for x in range(len(self.wih)): #copy self.wih into a new matrix to be manipulated
            for y in range(len(self.wih[x])):
                wihCopy[x][y] = self.wih[x][y]
        for x in range(len(self.who)): #copy self.who into a new matrix to be manipulated
            for y in range(len(self.who[x])):
                whoCopy[x][y] = self.who[x][y]
        for x in range(len(self.wih)): #go through each weight and change some of them(based on the rate)
            for y in range(len(self.wih[x])):
                rand = random.randint(0,1000) / 1000
                if rand < rate: wihCopy[x][y] = np.random.normal(0,.1);
        for x in range(len(self.who)): #go through each weight and change some of them(based on the rate)
            for y in range(len(self.who[x])):
                rand = random.randint(0,100) / 100
                if rand < rate: whoCopy[x][y] = np.random.normal(0,.1);

        new = NeuralNetwork(self.inodes, self.hnodes, self.onodes) #new network to be returned
        new.wih = wihCopy #given mutated weights
        new.who = whoCopy #given mutated weights
        return new
