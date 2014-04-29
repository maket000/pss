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
        if this.position.y + this.rect.height/2.0 >= sHeight-1: ###############################breaks at low velocities, maybe just put a floor made of an object, more versatile in the end 
            this.collided = True
            this.velocity.x *= this.friction
            this.position.y -= this.velocity.y
            try:
                this.velocity -= this.accel
                newy = (this.velocity.y**2 + 2*this.accel.y*((sHeight-1)-(this.position.y+this.rect.height/2)))**0.5
                timeLeft = 1 - ((newy - this.velocity.y)/this.accel.y)
                newy *= -this.spring
                newery = newy + this.accel.y * (timeLeft)
                this.velocity.y = newery - this.accel.y
                this.position.y = (sHeight-1) + ((newy*timeLeft + this.accel.y*(timeLeft**2))) - this.rect.height/2
            except:
                this.velocity.y = 0
        this.rect.center = this.position.get()
    def revert(this):
        this.position = copy.copy(this.lastPosition)
        this.velocity = copy.copy(this.lastVelocity)
    
    def draw(this):
        pygame.draw.rect(objectScreen, (0,0,0), this.rect, 1)

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
##        for o1,o2 in collisions:
##            obj1 = this.objects[o1]
##            obj2 = this.objects[o2]
##            if obj1.accel.x == 0:
##                if obj2.accel.x == 0:
##                    if obj1.velocity.x == obj2.velocity.x:
##                        RLt = None
##                        LRt = None
##                    else:
##                        RLt = (obj2.position.x - obj2.rect.width/2 - obj1.position.x - obj1.rect.width/2)/(obj1.velocity.x - obj2.velocity.x)
##                        LRt = (obj1.position.x - obj1.rect.width/2 - obj2.position.x - obj2.rect.width/2)/(obj2.velocity.x - obj1.velocity.x)
##                else:
##                    RLa = obj2.accel.x/2
##                    RLb = obj2.velocity.x - obj1.velocity.x
##                    RLc = obj2.position.x - obj2.rect.width/2 - obj1.position.x - obj1.rect.width/2
##                    RLd = (RLb**2) - (4*RLa*RLc)
##                    if RLd >= 0:
##                        RLt = min(x for x in [(-RLb+math.sqrt(RLd))/(2*RLa),(-RLb-math.sqrt(RLd))/(2*RLa)] if x >= 0)
##                    LRa = RLa
##                    LRb = obj2.velocity.x - obj1.velocity.x
##                    LRc = obj2.position.x + obj2.rect.width/2 - obj1.position.x + obj1.rect.width/2
##                    LRd = (LRb**2) - (4*LRa*LRc)
##                    if LRd >= 0:
##                        LRt = min(x for x in [(-LRb+math.sqrt(LRd))/(2*LRa),(-LRb-math.sqrt(LRd))/(2*LRa)] if x >= 0)
##            else:
##                if obj2.accel.x == 0:
##                    RLa = obj1.accel.x/2
##                    RLb = obj1.velocity.x - obj2.velocity.x
##                    RLc = obj1.position.x + obj1.rect.width/2 - obj2.position.x + obj2.rect.width/2
##                    RLd = (RLb**2) - (4*RLa*RLc)
##                    if RLd >= 0:
##                        RLt = min(x for x in [(-RLb+math.sqrt(RLd))/(2*RLa),(-RLb-math.sqrt(RLd))/(2*RLa)] if x >= 0)
##                    LRa = RLa
##                    LRb = obj1.velocity.x - obj2.velocity.x
##                    LRc = obj1.position.x - obj1.rect.width/2 - obj2.position.x - obj2.rect.width/2
##                    LRd = (LRb**2) - (4*LRa*LRc)
##                    if LRd >= 0:
##                        LRt = min(x for x in [(-LRb+math.sqrt(LRd))/(2*LRa),(-LRb-math.sqrt(LRd))/(2*LRa)] if x >= 0)
##                else:
##                    if obj1.accel.x == obj2.accel.x:
##                        RLt = (obj2.position.x - obj2.rect.width/2 - obj1.position.x - obj1.rect.width/2) / (obj2.velocity.x - obj1.velocity.x)
##                        LRt = (obj2.position.x + obj2.rect.width/2 - obj1.position.x + obj1.rect.width/2) / (obj2.velocity.x - obj1.velocity.x)
##                    else:
##                        RLa = (obj2.accel.x - obj1.accel.x)/2
##                        RLb = obj2.velocity.x - obj1.velocity.x
##                        RLc = obj2.position.x - obj2.rect.width/2 - obj1.position.x - obj1.rect.width/2
##                        RLd = (RLb**2) - (4*RLa*RLc)
##                        if RLd >= 0:
##                            RLt = min(x for x in [(-RLb+math.sqrt(RLd))/(2*RLa),(-RLb-math.sqrt(RLd))/(2*RLa)] if x >= 0)
##                        LRa = (obj2.accel.x - obj1.accel.x)/2
##                        LRb = obj2.velocity.x - obj1.velocity.x
##                        LRc = obj2.position.x + obj2.rect.width/2 - obj1.position.x + obj1.rect.width/2
##                        LRd = (LRb**2) - (4*LRa*LRc)
##                        if LRd >= 0:
##                            LRt = min(x for x in [(-LRb+math.sqrt(LRd))/(2*LRa),(-LRb-math.sqrt(LRd))/(2*LRa)] if x >= 0)
##            ###############################################################################################################implement checks for None, Negatives, other stuff
##            try:
##                RLcol[o1].append(min([RLt,LRt]))
##                RLcol[o2].append(min([RLt,LRt]))
##            except:
##                RLcol[o1].append(None)
##                RLcol[o2].append(None)
##
##            if obj1.accel.y == 0:
##                if obj2.accel.y == 0:
##                    if obj1.velocity.x == obj2.velocity.x:
##                        BTt = None
##                        TBt = None
##                    else:
##                        BTt = (obj2.position.y - obj2.rect.height/2 - obj1.position.y - obj1.rect.height/2)/(obj1.velocity.y - obj2.velocity.y)
##                        TBt = (obj1.position.y - obj1.rect.height/2 - obj2.position.y - obj2.rect.height/2)/(obj2.velocity.y - obj1.velocity.y)
##                else:
##                    BTa = obj2.accel.y/2
##                    BTb = obj2.velocity.y - obj1.velocity.y
##                    BTc = obj2.position.y - obj2.rect.height/2 - obj1.position.y - obj1.rect.height/2
##                    BTd = (BTb**2) - (4*BTa*BTc)
##                    if BTd >= 0:
##                        BTt = min(x for x in [(-BTb+math.sqrt(BTd))/(2*BTa),(-BTb-math.sqrt(BTd))/(2*BTa)] if x >= 0)
##                    TBa = BTa
##                    TBb = obj2.velocity.y - obj1.velocity.y
##                    TBc = obj2.position.y + obj2.rect.height/2 - obj1.position.y + obj1.rect.height/2
##                    TBd = (TBb**2) - (4*TBa*TBc)
##                    if TBd >= 0:
##                        TBt = min(x for x in [(-TBb+math.sqrt(TBd))/(2*TBa),(-TBb-math.sqrt(TBd))/(2*TBa)] if x >= 0)
##            else:
##                if obj2.accel.y == 0:
##                    BTa = obj1.accel.y/2
##                    BTb = obj1.velocity.y - obj2.velocity.y
##                    BTc = obj1.position.y + obj1.rect.height/2 - obj2.position.y + obj2.rect.height/2
##                    BTd = (BTb**2) - (4*BTa*BTc)
##                    if BTd >= 0:
##                        BTt = min(x for x in [(-BTb+math.sqrt(BTd))/(2*BTa),(-BTb-math.sqrt(BTd))/(2*BTa)] if x >= 0)
##                    TBa = BTa
##                    TBb = obj1.velocity.y - obj2.velocity.y
##                    TBc = obj1.position.y - obj1.rect.height/2 - obj2.position.y - obj2.rect.height/2
##                    TBd = (TBb**2) - (4*TBa*TBc)
##                    if TBd >= 0:
##                        TBt = min(x for x in [(-TBb+math.sqrt(TBd))/(2*TBa),(-TBb-math.sqrt(TBd))/(2*TBa)] if x >= 0)
##                else:
##                    if obj1.accel.y == obj2.accel.y:
##                        BTt = (obj2.position.y - obj2.rect.height/2 - obj1.position.y - obj1.rect.height/2) / (obj2.velocity.y - obj1.velocity.y)
##                        TBt = (obj2.position.y + obj2.rect.height/2 - obj1.position.y + obj1.rect.height/2) / (obj2.velocity.y - obj1.velocity.y)
##                    else:
##                        BTa = (obj2.accel.y - obj1.accel.y)/2
##                        BTb = obj2.velocity.y - obj1.velocity.y
##                        BTc = obj2.position.y - obj2.rect.height/2 - obj1.position.y - obj1.rect.height/2
##                        BTd = (BTb**2) - (4*BTa*BTc)
##                        if BTd >= 0:
##                            BTt = min(x for x in [(-BTb+math.sqrt(BTd))/(2*BTa),(-BTb-math.sqrt(BTd))/(2*BTa)] if x >= 0)
##                        TBa = (obj2.accel.y - obj1.accel.y)/2
##                        TBb = obj2.velocity.y - obj1.velocity.y
##                        TBc = obj2.position.y + obj2.rect.height/2 - obj1.position.y + obj1.rect.height/2
##                        TBd = (TBb**2) - (4*TBa*TBc)
##                        if TBd >= 0:
##                            TBt = min(x for x in [(-TBb+math.sqrt(TBd))/(2*TBa),(-TBb-math.sqrt(TBd))/(2*TBa)] if x >= 0)
##            try:
##                BTcol[o1].append(min(x for x in [BTt,TBt] if x >= 0))
##                BTcol[o2].append(min(x for x in [BTt,TBt] if x >= 0))
##            except:
##                BTcol[o1].append(None)
##                BTcol[o1].append(None)
##        #print RLcol
##        #print BTcol
                
            
            
            
    def draw(this):
        objectScreen.fill((255,255,255))
        for o in this.aliveObjects:
            this.objects[o].draw()
        if focus != -1:
            crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((464-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (484,600))
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


class Graph:
    def __init__(this, rect, yScale): #domain is a tuple (l,h) where l<=x<h
        this.rect = rect
        this.yScale = yScale
    
    def refunc(this, newfunc, domain, offset):
        this.fx = []
        this.xScale = float((domain[1]-domain[0]))/(this.rect.width-2)
        this.yScale = float(this.rect.height)/sHeight
        this.offset = offset
        this.func = newfunc
        this.steps = 0
        for rx in range(1,this.rect.width-1):
            x = rx*this.xScale
            this.fx.append(this.rect.top+int(this.yScale*eval(newfunc)))

    def step(this):
        for _ in range(int(1.0/this.xScale)):
            this.fx.pop(0)
            x = this.xScale*(this.steps + this.rect.width-2)
            this.fx.append(this.rect.top+int(this.yScale*eval(this.func)))
            this.steps += 1
        
    def draw(this):
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        for rx in range(this.rect.width-3):
            pygame.draw.line(screen,(0,0,0),(rx+this.rect.left,this.fx[rx]),(rx+this.rect.left+1,this.fx[rx+1]),1)
        pygame.draw.line(screen, (255,0,0), (0,this.fx[0]), (1023,this.fx[0]), 1)

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
        this.graph["position.x"] = Graph(graphRect, 5)
        this.graph["position.y"] = Graph(graphRect, 5)
        this.graph["velocity.x"] = Graph(graphRect, 5)
        this.graph["velocity.y"] = Graph(graphRect, 5)

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
        this.update()
        if this.textboxon:
            this.updateGraphs()
        
    def updateTextBoxes(this):
        for t in this.textbox:
            this.textbox[t].update(str(round(eval("this.obj."+t), 1)))

    def updateGraphs(this):
        possibleF = this.obj.getFunction(this.textboxon)
        this.graph[this.textboxon].refunc(this.obj.getFunction(this.textboxon),(0,60),(1,1))

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
                this.updateGraphs()
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
                this.updateGraphs()
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
        if this.textboxon:
            if this.obj.collided or ticker%10==0:
                this.obj.collided = False
                this.updateGraphs()
            else:
                this.graph[this.textboxon].step()
    
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

objectmanager.add(Object(Vector2(50,100), Vector2(10,-2), ACCEL, (25,25), 1.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(500,120), Vector2(-7.3,-3), ACCEL, (25,25), 1.0, 1.0, 1.0))

objectmanager.add(Object(Vector2(50,400), Vector2(30,-5), ACCEL, (25,25), 1.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(500,400), Vector2(-30,-5), ACCEL, (25,25), 1.0, 1.0, 1.0))

objectmanager.add(Object(Vector2(50,300), Vector2(40,-13), ACCEL, (25,25), 1.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(720,300), Vector2(-40,-15), ACCEL, (25,25), 1.0, 1.0, 1.0))

objectmanager.add(Object(Vector2(640,100), Vector2(0,-1), ACCEL, (25,25), 1.0, 1.0, 1.0))

objectmanager.add(Object(Vector2(650,500), Vector2(0,0), Vector2(0,0), (25,25), 1.0, 1.0, 1.0))

objectmanager.add(Object(Vector2(650,550), Vector2(0,0), ACCEL, (25,25), 1.0, 1.0, 0.90))

objectmanager.add(Object(Vector2(300,500), Vector2(0,-14), ACCEL, (25,25), 1.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(680,25), Vector2(0,0), ACCEL, (25,25), 1.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(720,25), Vector2(0,0), ACCEL, (25,25), 1.0, 1.0, 1.0))
                  

properter = Properter()

running = True
paused = False
focus = -1
ticker = 0
screen.fill((255,255,255))

clickRelease = 0#0 : unset
                #1 : properter.zoomSlider.move(pos)

while running:
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
