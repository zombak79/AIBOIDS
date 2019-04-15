import pyglet
import random
import math
from pyglet import gl

WIDTH = 1400
HEIGHT = 900

OFFSET = 100000

BOID_RADIUS = 8
BOID_COUNT = 30
BOID_SPEED = 5
MAX_SPEED = 15

DESIRED_DISTANCE = 40
EYESIGHT_RADIUS = 200

SPACING = True
GROUPING = True

MOUSE_COHESION_FACTOR = 0.09
COHESION_FACTOR = 0.01
SEPARATION_FACTOR = 0.1
ALIGNMENT_FACTOR = 0.6

window = pyglet.window.Window(width=WIDTH, height=HEIGHT+20)

paused = False
mousex = 0
mousey = 0
mouse = 'None'


class Boid:
    def __init__(self,id=0):
        #init boid randomly
        self.id=id
        self.r = BOID_RADIUS
        self.x = random.randint(0+BOID_RADIUS,WIDTH-BOID_RADIUS) + OFFSET
        self.y = random.randint(0+BOID_RADIUS,HEIGHT-BOID_RADIUS) + OFFSET
        self.vx = random.randint(-1*MAX_SPEED,1*MAX_SPEED)
        self.vy = random.randint(-1*MAX_SPEED,1*MAX_SPEED)
        #cohesion vector
        self.cx = 0 
        self.cy = 0
        #separation vector
        self.sx = 0 
        self.sy = 0
        #alignment vector
        self.ax = 0 
        self.ay = 0
        #mouse cohesion vector
        self.mx = 0
        self.my = 0 

    def draw(self):
        #draw boid
        self.circle(self.x-OFFSET,self.y-OFFSET,self.r)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (self.x-OFFSET, self.y-OFFSET, self.x-OFFSET+int(self.vx), self.y-OFFSET+int(self.vy))))
        #print status
        
    def circle(self, x, y, radius):
        iterations = 6
        s = math.sin(2*math.pi / iterations)
        c = math.cos(2*math.pi / iterations)

        dx, dy = radius, 0

        gl.glBegin(gl.GL_LINE_STRIP)
        for i in range(iterations+1):
            gl.glVertex2f(x+dx, y+dy)
            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
        gl.glEnd()

    def get_speed(self):
        return math.sqrt(((self.vx)**2)+((self.vy)**2))

    def set_speed(self):
        speed = self.get_speed()
  
        if not speed == 0:
            self.vx=(self.vx/speed)*MAX_SPEED
            self.vy=(self.vy/speed)*MAX_SPEED
    
    def calc_distance(self,x1,x2,y1,y2):
        return math.sqrt(((x1-x2)**2)+((y1-y2)**2))
    
    def distance(self,boid):
        #print(self.x,self.y,boid.x,boid.y)
        distance = self.calc_distance(self.x,boid.x,self.y,boid.y)
        self.ix=self.x
        self.iy=self.y
        distance2 = self.calc_distance(self.x+WIDTH,boid.x,self.y,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x+WIDTH
            self.iy=self.y
        distance2 = self.calc_distance(self.x-WIDTH,boid.x,self.y,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x-WIDTH
            self.iy=self.y
        distance2 = self.calc_distance(self.x,boid.x,self.y+HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x
            self.iy=self.y+HEIGHT
        distance2 = self.calc_distance(self.x,boid.x,self.y-HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x
            self.iy=self.y-HEIGHT
        distance2 = self.calc_distance(self.x-WIDTH,boid.x,self.y-HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x-WIDTH
            self.iy=self.y-HEIGHT
        distance2 = self.calc_distance(self.x+WIDTH,boid.x,self.y+HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x+WIDTH
            self.iy=self.y+HEIGHT        
        distance2 = self.calc_distance(self.x+WIDTH,boid.x,self.y-HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x+WIDTH
            self.iy=self.y-HEIGHT
        distance2 = self.calc_distance(self.x-WIDTH,boid.x,self.y+HEIGHT,boid.y)
        if distance2<distance:
            distance=distance2
            self.ix=self.x-WIDTH
            self.iy=self.y+HEIGHT
        #print(distance)
        return distance

    #http://www.vergenet.net/~conrad/boids/pseudocode.html
    #Rule 1: Boids try to fly towards the centre of mass of neighbouring boids. (cohesion)
    def cohesion(self,boids):
        if not GROUPING:
            self.cx = 0
            self.cy = 0
            return
        count = 0
        x=0
        y=0
        for neighbour in boids.boids:
            if not self.id == neighbour.id:
                if self.distance(neighbour)<EYESIGHT_RADIUS:
                    x+=neighbour.x
                    y+=neighbour.y
                    count+=1
        if count>0:
            x=(x/count-self.ix)*COHESION_FACTOR
            y=(y/count-self.iy)*COHESION_FACTOR
        else:
            x=0
            y=0

        self.cx = x
        self.cy = y


    #Rule 2: Boids try to keep a small distance away from other objects (including other boids). (separation)
    def separation(self,boids):
        if not SPACING:
            self.sx = 0
            self.sy = 0
            return
        x=0
        y=0
        for neighbour in boids.boids:
            if not self.id == neighbour.id:
                if self.distance(neighbour)<DESIRED_DISTANCE:
                    x=x-(neighbour.x-self.ix)
                    y=y-(neighbour.y-self.iy)
        self.sx = x*SEPARATION_FACTOR
        self.sy = y*SEPARATION_FACTOR

    #Rule 3: Boids try to match velocity with near boids. (alignment)
    def alignment(self,boids):
        count = 0
        x=0
        y=0
        for neighbour in boids.boids:
            if not self.id == neighbour.id:
                if self.distance(neighbour)<DESIRED_DISTANCE:
                    x+=neighbour.vx
                    y+=neighbour.vy
                    count+=1
        if count>0:
            self.ax = (x/count)*ALIGNMENT_FACTOR
            self.ay = (y/count)*ALIGNMENT_FACTOR
        else:
            self.ax=0
            self.ay=0

    #my own set of rules:
    #Rule 4: Boids try to follow mouse
    def mouse_follow(self):
        global mouse
        global mousex
        global mousey
        mouseboid = Boid()
        mouseboid.x=mousex+OFFSET
        mouseboid.y=mousey+OFFSET

        if mouse == 'Follow':
            if self.distance(mouseboid)<EYESIGHT_RADIUS:
                self.mx=(mouseboid.x-self.ix)*MOUSE_COHESION_FACTOR
                self.my=(mouseboid.y-self.iy)*MOUSE_COHESION_FACTOR
            else:
                self.mx=0
                self.my=0
        else:
            self.mx=0
            self.my=0

    #Rule 5: Boids try to eat food (blue)

    def tick(self):
        #calculate new speed vector
        self.vx+=self.ax+self.sx+self.cx+self.mx
        self.vy+=self.ay+self.sy+self.cy+self.my
        #limit speed
        if self.get_speed()>MAX_SPEED:
            self.set_speed()
        #move boid with speed vector
        self.x += int(self.vx)
        self.y += int(self.vy)
        #if boid is out of screen move it on the other side
        if self.x > WIDTH+OFFSET:
            self.x -= WIDTH
        if self.y>HEIGHT+OFFSET:
            self.y -= HEIGHT 
        if self.x<OFFSET:
            self.x += WIDTH
        if self.y<OFFSET:
            self.y += HEIGHT 

class Boids:
    def __init__(self):
        #init new set of boids
        self.boids = []
        for i in range(0,BOID_COUNT):
            boid = Boid(i)
            self.boids.append(boid)

    def tick(self):
        global paused
        if not paused:
            #move all boids
            for boid in self.boids:
                boid.cohesion(self)
                boid.separation(self)
                boid.alignment(self)
                boid.mouse_follow()
                boid.tick()

boids = Boids()
pressed_keys = []

def tick(td):
    boids.tick()
    
def draw():
    global mousex
    global mousey
    global mouse
    window.clear()
    status = "<R>Restart simulation <SPACE>paused:"+str(paused)+" <G>Grouping:"+str(GROUPING)+" <S>Spacing:"+str(SPACING)
    status = status + " <M>Mouse:"+mouse+" position: "+str(mousex)+","+str(mousey)
    label = pyglet.text.Label(status,
                        font_name='Kenvector Future Thin',
                        font_size=10,
                        x=0, y=window.height-11
                    )
    label.draw()
    for boid in boids.boids:
        boid.draw()

def init():
    global boids
    boids = Boids()

def get_mouse(x,y,dx,dy):
    global mousex
    global mousey
    global mouse
    mousex = x
    mousey = y

def key_pressed(key, mod):
    global pressed_keys
    global paused
    global GROUPING
    global SPACING
    global mouse
    if key == pyglet.window.key.SPACE:
        if paused:
            paused = False
        else:
            paused = True
    if key == pyglet.window.key.S:
        if SPACING:
            SPACING = False
        else:
            SPACING = True
    if key == pyglet.window.key.G:
        if GROUPING:
            GROUPING = False
        else:
            GROUPING = True
    if key == pyglet.window.key.M:
        if mouse == 'None':
            mouse = 'Follow' 
        elif mouse == 'Follow':
            mouse = 'Fear'
        else:
            mouse = 'None'
    if key == pyglet.window.key.R:
        init()
init()
pyglet.clock.schedule_interval(tick,1/25)
window.push_handlers(
    on_draw=draw,
    on_key_press=key_pressed,
    on_mouse_motion=get_mouse
)
pyglet.app.run()
