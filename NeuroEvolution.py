from Blip import Blip
import pygame as pg, random, time, pickle

pg.init() #initialize pygame
screenSize = 1000
screen = pg.display.set_mode((screenSize, screenSize)) #set screensize
pg.display.set_caption('NeuroEvolution Example')

class NeuroEvolution:
    #dynamic variables:
    activeBlips = [] #array of population's active blips blips
    deadBlips = [] #array of population's dead blips
    bars = [] #array of the bars. Each element is another array of positions[yPos, length of left side]
    focusBar = [] #bar that the blips are refrencing
    barTimer = 100 #controlls how often bars are added (don't touch, not dynamic)
    barCounter = 0 #stores how many bars have been created (for UI information)
    bestBlip = Blip() #stores the blip with the highest fitness (updated in showInterface() when the 'Save Best' button is activated)
    generationNumber = 0 #stores the current genNumber (for UI information and is used in checkGeneration())
    sliderX = 700 #stores the position of the slider wheel (in the UI) this position controlls framerate in showInterface()
    #settings variables:
    popSize = 200 #the number of blips per generation
    mutationRate = .1 #the percent of weights that are changed when mutating (in checkGeneration())
    barGapLength = 150 #length of gap between bars (used in barEngine())
    barVelocity = 5 #speed of the bars (used in barEngine())
    frameRate = 60 #controlls framerate and is updated in showInterface()

    def __init__(self):
        clock = pg.time.Clock() #for framerate
        self.complete = False #controlls game loop
        self.paused = False #controlls pause and unpause loops
        while not self.complete:
            for event in pg.event.get(): #check key presses and x button
                if event.type == pg.QUIT:
                    self.complete = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if self.paused: self.paused = False
                        elif not self.paused: self.paused = True
            clock.tick(self.frameRate) #for framerate
            screen.fill((255,255,255))
            if not self.paused: #these processes happen if the game is not paused
                self.checkGeneration() #handles selection of new generation when it's time
                self.barEngine() #handles all bar operations
                self.blipEngine() #handles all blip operations
            if self.paused: #the interface is only shown if the game is paused
                self.interfaceEngine() #shows text relays, buttons, and the speed slider
            pg.display.update()
        pg.quit()

    def checkGeneration(self): #controlls adding new, more optomized generations
        if self.generationNumber == 0: #at the beginning of the game, add some random blips
            for i in range(self.popSize):
                b = Blip()
                self.activeBlips.append(b)
            self.generationNumber += 1
        else: #when the entire generation is dead, create a new, more optomized one
            if len(self.activeBlips) == 0:
                self.nextGeneration()

    def nextGeneration(self):
        self.activeBlips = []
        self.bars = []
        self.barTimer = 100
        #normalize the fitness of each blip(turns each fitness value into a probability that its blip will be picked)
        sum = 0
        for blip in self.deadBlips: sum += (blip.fitness ** 2) #find the sum of all fitness values. they are squared to have higher fitness values be selected more often
        for blip in self.deadBlips: blip.fitness = ((blip.fitness ** 2) / sum) #change fitness values to normalized values. they are squared to have higher fitness values be selected more often
        #pick a blip based on its fitness(probability)
        for blip in self.deadBlips:
            index = 0
            rand = random.randint(0, 99) / 100
            while (rand > 0):
                rand = rand - self.deadBlips[index].fitness
                index += 1
            index -= 1
            selection = self.deadBlips[index]
            child = selection.mutate(self.mutationRate)
            child.xPos = random.randint(100, screenSize - 100) #give each blip a random starting location
            self.activeBlips.append(child)
        self.deadBlips = []
        self.barCounter = 0
        self.generationNumber += 1

    def barEngine(self): #controlls bar position, timing, adding, and removing
        for bar in self.bars:
            pg.draw.rect(screen, (50,50,50), [0, bar[0], bar[1], 50]) #draw left-bar
            pg.draw.rect(screen, (50,50,50), [(bar[1] + self.barGapLength), bar[0], (screenSize - (bar[1] + self.barGapLength)), 50]) #draw right-bar
            bar[0] += self.barVelocity #update position of bar
            if bar[0] >= screenSize: #delete bar once it passes
                self.bars.pop(0)
        if self.barTimer >= 100: #add bars every 100 frames
            rand = random.randint(0, (screenSize - self.barGapLength))
            self.bars.append([0,rand])
            self.barTimer = 1
            self.barCounter += 1
        self.barTimer += 1

    def blipEngine(self): # draws blips and handles collision detection
        #update the bar that the blips are refrencing for collision detection
        if self.bars[0][0] > (Blip.forcedYPos + 25):
            self.focusBar = self.bars[1]
        else:
            self.focusBar = self.bars[0]
        fBarSize, fBarY = self.focusBar[0], self.focusBar[1] #refrence focus bar
        # Draw blips on screen and do collision detection
        for blip in self.activeBlips:
            if blip.alive:#
                pg.draw.circle(screen, (250,0,0), (int(blip.xPos), Blip.forcedYPos), 25)  #draw blips
                blip.fitness += 1 #each frame the bird is alive, its fitness goes up
                blip.think(self.focusBar) #querys neural network for a decision
                # Collision detection
                blip.updateHitbox() #updates the points on each blip that are checked for collisions
                for coordinate in blip.hitbox:
                    xVal, yVal = coordinate[0], coordinate[1]
                    if (xVal < fBarY) and (yVal < fBarSize + 50): #check left-bar
                        if blip.alive:
                            self.deadBlips.append(blip)
                            blip.alive = False
                            self.activeBlips.remove(blip)
                    elif (xVal > fBarY + self.barGapLength) and (yVal < fBarSize + 50): #check right-bar
                        if blip.alive:
                            self.deadBlips.append(blip)
                            blip.alive = False
                            self.activeBlips.remove(blip)
                    elif (xVal <= 0) or (xVal >= screenSize): #check out of bounds
                        if blip.alive:
                            blip.fitness = 0.00000000000000000000001 #if blip goes out of bounds it gets a fitness of essentially zero
                            self.deadBlips.append(blip)
                            blip.alive = False
                            self.activeBlips.remove(blip)

    #User Interface Functions:
    def interfaceEngine(self): #shows UI (buttons, slider, and text relays) when paused
        # Text Relays
        self.relayText(20,20,50,(150,150,150),"Generation: ")
        self.relayText(340,20,50,(150,150,150),str(self.generationNumber))
        self.relayText(20,70,50,(150,150,150),"Blips Remaining: ")
        self.relayText(460,70,50,(150,150,150),str(len(self.activeBlips)))
        self.relayText(20,120,50,(150,150,150),"Bars Made: ")
        self.relayText(320,120,50,(150,150,150),str(self.barCounter))
        self.relayText(140,350,200,(255,50,50),"Paused")
        # Slider (slider circle is drawn below)
        self.relayText(785,50,25,(150,150,150), "Speed")
        pg.draw.rect(screen,(150, 150, 150), [700, 90, 250, 5])
        mPos = pg.mouse.get_pos()
        mClick = pg.mouse.get_pressed()
        if self.sliderX + 10 > mPos[0] > self.sliderX - 10 and 100 > mPos[1] > 80: #if mouse is on the slider wheel, hilight the circle
            pg.draw.circle(screen,(200,200,200), (self.sliderX,93), 10)
            if mClick[0] == 1 and 950 >= mPos[0] >= 700: #if mouse clicks slider wheel, change the wheel position within a certain threshold depending on mouse position
                self.sliderX = mPos[0]
                self.frameRate = (self.sliderX - 690) ** 2 #update framerate depending on slider wheel location
        else: pg.draw.circle(screen,(150,150,150), (self.sliderX,93), 10)
        # Button Relays
        self.relayButton(50,920,150,50,(150,150,150), (200,200,200), (0,0,0), 25, "Restart")
        self.relayButton(300,920,150,50,(150,150,150), (200,200,200), (0,0,0), 25,"Next Gen")
        self.relayButton(550,920,150,50,(150,150,150), (200,200,200), (0,0,0), 25, "Save Best")
        self.relayButton(800,920,150,50,(150,150,150), (200,200,200), (0,0,0), 25, "Load Best")
        # button actions:
        if 970 > mPos[1] > 920: #All buttons have same y-coords so this checks the threshold for all
            if 200 > mPos[0] > 50 and mClick[0] == 1: #Restart: restart with a new population at generation 1
                self.generationNumber = 0
                self.activeBlips = []
                self.deadBlips = []
                self.bars = []
                self.barCounter = 0
                self.barTimer = 100
                self.bestBlip = Blip()
                time.sleep(.2) #prohibits button holding
            if 450 > mPos[0] > 300 and mClick[0] == 1: #Next Gen: kill all active blips, forcing the simulation to the next generation
                self.nextGeneration()
                time.sleep(.2) #prohibits button holding
            if 700 > mPos[0] > 550 and mClick[0] == 1: #Save Best: saves the weights for the best blip brain(neural network)
                for i in range(len(self.deadBlips)): #check dead blips for best fitness
                    if self.deadBlips[i].fitness > self.bestBlip.fitness: self.bestBlip = self.deadBlips[i]
                for i in range(len(self.activeBlips)): #check dead blips for best fitness
                    if self.activeBlips[i].fitness > self.bestBlip.fitness: self.bestBlip = self.activeBlips[i]
                # with open("/home/marc/Development/Python/NeuroEvolution/bestBlipWIH.pickle", "wb") as storage:
                with open("bestBlipWIH.pickle", "wb") as storage:
                    pickle.dump(self.bestBlip.brain.wih, storage)
                    storage.close()
                # with open("/home/marc/Development/Python/NeuroEvolution/bestBlipWHO.pickle", "wb") as storage:
                with open("bestBlipWHO.pickle", "wb") as storage:
                    pickle.dump(self.bestBlip.brain.who, storage)
                    storage.close()
                time.sleep(.2) #prohibits button holding
            if 950 > mPos[0] > 800 and mClick[0] == 1: #Load Best: load saved weights from the best blip brain(neural network)
                self.generationNumber = "BEST"
                self.activeBlips = []
                self.deadBlips = []
                self.bars = []
                self.barCounter = 0
                self.barTimer = 100
                # storageWIH = open("/home/marc/Development/Python/NeuroEvolution/bestBlipWIH.pickle", "rb")
                storageWIH = open("bestBlipWIH.pickle", "rb")
                self.bestBlip.brain.wih = pickle.load(storageWIH)
                storageWIH.close()
                # storageWHO = open("/home/marc/Development/Python/NeuroEvolution/bestBlipWHO.pickle", "rb")
                storageWHO = open("bestBlipWHO.pickle", "rb")
                self.bestBlip.brain.who = pickle.load(storageWHO)
                storageWHO.close()
                self.activeBlips.append(self.bestBlip)
                time.sleep(.2) #prohibits button holding

    def relayText(self, x, y, fontSize, color, message): #Renders text
        font = pg.font.Font("freesansbold.ttf", fontSize)
        text = font.render(message, True, color)
        screen.blit(text, (x, y))

    #todo: MAYBE create a button object so button functions don't need to look so cumbersome (functions are currently in interfaceEngine())
    def relayButton(self, x, y, length, height, inactiveColor, activeColor, textColor, fontSize, message): #Renders buttons
        mousePos = pg.mouse.get_pos()
        if x+length > mousePos[0] > x and y+height > mousePos[1] > y: pg.draw.rect(screen, activeColor, [x, y, length, height])
        else: pg.draw.rect(screen, inactiveColor, [x, y, length, height])
        font = pg.font.Font("freesansbold.ttf", fontSize)
        text = font.render(message, True, textColor)
        textRect = text.get_rect(center=((x+(length/2)), (y+(height/2))))
        screen.blit(text, textRect)

NeuroEvolution()
