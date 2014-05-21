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
    def __init__(this, position, velocity, accel, size, mass, friction, spring, charge): #Vector2, Vector2, Vector2, (int,int), float, float, float
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
        this.charge = charge
        this.collided = False #MAKE THIS TRUE IF COLLIDE
    def update(this):
        this.lastPosition = copy.copy(this.position)
        this.lastVelocity = copy.copy(this.velocity)
        this.velocity += this.accel
        this.position += this.velocity
        if this.position.y + this.rect.height/2.0 >= sHeight: #####BAD
            over = (this.position.y+this.rect.height/2) - sHeight - 1
            this.position.y -= this.velocity.y
            this.velocity.y -= this.accel.y
            this.velocity.y = math.sqrt(abs(this.velocity.y**2 + 2*this.accel.y*(sHeight - 1 - this.position.y)))
            this.velocity.y *= -this.spring
            this.velocity.y = -math.sqrt(this.velocity.y**2 + 2*this.accel.y*over)
            this.position.y = sHeight - 1 - over
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


class ObjectManager:
    def __init__(this):
        this.nbadcol = 0
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
        
        for o1 in range(len(this.aliveObjects)): #updates
            for o2 in range(o1+1,len(this.aliveObjects)):
                this.objects[this.aliveObjects[o1]].magnetize(this.objects[this.aliveObjects[o2]])
                this.objects[this.aliveObjects[o2]].magnetize(this.objects[this.aliveObjects[o1]])                
            this.objects[this.aliveObjects[o1]].update()
        
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
                this.nbadcol += 1
                timeLeft = 1 #nononono


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
            if graphing:
                crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((464-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (464,600))
            else:
                crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((1024-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (1024,600))
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
    def stickARectInTheCurrentlyExistingRectsPleaseIfPossibleIfNotReturnFalse(this,rect):
        for i in this.aliveObjects:
            if this.objects[i].rect.colliderect(rect):
                return False
        return True

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
    def parseInput(this, event):
        if event.key == 8:
            this.backspace()
        elif event.key == 127:
            this.delete()
        elif event.key == 13:
            this.turnOff()
        elif event.key == 275:
            this.cursorMove(True)
        elif event.key == 276:
            this.cursorMove(False)
        else:
            this.assault(event.unicode)
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
        #pygame.draw.line(screen, (255,0,0), (this.rect.left+1,this.rect.bottom - this.data[-1]), (this.rect.right-1, this.rect.bottom - this.data[-1]), 1)

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

        this.graphToggle = checkBoxImg[0].get_rect().move(100,10)
        this.newBoxButton = newBlockImg[0].get_rect().move(130,10)

        this.zoomSlider = Slider(1, 4, 2, 0.5, pygame.Rect(10, 10, 80, 20))
        
        this.textboxon = False
        this.newBoxer = newboxer()
        
    def focus(this, obj):
        this.updateC()
        this.obj = obj
        this.clearGraphs()
        this.update()
        
    def updateTextBoxes(this):
        if focus != -1:
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
                this.graph[g].add((-rawData+30)*(56.0/6.0))

    def clearGraphs(this):
        for g in this.graph:
            this.graph[g].clear()

    def draw(this):
        for t in this.textbox:
            this.textbox[t].draw()
        if graphing:
            for t in this.tab:
                if t == this.textboxon:
                    this.tab[t].draw(True)
                else:
                    this.tab[t].draw(False)
            if this.textboxon:
                this.graph[this.textboxon].draw()
        this.zoomSlider.draw()
        screen.blit(checkBoxImg[graphing], this.graphToggle.topleft)
        screen.blit(newBlockImg[newboxing], this.newBoxButton.topleft)
        if newboxing:
            this.newBoxer.draw()

    def closeTextBox(this):
        if re.match(numregex, this.textbox[this.textboxon].contents) and this.textbox[this.textboxon].altered:
            exec("this.obj."+this.textboxon+" = "+this.textbox[this.textboxon].contents)
        else:
            this.updateTextBoxes()
    
    def click(this, click):
        if newboxing:
            this.newBoxer.click(click)
            return True
        else:
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
            if this.graphToggle.collidepoint(click):
                global graphing
                graphing = not graphing
                return True
            if this.newBoxButton.collidepoint(click):
                global newboxing, paused, graphing
                newboxing = True
                paused = True
                graphing = False
                return True
            if this.textboxon:
                this.closeTextBox()
            return False
    
    def keyit(this, event):
        if newboxing and this.newBoxer.on:
            this.newBoxer.box[this.newBoxer.on].parseInput(event)
            this.newBoxer.erroring = False
        elif paused:
            this.textbox[this.textboxon].parseInput(event)
            if event.key == 13:
                this.closeTextBox()
                this.textboxon = False
        return False
        
    def update(this):
        this.updateTextBoxes()
        this.updateGraphs()
    
    def updateC(this):
        objectmanager.zoom = this.zoomSlider.getValue()


class newboxer:
    def __init__(this):
        this.clear()

        this.window = pygame.Surface((284,204))
        this.window.fill((255,255,255))
        pygame.draw.rect(this.window, (0,0,0), pygame.Rect(0,0,280,200), 2)
        this.window.blit(fonts["textbox"].render("Position x:", 1, (0,0,0)), (10,10))
        this.window.blit(fonts["textbox"].render("       y:", 1, (0,0,0)), (140,10))
        this.window.blit(fonts["textbox"].render("Velocity x:", 1, (0,0,0)), (10,30))
        this.window.blit(fonts["textbox"].render("       y:", 1, (0,0,0)), (140,30))
        this.window.blit(fonts["textbox"].render("    Size w:", 1, (0,0,0)), (10,50))
        this.window.blit(fonts["textbox"].render("       h:", 1, (0,0,0)), (140,50))
        this.window.blit(fonts["textbox"].render("      Mass:", 1, (0,0,0)), (10,70))
        this.window.blit(fonts["textbox"].render("  Charge:", 1, (0,0,0)), (140,70))
        this.window.blit(fonts["textbox"].render("  Friction:", 1, (0,0,0)), (10,90))
        this.window.blit(fonts["textbox"].render("  Spring:", 1, (0,0,0)), (140,90))
        this.window.blit(xButtonImg, (265,0))
        this.closeRect = pygame.Rect(445,10,16,16)

        this.attack = Tab(pygame.Rect(220,150,200,40), "Create Object")
        
        
        
    def draw(this):
        screen.blit(this.window, (180,10))
        for t in this.box:
            this.box[t].draw()
        if this.erroring:
            this.errorMessage.draw(True)
        else:
            this.attack.draw(True)
    def click(this, point):
        if this.closeRect.collidepoint(point):
            this.clear()
            global newboxing
            newboxing = False
        elif this.attack.click(point):
            this.validate()
        else:
            for t in this.box:
                if this.box[t].rect.collidepoint(point):
                    if this.on:
                        this.box[this.on].turnOff()
                    this.box[t].turnOn()
                    this.on = t

    def validate(this):
        for t in this.box:
            if re.match(numregex, this.box[t].contents):
                exec("this."+t+"=float(this.box[t].contents)")
            else:
                this.error("One or more of your inputs was invalid.")
                return False
        possible = pygame.Rect(0,0,this.sx,this.sy)
        possible.center = (this.px,sHeight-this.py)
        if not objectmanager.stickARectInTheCurrentlyExistingRectsPleaseIfPossibleIfNotReturnFalse(possible):
            this.error("Collision")
            return False
        objectmanager.add(Object(Vector2(this.px,this.py), Vector2(this.vx,this.vy), ACCEL, (this.sx,this.sy), this.mass, this.friction, this.spring, this.charge))
        this.clear()
        global newboxing
        newboxing = False

    def error(this, message):
        this.erroring = True
        this.errorMessage = Tab(pygame.Rect(220,150,200,40), "Error: "+message)
        
    def clear(this):
        this.px = 512
        this.py = 300
        this.vx = 0
        this.vy = 0
        this.sx = 24
        this.sy = 24
        this.mass = 10
        this.charge = 0
        this.friction = 0
        this.spring = 1
        
        this.box = {}
        this.box["px"] = Textbox(pygame.Rect((268,19), (40,17)), "512")
        this.box["py"] = Textbox(pygame.Rect((385,19), (40,17)), "300")
        this.box["vx"] = Textbox(pygame.Rect((268,39), (40,17)), "0")
        this.box["vy"] = Textbox(pygame.Rect((385,39), (40,17)), "0")
        this.box["sx"] = Textbox(pygame.Rect((268,59), (40,17)), "24")
        this.box["sy"] = Textbox(pygame.Rect((385,59), (40,17)), "24")
        this.box["mass"] = Textbox(pygame.Rect((268,79), (40,17)), "10")
        this.box["charge"] = Textbox(pygame.Rect((385,79), (40,17)), "0")
        this.box["friction"] = Textbox(pygame.Rect((268,99), (40,17)), "0")
        this.box["spring"] = Textbox(pygame.Rect((385,99), (40,17)), "1")
        this.on = False
        this.erroring = False
        
        


#Initializations
pygame.init()
pygame.display.set_icon(pygame.image.load("res/img/icon.ico"))
dimensions = sWidth, sHeight = 1024, 600
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()


checkBoxImg = {0:pygame.image.load("res/img/checkboxOff.png").convert_alpha(),
               1:pygame.image.load("res/img/checkboxOn.png").convert_alpha()}

newBlockImg = {0:pygame.image.load("res/img/newBlockUpS.png").convert_alpha(),
               1:pygame.image.load("res/img/newBlockDepS.png").convert_alpha()}

scrollBarImg = pygame.image.load("res/img/scrollBar.png").convert_alpha()

xButtonImg = pygame.image.load("res/img/x.png").convert_alpha()
               


objectScreen = pygame.Surface(dimensions)

numregex = "[-+]?[0-9]*\.?[0-9]+$"
numChars = ["-",".","0","1","2","3","4","5","6","7","8","9"]

fonts = {}
fonts["textbox"] = pygame.font.Font("res/font/Courier.ttf", 12)

FPS = 30

ACCEL = Vector2(0, 9.8/FPS)

objectmanager = ObjectManager()


for x in range(100):
    objectmanager.add(Object(Vector2(randint(100,900), randint(125,175)), Vector2(randint(-10,10), randint(-10,10)), ACCEL, (5, 5), randint(1,10), 1.0, 1.0, 0.0))
##for x in range(1,150):
##    objectmanager.add(Object(Vector2(x*6, 100 + x*2), Vector2(1,0), ACCEL, (5,5), 1.0, 1.0, 1.0))

##objectmanager.add(Object(Vector2(100,400), Vector2(-1,2), ACCEL, (25,25), 50.0, 1.0, 1.0))
objectmanager.add(Object(Vector2(100,489), Vector2(25,-10), ACCEL, (20,20), 200.0, 1.0, 1.0, 0.0))

properter = Properter()

running = True
paused = True
focus = -1
graphing = False
newboxing = False
ticker = 0
screen.fill((255,255,255))
objectScreen.fill((255,255,255))

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
                    elif properter.textboxon or newboxing:
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
                    if newboxing:
                        properter.keyit(event)
                    elif event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
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
                    if properter.textboxon or newboxing:
                        properter.keyit(event)
                    elif event.key == K_p:
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
                    if newboxing:
                        properter.keyit(event)
                    elif event.key == K_p:
                        paused = not paused
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not properter.click(event.pos):
                            focus = objectmanager.click(event.pos)
                            if focus != -1:
                                properter.focus(objectmanager.objects[focus])
            objectmanager.update()
            
    if clickRelease:
        if clickRelease == 1:
            properter.zoomSlider.moveSlider(pygame.mouse.get_pos())
            properter.updateC()

    
    
    objectmanager.draw()
    properter.draw()

    
    pygame.display.flip()
    clock.tick(FPS)
print "Number of bad collisions:",objectmanager.nbadcol
pygame.quit()
