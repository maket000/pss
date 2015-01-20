#
# Interactive Physics Engine
# By: Nolan Munce
#


import copy
import math
import pygame
from pygame import *
from random import randint
import re
import sys



class Vector2:
    """A Vector in R^2"""
    
    def __init__(this, x=0.0, y=0.0):
        this.x = float(x)
        this.y = float(y)
        
    def __str__(this):
        return "%f,%f" % (this.x, this.y)

    def __repr__(this):
        return "Vector2(%f,%f" % (this.x, this.y)
    
    def __add__(this, v2):
        """Produce a new Vector2 that is the sum of
           this Vector2 and some other Vector2 v2."""
        return Vector2(this.x+v2.x, this.y+v2.y)
    
    def __iadd__(this, v2):
        """Add a Vector v2 to this Vector2."""
        this.x += v2.x
        this.y += v2.y
        return this
    
    def __sub__(this, v2):
        """Produce a new Vector2 that is the difference of
           this Vector2 from some other Vector2 v2."""
        return Vector2(this.x-v2.x, this.y-v2.y)
    
    def __neg__(this):
        """Produce the negation of this Vector2."""
        return Vector2(-this.x, -this.y)
    
    def __abs__(this):
        """Produce a Vector2 with the absolute values of the coordinates
           of this Vector2 as it's cooddinates."""
        return Vector2(abs(this.x), abs(this.y))
    
    def unit(this):
        """Produce a Vector2 that is the unit vector of this Vector2."""
        m = this.magnitude()
        if m == 0:
            return Vector2(0,0)
        return Vector2(this.x/m, this.y/m)
    
    def magnitude(this):
        """Produce the norm of this Vector2."""
        return math.sqrt(this.x**2 + this.y**2)
    
    def angle(this):
        """Determine the polar angle of this Vector2."""
        return math.atan2(this.y, this.x)
    
    def get(this):
        """Produce a tuple containing the coordinates of this Vector2."""
        return (this.x, this.y)
    
    def geti(this):
        """Produce a tuple containing the integer parts
           of the coordinates of this Vector2."""
        return (int(this.x), int(this.y))
    
    def scalarMultiply(this, n):
        """Produce a Vector2 representing the scalar multiplication
           of this Vector2 by a number n."""
        return Vector2(this.x*n, this.y*n)



class Object:
    """An Rectangle in R^2"""
    
    def __init__(this, position, velocity, accel, size, mass, friction, spring, charge, fixed): #Vector2, Vector2, Vector2, (int,int), float, float, float
        """Object constructor:
           takes Vector2, Vector2, Vector2, (int,int), float, float, float, float, bool parameters""" 
        this.position = position
        this.velocity = velocity
        this.lastPosition = copy.copy(this.position)
        this.lastVelocity = copy.copy(this.velocity)
        this.accel = copy.copy(accel)
        this.rect = pygame.Rect((0,0), size)
        this.rect.center = this.position.get()
        this.mass = mass
        this.friction = friction
        this.spring = spring
        this.charge = charge
        this.collided = False
        this.fixed = fixed
        if fixed:
            this.velocity = Vector2(0,0)
            this.accel = Vector2(0,0)

    def magnetize(this, other):
        """Change this Object's and the other Object's accelerations
           Based on the magnetic force between the two objects."""
        diff = this.position-other.position
        unit = diff.unit()
        r = diff.magnitude()
        eforce = (CK*this.charge*other.charge)/(r**2)
        this.accel += unit.scalarMultiply(eforce/this.mass)
        other.accel += -unit.scalarMultiply(eforce/other.mass)
        
        
    def update(this):
        """Update the position and velocity of this Object due
           to movement through a single frame."""
        this.lastPosition = copy.copy(this.position)
        this.lastVelocity = copy.copy(this.velocity)
        if this.fixed:
            this.velocity = Vector2(0,0)
        else:
            if this.position.y + this.rect.height/2.0 >= sHeight:
                this.position.y = sHeight - this.rect.height/2.0
                this.velocity.y *= -1
            this.velocity += this.accel
            this.position += this.velocity
            if this.position.y + this.rect.height/2.0 >= sHeight:
                this.velocity.y *= -this.spring
                this.position.y += this.velocity.y
            if this.position.x + this.rect.width/2.0 >= sWidth:
                this.position.x -= 2*((this.position.x+this.rect.width/2) - sWidth)
                this.velocity.x *= -this.spring
            if this.position.x - this.rect.width/2.0 < 0:
                this.position.x -= 2*((this.position.x-this.rect.width/2))
                this.velocity.x *= -this.spring
        this.rect.center = this.position.get()
        
    def revert(this):
        """Revert this Object's position and velocity to
           their values before this.update() was last called."""
        this.position = copy.copy(this.lastPosition)
        this.velocity = copy.copy(this.lastVelocity)
    
    def draw(this, color=(0,0,0)):
        """Draws this Object's rectangle in a
           certain colour to the object screen."""
        pygame.draw.rect(objectScreen, color, this.rect, 1)


