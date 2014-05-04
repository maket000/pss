import pygame
from pygame import *

import math, sys, copy, re
from random import randint

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
    def scalarMultiply(this, n):
        return Vector2(this.x*n, this.y*n)

class Object:
    def __init__(this, position, velocity, accel, size, mass, friction, spring): #Vector2, Vector2, Vector2, (int,int), float, float, float
        this.position = position
        this.velocity = velocity
        this.lastPosition = copy.copy(this.position)
        this.lastVelocity = copy.copy(this.velocity)
        this.accel = accel
        this.rect = pygame.Rect((0,0), size)
        this.rect.center = this.position.get()
        this.mass = mass
        this.friction = friction
        this.spring = spring
        this.collided = False #MAKE THIS TRUE IF COLLIDE
    def update(this):
        this.lastPosition = copy.copy(this.position)
        this.lastVelocity = copy.copy(this.velocity)
        this.velocity += this.accel
        this.position += this.velocity
        if this.position.y + this.rect.height/2.0 >= sHeight:
            this.position.y -= 2*((this.position.y+this.rect.height/2) - sHeight)
            this.velocity.y *= -this.spring
        if this.position.x + this.rect.width/2.0 >= sWidth:
            this.position.x -= 2*((this.position.x+this.rect.width/2) - sWidth)
            this.velocity.x *= -this.spring
        if this.position.x - this.rect.width/2.0 < 0:
            this.position.x -= 2*((this.position.x-this.rect.width/2))
            this.velocity.x *= -this.spring
        this.rect.center = this.position.get()
    def revert(this):
        this.position = copy.copy(this.lastPosition)
        this.velocity = copy.copy(this.lastVelocity)
    
    def draw(this, color=(0,0,0)):
        pygame.draw.rect(objectScreen, color, this.rect, 1)

    def getFunction(this, value):
        if value == "position.x":
            return "(("+str(this.accel.x)+"/2)*(x**2))+("+str(this.velocity.x)+"*x)+"+str(this.position.x)
        if value == "position.y":
            return "(("+str(this.accel.y)+"/2)*(x**2))+("+str(this.velocity.y)+"*x)+"+str(this.position.y)
        if value == "velocity.x":
            return str(this.velocity.x)+"+("+str(this.accel.x)+"*x)"
        if value == "velocity.y":
            return str(this.velocity.y)+"+("+str(this.accel.y)+"*x)"

