import pygame, math, sys
from random import randint
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
    def __neg__(this):
        return Vector2(-this.x, -this.y)
    def __abs__(this):
        return Vector2(abs(this.x), abs(this.y))
    def magnitude(this):
        return math.sqrt(this.x**2 + this.y**2)
    def angle(this):
        return math.atan2(this.y, this.x)
    def get(this):
        return (this.x, this.y)
    def geti(this):
        return (int(this.x), int(this.y))

class Object:
    def __init__(this, position, velocity, size, friction): #size is (w,h)
        this.position = position # might be totally replaced by this.rect.center
        this.velocity = velocity
        this.rect = pygame.Rect((0,0), size)
        this.rect.center = this.position.get()
        this.friction = friction
    def update(this):
        #if round(this.velocity.y) == 0:
            #print this.position.y
        this.velocity += ACCEL
        this.position += this.velocity
        this.rect.center = this.position.get()
        if this.position.y + this.rect.height/2.0 >= sheight-1:
            this.velocity.x *= this.friction
            if this.velocity.y<0.5:
                this.position.y -= this.velocity.y
                this.velocity.y = 0
            else:
                this.position -= this.velocity

                this.velocity -= ACCEL
                newy = (this.velocity.y**2 + 2*ACCEL.y*((sheight-1)-(this.position.y+this.rect.height/2)))**0.5
                timeleft = 1 - ((newy - this.velocity.y)/ACCEL.y)
                newy *= -1
                newery = newy - ACCEL.y * timeleft
                this.velocity.y = newery
                this.position.y = (sheight-1) + (newery*timeleft - ACCEL.y*(timeleft**2)) - this.rect.height/2
                this.rect.center = this.position.get()
    def draw(this):
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)

class ObjectManager:
    def __init__(this):
        this.objects = {}
        this.nextindex = 1
    def update(this):
        for o in this.objects:
            this.objects[o].update()
    def draw(this):
        for o in this.objects:
            this.objects[o].draw()
    def add(this, obj):
        this.objects[this.nextindex] = obj
        this.nextindex += 1
    def click(this, pos):
        for o in this.objects:
            if this.objects[o].rect.collidepoint(pos):
                return o
        return False

class Textbox:
    def __init__(this, rect, contents):
        this.rect = rect
        this.textpos = (rect.left+2, rect.top+1)
        this.contents = contents
        this.on = False
        this.cursor = 0
        this.render()
    def assault(this, text):
        this.contents = this.contents[:cursor]+text+this.contents[cursor:]
        this.render()
    def backspace(this):
        if cursor:
            this.contents = this.contents[:cursor-1]+this.contents[cursor:]
            this.cursor -= 1
        this.render()
    def delete(this):
        if cursor != len(this.contents)-1:
            this.contents = this.contents[:cursor]+this.contents[cursor+1:]
        this.render()
    def update(this, contents):
        this.contents = contents
        this.render()
    def render(this):
        this.rendered = fonts["textbox"].render(this.contents, 1, (0,0,0))
    def draw(this):
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        screen.blit(this.rendered, this.textpos)
    

class Properter:
    def __init__(this):
        this.obj = False
        this.textbox = {}
        this.textbox["position.x"] = Textbox(pygame.Rect((30,100), (40,17)), "")
        this.textbox["position.y"] = Textbox(pygame.Rect((80,100), (40,17)), "")
        this.textbox["velocity.x"] = Textbox(pygame.Rect((30,120), (40,17)), "")
        this.textbox["velocity.y"] = Textbox(pygame.Rect((80,120), (40,17)), "")
        this.textboxon = False
    def focus(this, obj):
        this.obj = obj
        this.update()
    def updateTextBox(this, key):
        this.textbox[key].update(str(round(eval("this.obj."+key), 1)))
    def draw(this):
        for t in this.textbox:
            this.textbox[t].draw()
    def click(this, click):
        for t in this.textbox:
            if this.textbox[t].rect.collidepoint(click):
                this.textbox[t].on = True
                this.textboxon = t
    def keyit(this, event):
        if event.key == 8:
            this.textbox[textboxon].backspace()
        elif event.key == 127:
            this.textbox[textboxon].delete()
        else:
            this.textbox[textboxon].assault(inp)
    def update(this):
        for t in this.textbox:
            this.updateTextBox(t)


#Initializations
pygame.init()
pygame.display.set_icon(pygame.image.load("res/img/icon.ico"))
dimensions = swidth, sheight = 1024, 600
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()

fonts = {}
fonts["textbox"] = pygame.font.Font("res/font/Courier.ttf", 12)

FPS = 30

ACCEL = Vector2(0, 9.8/FPS)


objectmanager = ObjectManager()
objectmanager.add(Object(Vector2(25,100), Vector2(0.2,0), (25,25), 0.999))

#objectmanager.add(Object(Vector2(200,300), Vector2(1,-10), (25,25)))
#objectmanager.add(Object(Vector2(600,300), Vector2(-1,-10), (25,25)))

objectmanager.add(Object(Vector2(200,574), Vector2(10,0), (25,25), 0.9))
properter = Properter()

running = True
paused = False
focus = False
ticker = 0
screen.fill((255,255,255))
while running:
    ticker += 1
    #screen.fill((255,255,255))
    #update
    if paused:
        #pause update logic
        if focus:
            #focused paused
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if properter.textboxon:
                        properter.keyit(event)
                    elif event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
                            newfocus = objectmanager.click(event.pos)
                            if newfocus == focus:
                                focus = False
                            else:
                                focus = newfocus
                                if focus:
                                    properter.focus(objectmanager.objects[focus])
            #draw
            properter.draw()
        else:
            #unfocused paused
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        focus = objectmanager.click(event.pos)
                        if focus:
                            properter.focus(objectmanager.objects[focus])
    else:
        if focus:
            #focused unpaused
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if properter.textboxon:
                        properter.keyit(event)
                    elif event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
                            newfocus = objectmanager.click(event.pos)
                            if newfocus == focus:
                                focus = False
                            else:
                                focus = newfocus
                                if focus:
                                    properter.focus(objectmanager.objects[focus])
            properter.update()
            #draw
            properter.draw()
            objectmanager.update()
        else:
            #unpaused update logic
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        focus = objectmanager.click(event.pos)
                        if focus:
                            properter.focus(objectmanager.objects[focus])
            objectmanager.update()
    
    objectmanager.draw()
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
