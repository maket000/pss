import pygame, math
from pygame import *

class Vector2:
    def __init__(this, x=0.0, y=0.0):
        this.x = float(x)
        this.y = float(y)
    def __str__(this):
        return "%f,%f" % (this.x, this.y)
    def __add__(this, v2):
        return Vector2(this.x+v2.x, this.y+v2.y)
    def __iadd__(this, v2):
        this.x += v2.x
        this.y += v2.y
        return this
    def __sub__(this, v2):
        return Vector2(this.x-v2.x, this.y-v2.y)
    def __abs__(this):
        return Vector2(abs(this.x), abs(this.y))
    def magnitude(this):
        return math.sqrt(this.x**2 + this.y**2)
    def angle(this):
        return math.atan2(this.y, this.x)
    def getComp(this):
        return (this.x, this.y)
    def getiComp(this):
        return (int(this.x), int(this.y))

class Object:
    def __init__(this, position, velocity):
        this.position = position
        this.velocity = velocity
    def update(this):
        this.velocity += ACCEL
        this.position += this.velocity
    def draw(this):
        screen.set_at(this.position.getiComp(), (255,255,255))

class ObjectManager:
    def __init__(this):
        this.objects = {}
        this.nextindex = 0
    def update(this):
        for o in this.objects:
            this.objects[o].update()
    def draw(this):
        for o in this.objects:
            this.objects[o].draw()
    def add(this, obj):
        this.objects[this.nextindex] = obj
        this.nextindex += 1
        

#Initializations
pygame.init()
pygame.display.set_icon(pygame.image.load("img/icon.ico"))
dimensions = swidth, sheight = 1024, 600
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()

FPS = 30
PMSCALE = 10.0

ACCEL = Vector2(0, 9.8/FPS)


objectmanager = ObjectManager()
objectmanager.add( Object(Vector2(150,600), Vector2(4,-10)) )
objectmanager.add( Object(Vector2(140,600), Vector2(4,-11)) )
objectmanager.add( Object(Vector2(130,600), Vector2(4,-12)) )
objectmanager.add( Object(Vector2(120,600), Vector2(4,-13)) )
objectmanager.add( Object(Vector2(110,600), Vector2(4,-14)) )
objectmanager.add( Object(Vector2(100,600), Vector2(4,-15)) )

running = True
while running:
    #input
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    #update
    objectmanager.update()
    
    #draw
    screen.fill((0,0,0))
    objectmanager.draw()
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
