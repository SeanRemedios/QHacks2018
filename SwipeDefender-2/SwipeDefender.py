import random
import pygame
import sys
import re
from pygame import *
from spritesheet import spritesheet

pygame.init()
fps = pygame.time.Clock()

WHITE = (255, 255, 255)
ORANGE = (255,140,0)
GREEN = (47, 129, 54)
BLACK = (0, 0, 0)

WIDTH = 1400
HEIGHT = 850
gameRunning = False

enemies = []
enemiesWaitFrames = 200

xDiff = 1400/1300
yDiff = 850/725

dataHandPoint = (-50,-50)

score = 0
castleHealth = 100
#castle src=https://opengameart.org/content/lpc-castle
castle = pygame.image.load("castle_take2_edited.png")
#trees src=https://opengameart.org/content/lpc-tree-recolors
trees = pygame.image.load("castle_path_edited.png")
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Swipe Defender')
#"Adventure Meme" Kevin MacLeod [Licensed under Creative Commons: By Attribution 3.0]
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()
pygame.mixer.init()
#pygame.mixer.music.load('AdventureMeme-MacLeod.mp3')
#pygame.mixer.music.play(-1)

#Intruder src=https://jesse-m.itch.io/jungle-pack
intruderSprites = spritesheet('intruder.png')
# Sprite is 40x69 pixels...
intruderImages = intruderSprites.images_at(((0, 0, 40, 69),(40, 0, 40,69),(80, 0, 40, 69),(120, 0, 40, 69),
(160, 00, 40, 69),(0, 69, 40, 69),(40, 0, 40, 69),(80, 0, 40, 69)), colorkey=BLACK)

dataFromOpenCV = (0, 0, 0, 0)

class intruder:
    damage = 20
    posX = -35
    posY = WIDTH/4 + 20
    width = 40
    height = 69
    frameCount = 0

    def __init__(self):
        self.speedX = 1 + score/10000
        self.speedY = random.uniform(-0.1, +0.1)
    def onLoadFinished(self, result):
        return
    def move(self):
        #add if before castle
        if (self.posX > WIDTH-130):
            if (self.posY > 250):
                self.posY = self.posY - 1
            else:
                global castleHealth
                castleHealth -= 20
                self.posX = -250
            return
        else:
            self.posX = self.posX + self.speedX
            self.posY = self.posY + self.speedY
        #else do damage (when at castle wall)

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

def displayScore(canvas):
    largeText = pygame.font.Font('freesansbold.ttf',20)
    TextSurf, TextRect = text_objects("Score: " + str(score), largeText)
    TextRect.left = 20
    TextRect.top = 20
    canvas.blit(TextSurf, TextRect)



def init():
    enemies.append(intruder())
    draw(window)
    pygame.display.update()

def draw(canvas):
    global enemiesWaitFrames, score
    score += 1
    canvas.fill(GREEN)

    #display score
    displayScore(canvas)
    
    #add castle + trees to cavas
    canvas.blit(castle, (WIDTH-400,0,400,HEIGHT))
    canvas.blit(trees, (0,0,WIDTH-400,HEIGHT))

    # move current enemies
    for e in enemies:
        if (abs(dataHandPoint[0] - e.posX) < 100 and abs(dataHandPoint[1] - e.posY) < 100):
        #if (abs(dataFromOpenCV[1] - 20 - e.posX) < 100 and abs(dataFromOpenCV[2] - 35 - e.posY) < 100):
            enemies.remove(e)
            print('Positions:')
            print(dataFromOpenCV[1] - 20, dataFromOpenCV[2] - 35)
            print(e.posX, e.posY)

        if (e.posX > WIDTH + 100 or e.posX < -100):
            enemies.remove(e)
        else:
            e.move()
            canvas.blit(intruderImages[int(e.frameCount)%8], (e.posX, e.posY, e.width, e.height))
            e.frameCount += 0.2

    pygame.draw.circle(canvas, ORANGE, [round(dataHandPoint[0]), round(dataHandPoint[1])], 10, 3)

    # potentially add new enemies
    rand = random.uniform(0, 100)
    enemiesWaitFrames -= 1
    if (rand > 70 and enemiesWaitFrames <= 0):
        enemiesWaitFrames = 200
        enemies.append(intruder())

def keydown(event):
    return
def keyup(event):
    if (event.key == K_SPACE):
        global gameRunning
        gameRunning = not gameRunning
    return
init()

def swipeDefender():
    while True:

        fileReHand=open("hand.txt", "r")
        if fileReHand.mode == 'r':
            contentsHand =fileReHand.read()
        fileReHand.close()

        splitHand = contentsHand.replace("(","")
        splitHand2 = splitHand.replace(")",", ")
        splitHand3 = splitHand2.strip(", ")
        splitHand4 = splitHand3.split(",")

        dataHand = (abs(WIDTH - int(splitHand4[-2])*xDiff), int(splitHand4[-1])*yDiff)
        global dataHandPoint
        dataHandPoint = dataHand

        fileRe=open("switch.txt", "r")

        if fileRe.mode == 'r':
            contents =fileRe.read()
            #if contents != '':
                #print (contents)

        fileRe.close()

        splitPoint = contents.replace("[","")
        splitPoint2 = splitPoint.replace("]]",", ")
        splitPoint3 = splitPoint2.replace("]","")
        splitPoint4 = splitPoint3.strip(", ")

        splitPoint4 = splitPoint4.split(",")
        data = (abs(WIDTH - int(splitPoint4[-4])*xDiff), int(splitPoint4[-3])*yDiff, abs(WIDTH - int(splitPoint4[-2])*xDiff), int(splitPoint4[-1])*yDiff )
        global dataFromOpenCV
        dataFromOpenCV = data



        

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keydown(event)
            elif event.type == KEYUP:
                keyup(event)
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

        if (gameRunning and castleHealth > 0):
            draw(window)

            pygame.display.update()
            fps.tick(60)


swipeDefender()
#threading.Thread(target=swipeDefender).start()
#threading.Thread(target=HandDetection.handMovement).start()