class ObjectManager:
    """Manages the physics in a system of Objects"""
    
    def __init__(this):
        this.nbadcol = 0
        this.objects = []
        this.aliveObjects = []
        this.zoom = 1

    def collides(this, o1, o2):
        """Determine if two Objects, o1 and o2 are colliding given
           their keys in this.objects."""
        obj1 = this.objects[this.aliveObjects[o1]]
        obj2 = this.objects[this.aliveObjects[o2]]
        return obj1.rect.colliderect(obj2.rect)

    def update(this):
        """Generates the next frame for each object in the system."""
        # Magnetize each object
        for o1 in range(len(this.aliveObjects)):
            for o2 in range(o1+1,len(this.aliveObjects)):
                this.objects[this.aliveObjects[o1]].magnetize(this.objects[this.aliveObjects[o2]])
        for o in range(len(this.aliveObjects)):
            this.objects[this.aliveObjects[o]].update()

        # If there are any collisions, revert the objects that collide
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

        # For every collision, determine which side of each object collided
        RLcol = [[] for x in range(len(this.aliveObjects))]
        BTcol = [[] for x in range(len(this.aliveObjects))]
        
        for o1,o2 in collisions:
            obj1 = this.objects[o1]
            obj2 = this.objects[o2]
            if (obj1.velocity.x == obj2.velocity.x and obj1.accel.x == obj2.accel.x):
                RLt = None
                LRt = None
            elif obj1.accel.x == obj2.accel.x:
                RLt = (obj2.position.x - obj2.rect.width/2.0
                       - obj1.position.x - obj1.rect.width/2.0) \
                      / (obj1.velocity.x - obj2.velocity.x)
                LRt = (obj1.position.x - obj1.rect.width/2.0
                       - obj2.position.x - obj2.rect.width/2.0) \
                      / (obj2.velocity.x - obj1.velocity.x)
            else:
                try: #There might be a physics logic error here. 
                    t1 = ((obj1.velocity.x - obj2.velocity.x)
                          + math.sqrt((obj1.velocity.x - obj2.velocity.x)**2
                                      - 2*(obj1.accel.x - obj2.accel.x)
                                           * (obj1.position.x
                                              + obj1.rect.width/2.0
                                              - obj2.position.x
                                              + obj2.rect.width/2.0))) \
                         / (obj1.accel.x - obj2.accel.x)
                    t2 = ((obj1.velocity.x - obj2.velocity.x)
                          - math.sqrt((obj1.velocity.x - obj2.velocity.x)**2
                                      - 2*(obj1.accel.x - obj2.accel.x)
                                           * (obj1.position.x
                                              + obj1.rect.width/2.0
                                              - obj2.position.x
                                              + obj2.rect.width/2.0))) \
                         / (obj1.accel.x - obj2.accel.x) 
                except:
                    t1 = -1
                    t2 = -1
                RLt = []
                if t1 > 0:
                    RLt.append(t1)
                if t2 > 0:
                    RLt.append(t2)
                if RLt:
                    RLt = min(RLt)
                else:
                    RLt = None
                
                try:
                    t1 = ((obj2.velocity.x - obj1.velocity.x) +
                          math.sqrt((obj2.velocity.x - obj1.velocity.x) ** 2
                                    - 2*(obj2.accel.x - obj1.accel.x)
                                    * (obj2.position.x + obj2.rect.width/2.0
                                       - obj1.position.x + obj1.rect.width/2.0))) \
                         / (obj2.accel.x - obj1.accel.x)
                    t2 = ((obj2.velocity.x - obj1.velocity.x)
                          - math.sqrt((obj2.velocity.x - obj1.velocity.x)**2
                                      - 2*(obj2.accel.x - obj1.accel.x)
                                      * (obj2.position.x + obj2.rect.width/2.0
                                         - obj1.position.x + obj1.rect.width/2.0))) \
                         / (obj2.accel.x - obj1.accel.x)
                except:
                    t1 = -1
                    t2 = -1
                LRt = []
                if t1 > 0:
                    LRt.append(t1)
                if t2 > 0:
                    LRt.append(t2)
                if LRt:
                    LRt = min(LRt)
                else:
                    LRt = None
                        
            if obj1.velocity.y == obj2.velocity.y and obj1.accel.y == obj2.accel.y:
                BTt = None
                TBt = None
            elif obj1.accel.y == obj2.accel.y:
                BTt = (obj2.position.y - obj2.rect.height/2.0
                       - obj1.position.y - obj1.rect.height/2.0) \
                      / (obj1.velocity.y - obj2.velocity.y)
                TBt = (obj1.position.y - obj1.rect.height/2.0
                       - obj2.position.y - obj2.rect.height/2.0) \
                      / (obj2.velocity.y - obj1.velocity.y)
            else:
                try: # Once more, possible physics logic error.
                     # The discriminants are equal and I'm not sure if that's correct.
                    t1 = ((obj1.velocity.y - obj2.velocity.y)
                          + math.sqrt((obj1.velocity.y - obj2.velocity.y)**2
                                      - 2*(obj1.accel.y - obj2.accel.y)
                                      * (obj1.position.y
                                         + obj1.rect.height/2.0
                                         - obj2.position.y
                                         + obj2.rect.height/2.0))) \
                         / (obj1.accel.y - obj2.accel.y)
                    t2 = ((obj1.velocity.y - obj2.velocity.y)
                          - math.sqrt((obj1.velocity.y - obj2.velocity.y)**2
                                      - 2*(obj1.accel.y - obj2.accel.y)
                                      * (obj1.position.y
                                         + obj1.rect.height/2.0
                                         - obj2.position.y
                                         + obj2.rect.height/2.0))) \
                         / (obj1.accel.y - obj2.accel.y)
                except:
                    t1 = -1
                    t2 = -1
                BTt = []
                if t1 > 0:
                    BTt.append(t1)
                if t2 > 0:
                    BTt.append(t2)
                if BTt:
                    BTt = min(BTt)
                else:
                    BTt = None
                
                try:
                    t1 = ((obj2.velocity.y - obj1.velocity.y)
                          + math.sqrt((obj2.velocity.y - obj1.velocity.y)**2
                                      - 2*(obj2.accel.y - obj1.accel.y)
                                      * (obj2.position.y
                                         + obj2.rect.height/2.0
                                         - obj1.position.y
                                         + obj1.rect.height/2.0))) \
                         / (obj2.accel.y - obj1.accel.y)
                    t2 = ((obj2.velocity.y - obj1.velocity.y)
                          - math.sqrt((obj2.velocity.y - obj1.velocity.y)**2
                                      - 2*(obj2.accel.y - obj1.accel.y)
                                      * (obj2.position.y + obj2.rect.height/2.0
                                         - obj1.position.y
                                         + obj1.rect.height/2.0))) \
                         / (obj2.accel.y - obj1.accel.y)
                except:
                    t1 = -1
                    t2 = -1
                TBt = []
                if t1 > 0:
                    TBt.append(t1)
                if t2 > 0:
                    TBt.append(t2)
                if TBt:
                    TBt = min(TBt)
                else:
                    TBt = None

            #Sets new positions and velocities of Objects based on how they collided
            if 0 <= RLt <= 1:
                obj1.position.x += obj1.velocity.x*RLt + 0.5*obj1.accel.x*RLt**2
                obj2.position.x = obj1.position.x + obj1.rect.width/2 + obj2.rect.width/2
                obj1.velocity.x, obj2.velocity.x = (obj1.velocity.x * (obj1.mass - obj2.mass)
                                                    + 2*obj2.mass*obj2.velocity.x) \
                                                   / (obj1.mass + obj2.mass), \
                                                   (obj2.velocity.x * (obj2.mass - obj1.mass)
                                                    + 2*obj1.mass*obj1.velocity.x) \
                                                   / (obj2.mass + obj1.mass)
                timeLeft = 1 - RLt
            elif 0 <= LRt <= 1:
                obj1.position.x += obj1.velocity.x*LRt + 0.5*obj1.accel.x*LRt**2
                obj2.position.x = obj1.position.x - (obj1.rect.width/2 + obj2.rect.width/2)
                obj1.velocity.x, obj2.velocity.x = (obj1.velocity.x * (obj1.mass - obj2.mass)
                                                    + 2*obj2.mass*obj2.velocity.x) \
                                                   / (obj1.mass + obj2.mass), \
                                                   (obj2.velocity.x * (obj2.mass - obj1.mass)
                                                    + 2*obj1.mass*obj1.velocity.x) \
                                                   / (obj2.mass + obj1.mass)
                timeLeft = 1 - LRt
            elif 0 <= BTt <= 1:
                obj1.position.y += obj1.velocity.x*BTt + 0.5*obj1.accel.y*BTt**2
                obj2.position.y = obj1.position.y + obj1.rect.height/2 + obj2.rect.width/2
                obj1.velocity.y, obj2.velocity.y = (obj1.velocity.y * (obj1.mass - obj2.mass)
                                                    + 2*obj2.mass*obj2.velocity.y) \
                                                   / (obj1.mass + obj2.mass), \
                                                   (obj2.velocity.y * (obj2.mass - obj1.mass)
                                                    + 2*obj1.mass*obj1.velocity.y) \
                                                   / (obj2.mass + obj1.mass)
                timeLeft = 1 - BTt
            elif 0 <= TBt <= 1:
                obj1.position.y += obj1.velocity.x*TBt + 0.5*obj1.accel.y*TBt**2
                obj2.position.y = obj1.position.y - (obj1.rect.height/2 + obj2.rect.width/2)
                obj1.velocity.y, obj2.velocity.y = (obj1.velocity.y * (obj1.mass - obj2.mass)
                                                    + 2*obj2.mass*obj2.velocity.y) \
                                                   / (obj1.mass + obj2.mass), \
                                                   (obj2.velocity.y * (obj2.mass - obj1.mass)
                                                    + 2*obj1.mass*obj1.velocity.y) \
                                                    / (obj2.mass + obj1.mass)
                timeLeft = 1 - TBt
            # The collision could not be determined, this results in strange effects
            else:
                this.nbadcol += 1
                timeLeft = 1


            obj1.position += obj1.velocity.scalarMultiply(timeLeft)
            
            obj1.rect.center = obj1.position.get()
            obj2.rect.center = obj2.position.get()

        # Resets the acceleration of every object to that imposed by gravity
        for o in range(len(this.aliveObjects)):
            this.objects[this.aliveObjects[o]].accel = copy.copy(ACCEL)
            
            
    def draw(this):
        """Draw each object onto the object screen."""
        objectScreen.fill((255,255,255))
        for o in this.aliveObjects:
            if focus == o:
                this.objects[o].draw((0,255,0))
            elif this.objects[o].charge < 0:
                this.objects[o].draw((0,0,255))
            elif this.objects[o].charge > 0:
                this.objects[o].draw((255,0,0))
            else:
                this.objects[o].draw()
        if focus != -1:
            if graphing: #These lines are painful to look at, long, magic numbers. I'll fix these later.
                crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((464-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (464,600))
            else:
                crop = pygame.transform.smoothscale(objectScreen.subsurface(this.objects[focus].rect.inflate((1024-this.objects[focus].rect.width)/this.zoom,(600-this.objects[focus].rect.height)/this.zoom).clamp(objectScreen.get_rect())), (1024,600))
            screen.blit(crop,(0,0))
        else:
            screen.blit(objectScreen, (0,0))
            
    def add(this, obj):
        """Add a new object to the system."""
        this.objects.append(obj)
        if this.aliveObjects:
            this.aliveObjects.append(this.aliveObjects[-1]+1)
        else:
            this.aliveObjects.append(len(this.objects)-1)
            
    def click(this, pos):
        """Click on the object screen, if there is no focus and
           the click collieds with an Object, focus is set to that Object."""
        if focus == -1:
            for i in this.aliveObjects:
                if this.objects[i].rect.collidepoint(pos):
                    return i
        return -1
    
    def stickARectInTheCurrentlyExistingRectsPleaseIfPossibleIfNotReturnFalse(this,rect):
        """Test that a Rectangle doesn't collide with any rectangle already in the system."""
        for i in this.aliveObjects:
            if this.objects[i].rect.colliderect(rect):
                return False
        return True

    def delete(this):
        """Remove the Object that has focus from the system."""
        this.objects.pop(focus)
        this.aliveObjects.pop(this.aliveObjects.index(focus))

class Tab:
    """A Tab GUI element"""
    
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
        """Determine if a click collides with this Tab."""
        return this.rect.collidepoint(point)
    
    def draw(this, on):
        """Draw this tab to the screen."""
        screen.blit(this.visual[on], this.rect.topleft)
        

class Textbox:
    """An input textbox"""
    
    def __init__(this, rect, contents):
        this.rect = rect
        this.textpos = (rect.left+3, rect.top+2)
        this.contents = contents
        this.on = False
        this.cursor = 0
        this.altered = False
        this.render()
        
    def parseInput(this, event):
        """Parse keyboard input given to this Textbox and
           change the contents of this accordingly."""
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
        """Allow input to this Textbox."""
        this.on = True
        this.cursor = 0
        this.altered = False
        
    def turnOff(this):
        """Deny input to this Textbox."""
        this.on = False
        return this.altered
    
    def assault(this, text):
        """Add text to the contents of this Textbox."""
        if text in numChars:
            this.contents = this.contents[:this.cursor]+text+this.contents[this.cursor:]
            this.cursor += 1
            this.altered = True
            this.render()
            
    def backspace(this):
        """Remove the character behind the cursor in this Textbox."""
        if this.cursor:
            this.contents = this.contents[:this.cursor-1]+this.contents[this.cursor:]
            this.cursor -= 1
            this.altered = True
            this.render()
            
    def delete(this):
        """Remove the character in front of the cursor in thie Textbox."""
        if this.cursor != len(this.contents):
            this.contents = this.contents[:this.cursor]+this.contents[this.cursor+1:]
            this.altered = True
            this.render()
            
    def cursorMove(this, forward):
        """Move the position of the cursor in this Textbox."""
        if forward and this.cursor != len(this.contents):
            this.cursor += 1
        elif not(forward) and this.cursor != 0:
            this.cursor -= 1
            
    def update(this, contents):
        """Update the contents of this Textbox."""
        this.contents = contents
        this.render()
        
    def render(this):
        """Render the contents of this Textbox."""
        this.rendered = fonts["textbox"].render(this.contents, 1, (0,0,0))
        
    def draw(this):
        """Draw this Textbox to the screen."""
        if this.on:
            pygame.draw.rect(screen, (222,222,222), this.rect, 0)
            cursorXpos = fonts["textbox"].size(this.contents[:this.cursor])[0]+this.rect.left+2
            if ((ticker%30)/15) and paused:
                pygame.draw.line(screen, (0,0,0), (cursorXpos, this.rect.top+2), (cursorXpos, this.rect.bottom-4), 1)
            
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        screen.blit(this.rendered, this.textpos)


class Graph:
    """A graph of the movement of Objects."""
    
    def __init__(this, rect, axis):
        this.rect = rect
        this.data = []
        this.axis = axis
        if this.axis:
            this.ap = [(rect.left, rect.centery), (rect.right, rect.centery)]
            
    def clear(this):
        """Clear data stored in this Graph."""
        this.data = []
        
    def add(this, data):
        """Add data to this Graph."""
        this.data.append(data)
        
    def draw(this):
        """Draw this graph to the screen."""
        pygame.draw.rect(screen, (0,0,0), this.rect, 1)
        offset = len(this.data)-this.rect.width
        if offset < 0:
            offset = 0
        if this.axis:
            pygame.draw.line(screen, (0,0,0), this.ap[0], this.ap[1], 1)
        for x in range(len(this.data)-this.rect.width, len(this.data)-2):
            if x>=0:
                pygame.draw.line(screen,(0,0,0),(x+this.rect.left - offset,this.rect.bottom - this.data[x]),(x+this.rect.left+1 - offset,this.rect.bottom - this.data[x+1]),1)

class Slider:
    """A slider GUI element"""
    
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
        this.ztext = fonts["textbox"].render("ZOOM", 1, (0,0,0))
        for x in range(ticks+1):
            this.notches.append((this.rect.left + x * twid, this.rect.centery))
            this.values.append(low + x*interval)

        this.slider = pygame.Rect(0,0,5,30)
        this.updateSlider()
        
    def click(this, pos):
        """Check if a click hits this Slider and act accordingly."""
        if this.slider.collidepoint(pos):
            global clickRelease
            clickRelease = 1
            return True
        if this.rect.collidepoint(pos):
            this.moveSlider(pos)
            return True
        return False

    def moveSlider(this, pos):
        """Change the position of this Slider."""
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
        """Draw this Slider to the screen."""
        screen.blit(scrollBoxImg, this.rect.topleft)
        pygame.draw.rect(screen, (100,0,0), this.slider, 2)
        
    def updateSlider(this):
        """Update the position of this Slider."""
        this.slider.center = this.notches[this.current]
        
    def getValue(this):
        """Get the value of this Slider's current notch."""
        return this.values[this.current]
        

class Properter:
    """Manages all GUI elements of the engine"""
    
    def __init__(this):
        """Creates all necessary GUI objects."""
        this.obj = False
        this.textbox = {}
        this.boxText = pygame.Surface((216,80))

        this.textbox["position.x"] = Textbox(pygame.Rect((84,41), (40,17)), "")
        this.textbox["position.y"] = Textbox(pygame.Rect((180,41), (40,17)), "")
        this.textbox["velocity.x"] = Textbox(pygame.Rect((84,61), (40,17)), "")
        this.textbox["velocity.y"] = Textbox(pygame.Rect((180,61), (40,17)), "")
        this.textbox["mass"] = Textbox(pygame.Rect((84,81), (40,17)), "")
        this.textbox["charge"] = Textbox(pygame.Rect((180,81), (40,17)), "")
        this.textbox["friction"] = Textbox(pygame.Rect((84,101), (40,17)), "")
        this.textbox["spring"] = Textbox(pygame.Rect((180,101), (40,17)), "")

        this.boxText.fill((255,255,255))
        pygame.draw.rect(this.boxText, (0,0,0), pygame.Rect(0,0,216,80), 1)
        this.boxText.blit(fonts["textbox"].render("Position x:", 1, (0,0,0)), (1,2))
        this.boxText.blit(fonts["textbox"].render("       y:", 1, (0,0,0)), (111,2))
        this.boxText.blit(fonts["textbox"].render("Velocity x:", 1, (0,0,0)), (1,22))
        this.boxText.blit(fonts["textbox"].render("       y:", 1, (0,0,0)), (111,22))
        this.boxText.blit(fonts["textbox"].render("      Mass:", 1, (0,0,0)), (1,42))
        this.boxText.blit(fonts["textbox"].render("  Charge:", 1, (0,0,0)), (111,42))
        this.boxText.blit(fonts["textbox"].render("  Friction:", 1, (0,0,0)), (1,62))
        this.boxText.blit(fonts["textbox"].render("  Spring:", 1, (0,0,0)), (111,62))


        graphRect = pygame.Rect(464, 40, 560, 560)
        this.graph = {}
        this.graph["position.x"] = Graph(graphRect, False)
        this.graph["position.y"] = Graph(graphRect, False)
        this.graph["velocity.x"] = Graph(graphRect, True)
        this.graph["velocity.y"] = Graph(graphRect, True)

        this.tab = {}
        this.tab["position.x"] = Tab(pygame.Rect(464, 9, 125, 30), "x position")
        this.tab["position.y"] = Tab(pygame.Rect(590, 9, 125, 30), "y position")
        this.tab["velocity.x"] = Tab(pygame.Rect(716, 9, 125, 30), "x velocity")
        this.tab["velocity.y"] = Tab(pygame.Rect(842, 9, 125, 30), "y velocity")

        this.graphToggle = checkBoxImg[0].get_rect().move(100,10)
        this.newBoxButton = newBlockImg[0].get_rect().move(130,7)
        this.deleteButton = deleteButtonImg.get_rect().move(160,7)
        this.quitButton = xButtonImg.get_rect().move(1008,0)

        this.zoomSlider = Slider(1, 4, 0, 0.5, pygame.Rect(10, 10, 80, 20))
        
        this.textboxon = False
        this.graphon = False
        this.newBoxer = newboxer()
        
    def focus(this, obj):
        """Change focus to an Object obj."""
        this.updateC()
        this.obj = obj
        this.clearGraphs()
        this.update()
        
    def updateTextBoxes(this):
        """Update the values of the Textboxes."""
        if focus != -1:
            for t in this.textbox:
                this.textbox[t].update(str(round(eval("this.obj."+t), 1)))

    def updateGraphs(this):
        """Update the values of the Graphs."""
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
        """Clears all the graphs."""
        for g in this.graph:
            this.graph[g].clear()

    def draw(this):
        """Draws the GUI to the screen."""
        screen.blit(this.boxText, (5,40))
        for t in this.textbox:
            this.textbox[t].draw()
        if graphing and focus != -1:
            if this.graphon:
                this.graph[this.graphon].draw()
                pygame.draw.rect(screen, (255,255,255), pygame.Rect(this.graph[this.graphon].rect.x,0,this.graph[this.graphon].rect.width, 40), 0)
            for t in this.tab:
                if t == this.graphon:
                    this.tab[t].draw(True)
                else:
                    this.tab[t].draw(False)
        this.zoomSlider.draw()
        screen.blit(checkBoxImg[graphing], this.graphToggle.topleft)
        screen.blit(newBlockImg[newboxing], this.newBoxButton.topleft)
        screen.blit(deleteButtonImg, this.deleteButton.topleft)
        screen.blit(xButtonImg, this.quitButton.topleft)
        if newboxing:
            this.newBoxer.draw()

    def closeTextBox(this):
        """Removes focus from a Textbox."""
        if re.match(numregex, this.textbox[this.textboxon].contents) and this.textbox[this.textboxon].altered:
            exec("this.obj."+this.textboxon+" = "+this.textbox[this.textboxon].contents)
        else:
            this.updateTextBoxes()
    
    def click(this, click):
        """Parse a click on the GUI."""
        if this.quitButton.collidepoint(click):
            global running
            running = False
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
                    this.textbox[t].cursor = len(this.textbox[t].contents)
                    this.textboxon = t
                    return True
            for t in this.tab:
                if this.tab[t].click(click):
                    for off in this.tab:
                        if off != t:
                            this.tab[off].on = False
                    if t == this.graphon:
                        this.graphon = False
                    else:
                        this.graphon = t
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
            if this.deleteButton.collidepoint(click) and focus != -1:
                objectmanager.delete()
            
            return False
    
    def keyit(this, event):
        """Sends input to any active Textboxes."""
        if newboxing and this.newBoxer.on:
            this.newBoxer.box[this.newBoxer.on].parseInput(event)
            this.newBoxer.erroring = False
        elif paused and this.textboxon:
            this.textbox[this.textboxon].parseInput(event)
            if event.key == 13:
                this.closeTextBox()
                this.textboxon = False
        return False
        
    def update(this):
        """Updates the GUI."""
        this.updateTextBoxes()
        this.updateGraphs()
    
    def updateC(this):
        """Updates the zoom on the objects."""
        objectmanager.zoom = this.zoomSlider.getValue()


class newboxer:
    """Window used to generate a new Object"""
    def __init__(this):
        """Creates all necessary Textbox objects."""
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
        """Draw the dialog to the screen."""
        screen.blit(this.window, (180,10))
        for t in this.box:
            this.box[t].draw()
        if this.erroring:
            this.errorMessage.draw(True)
        else:
            this.attack.draw(True)
            
    def click(this, point):
        """Parse a click on the dialog."""
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
                    this.box[t].cursor = len(this.box[t].contents)
                    this.on = t

    def validate(this):
        """Ensure that values of the new Object are valid."""
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
        objectmanager.add(Object(Vector2(this.px,this.py),
                                 Vector2(this.vx,this.vy),
                                 ACCEL, (this.sx,this.sy),
                                 this.mass, this.friction,
                                 this.spring, this.charge, False))
        this.clear()
        global newboxing
        newboxing = False

    def error(this, message):
        """Produce and error messaage to the user on the dialog."""
        this.erroring = True
        this.errorMessage = Tab(pygame.Rect(220,150,200,40), "Error: "+message)
        
    def clear(this):
        """Clear all Textboxes in the dialog."""
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
        this.box["mass"] = Textbox(pygame.Rect((268,79), (40,17)), "100")
        this.box["charge"] = Textbox(pygame.Rect((385,79), (40,17)), "0")
        this.box["friction"] = Textbox(pygame.Rect((268,99), (40,17)), "0")
        this.box["spring"] = Textbox(pygame.Rect((385,99), (40,17)), "1")
        this.on = False
        this.erroring = False
        
        


# Initializations
pygame.init()

# Setting the icon only works in beta releases of pygame.
# pygame.display.set_icon(pygame.image.load("res/img/icon.ico"))

dimensions = sWidth, sHeight = 1024, 600
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()


checkBoxImg = {0:pygame.image.load("res/img/checkboxOff.png").convert_alpha(),
               1:pygame.image.load("res/img/checkboxOn.png").convert_alpha()}

newBlockImg = {0:pygame.image.load("res/img/newBlockUpS.png").convert_alpha(),
               1:pygame.image.load("res/img/newBlockDepS.png").convert_alpha()}

scrollBarImg = pygame.image.load("res/img/scrollBar.png").convert_alpha()
scrollBoxImg = pygame.image.load("res/img/scrollBox.png").convert_alpha()

xButtonImg = pygame.image.load("res/img/x.png").convert_alpha()
deleteButtonImg = pygame.image.load("res/img/deleteButton.png").convert_alpha()
               


objectScreen = pygame.Surface(dimensions)

numregex = "[-+]?[0-9]*\.?[0-9]+$"
numChars = ["-",".","0","1","2","3","4","5","6","7","8","9"]

fonts = {}
fonts["textbox"] = pygame.font.Font("res/font/Courier.ttf", 12)

FPS = 30

CK = 8.9875517873681764*10**9
ACCEL = Vector2(0, 9.8/FPS)

objectmanager = ObjectManager()

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
    if paused:
        if focus != -1:
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
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if newboxing:
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
    
# Some preset sets of objects
    keys = pygame.key.get_pressed()
    if keys[K_F5]:
        # Random Small Objects
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(25):
            objectmanager.add(Object(Vector2(randint(20,1000),randint(20,580)), Vector2(0,0), ACCEL, (4,4), 100, 1.0, 1.0, 0.0, False))
            
    if keys[K_F6]:
        # Random Small Objects with velocity
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(25):
            objectmanager.add(Object(Vector2(randint(20,1000),randint(20,580)), Vector2(randint(-10,10),randint(-10,10)), ACCEL, (4,4), 100, 1.0, 1.0, 0.0, False))

    elif keys[K_F7]:
        # Random Small Objects with charge
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(25):
            objectmanager.add(Object(Vector2(randint(20,1000),randint(20,580)), Vector2(0,0), ACCEL, (4,4), 100, 1.0, 1.0, [0.001,-0.001][randint(0,1)], False))

    elif keys[K_F8]:
        # magnet cage with 1 object with velocity
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(16):
            objectmanager.add(Object(Vector2(32+x*64,25), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(32+x*64,575), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        for x in range(1,11):
            objectmanager.add(Object(Vector2(32,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(992,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        objectmanager.add(Object(Vector2(512,300), Vector2(10,10), ACCEL, (24,24), 10, 1.0, 1.0, 0.01, False))

    elif keys[K_F9]:
        # Magnet cage with 2 Objects
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(16):
            objectmanager.add(Object(Vector2(32+x*64,25), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(32+x*64,575), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        for x in range(1,11):
            objectmanager.add(Object(Vector2(32,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(992,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        objectmanager.add(Object(Vector2(512,300), Vector2(10,10), ACCEL, (24,24), 10, 1.0, 1.0, 0.01, False))
        objectmanager.add(Object(Vector2(412,200), Vector2(10,10), ACCEL, (24,24), 10, 1.0, 1.0, 0.01, False))

    elif keys[K_F10]:
        # Magnet cage with 2 Objects with velocity
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        for x in range(16):
            objectmanager.add(Object(Vector2(32+x*64,25), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(32+x*64,575), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        for x in range(1,11):
            objectmanager.add(Object(Vector2(32,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
            objectmanager.add(Object(Vector2(992,25+50*x), Vector2(0,0), ACCEL, (64,50), 2000, 1.0, 1.0, 0.01, True))
        objectmanager.add(Object(Vector2(512,300), Vector2(20,20), ACCEL, (24,24), 10, 1.0, 1.0, 0.01, False))
        objectmanager.add(Object(Vector2(412,200), Vector2(20,20), ACCEL, (24,24), 10, 1.0, 1.0, 0.01, False))

    elif keys[K_F11]:
        # Oil Drop Experiment
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()
        objectmanager.add(Object(Vector2(500,300), Vector2(0,0), ACCEL, (160,60), 10, 1.0, 1.0, 0.01, True))
        objectmanager.add(Object(Vector2(500,500), Vector2(0,0), ACCEL, (24,24), 1, 1.0, 1.0, -0.00014538627399100616, False))

    elif keys[K_F12]:
        #Resets environment
        focus = -1
        objectmanager = ObjectManager()
        properter = Properter()

    pygame.display.flip()
    clock.tick(30)

#This measures how bad I am at physics, as well as the inconsistency of floating point numbers
print "Number of bad collisions:", objectmanager.nbadcol
pygame.quit()