class ObjectManager:
    def __init__(this):
        this.objects = []
        this.aliveObjects = []
        this.zoom = 1

    def collides(this, o1, o2):
        obj1 = this.objects[this.aliveObjects[o1]]
        obj2 = this.objects[this.aliveObjects[o2]]
        if obj1.rect.colliderect(obj2.rect):
            return True
        
        return False
    
    def update(this):
        for o in this.aliveObjects: #updates
            this.objects[o].update()
        
        collisions = []
        toRevert = []
        for o1 in range(len(this.aliveObjects)):
            for o2 in range(o1+1,len(this.aliveObjects)):
                if this.collides(o1,o2):
                    collisions.append([this.aliveObjects[o1],this.aliveObjects[o2]])
                    this.objects[this.aliveObjects[o1]].collided = True
                    this.objects[this.aliveObjects[o2]].collided = True
                    toRevert.append(o1)
                    toRevert.append(o2)
            
        toRevert = list(set(toRevert))
        for r in toRevert:
            this.objects[r].revert()

        RLcol = [[] for x in range(len(this.aliveObjects))]
        BTcol = [[] for x in range(len(this.aliveObjects))]
        #print collisions
        for o1,o2 in collisions:
            obj1 = this.objects[o1]
            obj2 = this.objects[o2]
            if obj1.velocity.x == obj2.velocity.x:
                RLt = None
                LRt = None
            else:
                RLt = (obj2.position.x - obj2.rect.width/2 - obj1.position.x - obj1.rect.width/2)/(obj1.velocity.x - obj2.velocity.x)
                LRt = (obj1.position.x - obj1.rect.width/2 - obj2.position.x - obj2.rect.width/2)/(obj2.velocity.x - obj1.velocity.x)
                        
            if obj1.velocity.y == obj2.velocity.y:
                BTt = None
                TBt = None
            else:
                BTt = (obj2.position.y - obj2.rect.height/2 - obj1.position.y - obj1.rect.height/2)/(obj1.velocity.y - obj2.velocity.y)
                TBt = (obj1.position.y - obj1.rect.height/2 - obj2.position.y - obj2.rect.height/2)/(obj2.velocity.y - obj1.velocity.y)
            if 0 <= RLt <= 1:
                obj1.position.x += obj1.velocity.x*RLt
                obj2.position.x = obj1.position.x + obj1.rect.width/2 + obj2.rect.width/2
                obj1.velocity.x, obj2.velocity.x = (obj1.velocity.x*(obj1.mass - obj2.mass) + 2*obj2.mass*obj2.velocity.x) / (obj1.mass + obj2.mass), (obj2.velocity.x*(obj2.mass - obj1.mass) + 2*obj1.mass*obj1.velocity.x) / (obj2.mass + obj1.mass)
                timeLeft = 1 - RLt
            elif 0 <= LRt <= 1:
                obj1.position.x += obj1.velocity.x*LRt
                obj2.position.x = obj1.position.x - (obj1.rect.width/2 + obj2.rect.width/2)
                obj1.velocity.x, obj2.velocity.x = (obj1.velocity.x*(obj1.mass - obj2.mass) + 2*obj2.mass*obj2.velocity.x) / (obj1.mass + obj2.mass), (obj2.velocity.x*(obj2.mass - obj1.mass) + 2*obj1.mass*obj1.velocity.x) / (obj2.mass + obj1.mass)
                timeLeft = 1 - LRt
            elif 0 <= BTt <= 1:
                obj1.position.y += obj1.velocity.x*BTt
                obj2.position.y = obj1.position.y + obj1.rect.height/2 + obj2.rect.width/2
                obj1.velocity.y, obj2.velocity.y = (obj1.velocity.y*(obj1.mass - obj2.mass) + 2*obj2.mass*obj2.velocity.y) / (obj1.mass + obj2.mass), (obj2.velocity.y*(obj2.mass - obj1.mass) + 2*obj1.mass*obj1.velocity.y) / (obj2.mass + obj1.mass)
                timeLeft = 1 - BTt
            elif 0 <= TBt <= 1:
                obj1.position.y += obj1.velocity.x*TBt
                obj2.position.y = obj1.position.y - (obj1.rect.height/2 + obj2.rect.width/2)
                obj1.velocity.y, obj2.velocity.y = (obj1.velocity.y*(obj1.mass - obj2.mass) + 2*obj2.mass*obj2.velocity.y) / (obj1.mass + obj2.mass), (obj2.velocity.y*(obj2.mass - obj1.mass) + 2*obj1.mass*obj1.velocity.y) / (obj2.mass + obj1.mass)
                timeLeft = 1 - TBt
            else:
                timeLeft = 1


            obj1.position += obj1.velocity.scalarMultiply(timeLeft)
            
            obj1.rect.center = obj1.position.get()
            obj2.rect.center = obj2.position.get()
                
        #print RLcol
        #print BTcol
                
            
            
            
    def draw(this):
        objectScreen.fill((255,255,255))
        for o in this.aliveObjects:
            if focus == o:
                this.objects[o].draw((255,0,0))
            else:
                this.objects[o].draw()
        if focus != -1:
            crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((464-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (464,600))
            screen.blit(crop,(0,0))
        else:
            screen.blit(objectScreen, (0,0))
    def add(this, obj):
        this.objects.append(obj)
        if this.aliveObjects:
            this.aliveObjects.append(this.aliveObjects[-1]+1)
        else:
            this.aliveObjects.append(0)
    def click(this, pos):
        if focus == -1:
            for i in this.aliveObjects:
                if this.objects[i].rect.collidepoint(pos):
                    return i
        return -1

class Tab:
    def __init__(this, rect, text):
        this.rect = rect
        textsize = fonts["textbox"].size(text)
        text = fonts["textbox"].render(text, 1, (0,0,0))
        textpos = ((rect.width-textsize[0])/2,(rect.height-textsize[1])/2)
        outrect = this.rect.copy()
        outrect.topleft = (0,0)
        this.visual = [pygame.Surface(this.rect.size),pygame.Surface(this.rect.size)]
        this.visual[0].fill((255,255,255))
        pygame.draw.rect(this.visual[0], (0,0,0), outrect, 1)
        this.visual[0].blit(text, textpos)
        this.visual[1].fill((255,200,200))
        pygame.draw.rect(this.visual[1], (0,0,0), outrect, 1)
        this.visual[1].blit(text, textpos)
        
    def click(this, point):
        return this.rect.collidepoint(point)
    def draw(this, on):
        screen.blit(this.visual[on], this.rect.topleft)
        

class Textbox:
    def __init__(this, rect, contents):
        this.rect = rect
        this.textpos = (rect.left+3, rect.top+2)
        this.contents = contents
        this.on = False
        this.cursor = 0
        this.altered = False
        this.render()
    def turnOn(this):
        this.on = True
        this.cursor = 0
        this.altered = False
    def turnOff(this):
        this.on = False
        return this.altered
    def assault(this, text):
        if text in numChars:
            this.contents = this.contents[:this.cursor]+text+this.contents[this.cursor:]
            this.cursor += 1
            this.altered = True
            this.render()
    def backspace(this):
        if this.cursor:
            this.contents = this.contents[:this.cursor-1]+this.contents[this.cursor:]
            this.cursor -= 1
            this.altered = True
            this.render()
    def delete(this):
        if this.cursor != len(this.contents):
            this.contents = this.contents[:this.cursor]+this.contents[this.cursor+1:]
            this.altered = True
            this.render()
    def cursorMove(this, forward):
        if forward and this.cursor != len(this.contents):
            this.cursor += 1
        elif not(forward) and this.cursor != 0:
            this.cursor -= 1
    def update(this, contents):
        this.contents = contents
        this.render()
    def render(this):
        this.rendered = fonts["textbox"].render(this.contents, 1, (0,0,0))
    def draw(this):
        if this.on:
            pygame.draw.rect(screen, (222,222,222), this.rect, 0)
            cursorXpos = fonts["textbox"].size(this.contents[:this.cursor])[0]+this.rect.left+2
            if ((ticker%30)/15) and paused:
                pygame.draw.line(screen, (0,0,0), (cursorXpos, this.rect.top+2), (cursorXpos, this.rect.bottom-4), 1)
            
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        screen.blit(this.rendered, this.textpos)


##class Graph: old, predictive
##    def __init__(this, rect, yScale): #domain is a tuple (l,h) where l<=x<h
##        this.rect = rect
##        this.yScale = yScale
##    
##    def refunc(this, newfunc, domain, offset):
##        this.fx = []
##        this.xScale = float((domain[1]-domain[0]))/(this.rect.width-2)
##        this.yScale = float(this.rect.height)/sHeight
##        this.offset = offset
##        this.func = newfunc
##        this.steps = 0
##        for rx in range(1,this.rect.width-1):
##            x = rx*this.xScale
##            this.fx.append(this.rect.top+int(this.yScale*eval(newfunc)))
##
##    def step(this):
##        for _ in range(int(1.0/this.xScale)):
##            this.fx.pop(0)
##            x = this.xScale*(this.steps + this.rect.width-2)
##            this.fx.append(this.rect.top+int(this.yScale*eval(this.func)))
##            this.steps += 1
##        
##    def draw(this):
##        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
##        for rx in range(this.rect.width-3):
##            pygame.draw.line(screen,(0,0,0),(rx+this.rect.left,this.fx[rx]),(rx+this.rect.left+1,this.fx[rx+1]),1)
##        pygame.draw.line(screen, (255,0,0), (0,this.fx[0]), (1023,this.fx[0]), 1)


class Graph:
    def __init__(this, rect):
        this.rect = rect
        this.data = []
    def clear(this):
        this.data = []
    def add(this, data):
        this.data.append(data)
    def draw(this):
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        offset = len(this.data)-this.rect.width
        if offset < 0:
            offset = 0
        for x in range(len(this.data)-this.rect.width, len(this.data)-2):
            if x>=0:
                pygame.draw.line(screen,(0,0,0),(x+this.rect.left - offset,this.rect.bottom - this.data[x]),(x+this.rect.left+1 - offset,this.rect.bottom - this.data[x+1]),1)
        pygame.draw.line(screen, (255,0,0), (0,this.data[-1]), (1023,this.data[-1]), 1)

class Slider:
    def __init__(this, low, high, start, interval, rect):
        this.low = low
        this.high = high
        this.current = start
        this.interval = interval
        this.rect = rect
        ticks = int((high - low)/interval)
        twid = rect.width / ticks
        this.notches = []
        this.values = []
        for x in range(ticks+1):
            this.notches.append((this.rect.left + x * twid, this.rect.centery))
            this.values.append(low + x*interval)

        this.slider = pygame.Rect(0,0,5,30)
        this.updateSlider()
    def click(this, pos):
        if this.slider.collidepoint(pos):
            global clickRelease
            clickRelease = 1
            return True
        if this.rect.collidepoint(pos):
            this.moveSlider(pos)
            return True
        return False

    def moveSlider(this, pos):
        if pos[0] > this.rect.right:
            this.current = len(this.values) - 1
        elif pos[0] < this.rect.left:
            this.current = 0
        else:
            for x in range(len(this.notches)-1):
                if pos[0] == this.notches[x][0]:
                    this.current = x
                    break
                elif this.notches[x][0] < pos[0] < this.notches[x+1][0]:
                    if pos[0] - this.notches[x][0] <= this.notches[x+1][0] - pos[0]:
                        this.current = x
                    else:
                        this.current = x+1
                    break
        this.updateSlider()
            
    
    def draw(this):
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        pygame.draw.rect(screen, (100,0,0), this.slider, 2)
        
    def updateSlider(this):
        this.slider.center = this.notches[this.current]
    def getValue(this):
        return this.values[this.current]
        

class Properter:
    def __init__(this):
        this.obj = False
        this.textbox = {}
        this.textbox["position.x"] = Textbox(pygame.Rect((30,100), (40,17)), "")
        this.textbox["position.y"] = Textbox(pygame.Rect((80,100), (40,17)), "")
        this.textbox["velocity.x"] = Textbox(pygame.Rect((30,120), (40,17)), "")
        this.textbox["velocity.y"] = Textbox(pygame.Rect((80,120), (40,17)), "")


        graphRect = pygame.Rect(464, 40, 560, 560)
        this.graph = {}
        this.graph["position.x"] = Graph(graphRect)
        this.graph["position.y"] = Graph(graphRect)
        this.graph["velocity.x"] = Graph(graphRect)
        this.graph["velocity.y"] = Graph(graphRect)

        this.tab = {}
        this.tab["position.x"] = Tab(pygame.Rect(464, 9, 125, 30), "x position")
        this.tab["position.y"] = Tab(pygame.Rect(590, 9, 125, 30), "y position")
        this.tab["velocity.x"] = Tab(pygame.Rect(716, 9, 125, 30), "x velocity")
        this.tab["velocity.y"] = Tab(pygame.Rect(842, 9, 125, 30), "y velocity")

        this.zoomSlider = Slider(1, 4, 2, 0.5, pygame.Rect(10, 10, 80, 20))
        
        this.textboxon = False
        
    def focus(this, obj):
        this.updateC()
        this.obj = obj
        this.clearGraphs()
        this.update()
        
    def updateTextBoxes(this):
        for t in this.textbox:
            this.textbox[t].update(str(round(eval("this.obj."+t), 1)))

    def updateGraphs(this):
        for g in this.graph:
            rawData = eval("this.obj."+g)
            if g == "position.x":
                this.graph[g].add(rawData*0.546875)
            elif g == "position.y":
                this.graph[g].add((sHeight-rawData)*(14.0/15.0))
            elif g == "velocity.x":
                this.graph[g].add((rawData+30)*(56.0/6.0))
            elif g == "velocity.y":
                this.graph[g].add((rawData+30)*(56.0/6.0))

    def clearGraphs(this):
        for g in this.graph:
            this.graph[g].clear()

    def draw(this):
        for t in this.textbox:
            this.textbox[t].draw()
            if t == this.textboxon:
                this.tab[t].draw(True)
            else:
                this.tab[t].draw(False)
        if this.textboxon:
            this.graph[this.textboxon].draw()
        this.zoomSlider.draw()

    def closeTextBox(this):
        if re.match(numregex, this.textbox[this.textboxon].contents) and this.textbox[this.textboxon].altered:
            exec("this.obj."+this.textboxon+" = "+this.textbox[this.textboxon].contents)
        else:
            this.updateTextBoxes()
    
    def click(this, click):
        slid = this.zoomSlider.click(click)
        if slid:
            this.updateC()
            return True
        for t in this.textbox:
            if this.textbox[t].rect.collidepoint(click):
                if this.textboxon:
                    this.closeTextBox()
                    this.textbox[this.textboxon].turnOff()
                this.textbox[t].turnOn()
                this.textboxon = t
                return True
            if this.tab[t].click(click):
                for off in this.tab:
                    if off != t:
                        this.tab[off].on = False
                if this.textboxon:
                    this.closeTextBox()
                    this.textbox[this.textboxon].turnOff()
                this.textbox[t].turnOn()
                this.textboxon = t
                return True
        if this.textboxon:
            this.closeTextBox()
        return False
    
    def keyit(this, event):
        if event.key == 8 and paused:
            this.textbox[this.textboxon].backspace()
        elif event.key == 127 and paused:
            this.textbox[this.textboxon].delete()
        elif event.key == 13 and paused:
            this.closeTextBox()
            this.textbox[this.textboxon].turnOff()
            this.textboxon = False
        elif event.key == 275 and paused:
            this.textbox[this.textboxon].cursorMove(True)
        elif event.key == 276 and paused:
            this.textbox[this.textboxon].cursorMove(False)
        elif paused:
            this.textbox[this.textboxon].assault(event.unicode)
        return False
        
    def update(this):
        this.updateTextBoxes()
        this.updateGraphs()
    
    def updateC(this):
        objectmanager.zoom = this.zoomSlider.getValue()




#Initializations
pygame.init()
pygame.display.set_icon(pygame.image.load("res/img/icon.ico"))
dimensions = sWidth, sHeight = 1024, 600
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()

objectScreen = pygame.Surface(dimensions)

numregex = "[-+]?[0-9]*\.?[0-9]+$"
numChars = ["-",".","0","1","2","3","4","5","6","7","8","9"]

fonts = {}
fonts["textbox"] = pygame.font.Font("res/font/Courier.ttf", 12)

FPS = 30

ACCEL = Vector2(0, 9.8/FPS)

objectmanager = ObjectManager()

for x in range(100):
    objectmanager.add(Object(Vector2(randint(100,900), randint(100,500)), Vector2(randint(-10,10), randint(-10,10)), ACCEL, (5, 5), randint(1,10), 1.0, 1.0))
##for x in range(1,150):
##    objectmanager.add(Object(Vector2(x*6, 100 + x*2), Vector2(1,0), ACCEL, (5,5), 1.0, 1.0, 1.0))
                  

properter = Properter()

running = True
paused = False
focus = -1
ticker = 0
screen.fill((255,255,255))

clickRelease = 0#0 : unset
                #1 : properter.zoomSlider.move(pos)

while running:
    if ticker%30==0:
        print ticker/30
    ticker += 1
    screen.fill((255,255,255))
    #update
    if paused:
        #pause update logic
        if focus != -1:
            #focused paused
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_p:
                        paused = not paused
                    if properter.textboxon:
                        properter.keyit(event)
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
                            newfocus = objectmanager.click(event.pos)
                            if newfocus == focus:
                                focus = -1
                            else:
                                focus = newfocus
                                if focus != -1:
                                    properter.focus(objectmanager.objects[focus])
                elif event.type == MOUSEBUTTONUP:
                    clickRelease = 0
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
                        if focus != -1:
                            properter.focus(objectmanager.objects[focus])
    else:
        if focus != -1:
            #focused unpaused
            #input
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if properter.textboxon:
                        properter.keyit(event)
                    if event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
                            newfocus = objectmanager.click(event.pos)
                            if newfocus == focus:
                                focus = -1
                            else:
                                focus = newfocus
                                if focus != -1:
                                    properter.focus(objectmanager.objects[focus])
                elif event.type == MOUSEBUTTONUP:
                    clickRelease = 0
            
            objectmanager.update()
            properter.update()
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
                        if focus != -1:
                            properter.focus(objectmanager.objects[focus])
            objectmanager.update()
            
    if clickRelease:
        if clickRelease == 1:
            properter.zoomSlider.moveSlider(pygame.mouse.get_pos())
            properter.updateC()

    
    objectmanager.draw()
    if focus != -1:
        properter.draw()
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
