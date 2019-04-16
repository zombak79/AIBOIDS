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

DESIRED_DISTANCE = 30
EYESIGHT_RADIUS = 200

SPACING = True
GROUPING = True

COHESION_FACTOR = 0.01
SEPARATION_FACTOR = 0.1
ALIGNMENT_FACTOR = 0.6

MOUSE_COHESION_FACTOR = 0.9
MOUSE_SEPARATION_FACTOR = 0.9

BRICKS_COHESION_FACTOR = 0.9
BRICKS_SEPARATION_FACTOR = 0.9

window = pyglet.window.Window(width=WIDTH, height=HEIGHT+20)

paused = False
mousex = WIDTH/2
mousey = HEIGHT/2
mouse = 'None'

blue = ('c3f', (0, 0, 255)*4)
red = ('c3f', (255, 0, 0)*4)

class Rect:
  #class for drawing bricks
  #source https://stackoverflow.com/questions/26808513/drawing-a-rectangle-around-mouse-drag-pyglet/49257192#49257192   
  def __init__(self, x, y, w, h):
    self.set(x, y, w, h)

  def draw(self,color):
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self._quad,color)
    

  def set(self, x=None, y=None, w=None, h=None):
    self._x = self._x if x is None else x
    self._y = self._y if y is None else y
    self._w = self._w if w is None else w
    self._h = self._h if h is None else h
    self._quad = ('v2f', (self._x, self._y,
                          self._x + self._w, self._y,
                          self._x + self._w, self._y + self._h,
                          self._x, self._y + self._h)
                        )
 
  def __repr__(self):
      return f"Rect(x={self._x}, y={self._y}, w={self._w}, h={self._h})"

class Boid:
    def __init__(self,id=0):
        #init boid randomly
        self.kind = 'Boid'
        self.id=id
        self.r = BOID_RADIUS
        #random position
        self.x = random.randint(0+BOID_RADIUS,WIDTH-BOID_RADIUS) + OFFSET
        self.y = random.randint(0+BOID_RADIUS,HEIGHT-BOID_RADIUS) + OFFSET
        #random speed vector
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
        #bricks separation vector
        self.bsx = 0 
        self.bsy = 0
        #bricks cohesion vector
        self.bcx = 0 
        self.bcy = 0
        
    def draw(self):
        #draw boid
        self.circle(self.x-OFFSET,self.y-OFFSET,self.r)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (self.x-OFFSET, self.y-OFFSET, self.x-OFFSET+int(self.vx), self.y-OFFSET+int(self.vy))))
        
    def circle(self, x, y, radius):
        #procedure for drawing boid
        #source: https://naucse.python.cz/course/pyladies/projects/asteroids/
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
        #distance between two objects, counts with position in edges of screen
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
        return distance

    #rules for movement
    #source: http://www.vergenet.net/~conrad/boids/pseudocode.html by Conrad Parker, 1995
    
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
                if self.distance(neighbour)<EYESIGHT_RADIUS:
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
    #Rule 4: Boids follow mouse
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
        if mouse == 'None':
            self.mx=0
            self.my=0

    #Rule 5: Boids fear mouse
    def mouse_fear(self):
        global mouse
        global mousex
        global mousey
        mouseboid = Boid()
        mouseboid.x=mousex+OFFSET
        mouseboid.y=mousey+OFFSET

        if mouse == 'Fear':
            if self.distance(mouseboid)<EYESIGHT_RADIUS:
                self.mx=-(mouseboid.x-self.ix)*MOUSE_SEPARATION_FACTOR
                self.my=-(mouseboid.y-self.iy)*MOUSE_SEPARATION_FACTOR
            else:
                self.mx=0
                self.my=0
        if mouse == 'None':
            self.mx=0
            self.my=0
    
    #6 - fear red bricks
    def bricks_fear(self,bricks):
        x=0
        y=0
        for brick in bricks.bricks:
            if brick.kind == 'Fear':
                if self.distance(brick)<EYESIGHT_RADIUS:
                    x=x-(brick.x-self.ix)
                    y=x-(brick.y-self.iy)
        self.bsx = x*BRICKS_SEPARATION_FACTOR
        self.bsy = y*BRICKS_SEPARATION_FACTOR
    
    
    #7 - folow blue bricks
    def bricks_follow(self,bricks):
        x=0
        y=0
        count=0
        for brick in bricks.bricks:
            if brick.kind == 'Follow':
                if self.distance(brick)<EYESIGHT_RADIUS:
                    x=x+(brick.x-self.ix)
                    y=y+(brick.y-self.iy)
                    count+=1
        if count == 0:
            self.bcx = 0
            self.bcy = 0
        else:
            self.bcx = (x/count)*BRICKS_COHESION_FACTOR
            self.bcy = (y/count)*BRICKS_COHESION_FACTOR
    
    def tick(self):
        #calculate new speed vector
        self.vx+=self.ax+self.sx+self.cx+self.mx+self.bsx+self.bcx
        self.vy+=self.ay+self.sy+self.cy+self.my+self.bsy+self.bcy
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


class Brick(Boid):
    def __init__(self,x,y,kind):
        #init Brick
        self.kind = kind
        self.x = x+OFFSET
        self.y = y+OFFSET

    def draw(self):
        #draw brick
        r1 = Rect((self.x-OFFSET)-BOID_RADIUS,(self.y-OFFSET)-BOID_RADIUS,2*BOID_RADIUS,2*BOID_RADIUS)
        if self.kind=='Follow':
            r1.draw(blue)
        if self.kind=='Fear':
            r1.draw(red)
        return

    def tick(self):
        #do nothing - bricks are static objects which does not move
        return

class Boids:
    def __init__(self):
        #init new set of boids
        self.boids = []
        self.bricks = [] 
        for i in range(0,BOID_COUNT):
            boid = Boid(i)
            self.boids.append(boid)
    
    def add_brick(self,x,y,kind):
        if kind=='None':
            return
        brick = Brick(x,y,kind)
        self.bricks.append(brick)

    def tick(self):
        global paused
        if not paused:
            #move all boids
            for boid in self.boids:
                #apply all rules
                boid.cohesion(self)
                boid.separation(self)
                boid.alignment(self)
                boid.mouse_follow()
                boid.mouse_fear()
                boid.bricks_fear(self)
                boid.bricks_follow(self)
                #move boid
                boid.tick()

#global variable for all boids objects
boids = Boids()
#global procedures
def tick(td):
    boids.tick()
    
def draw():
    global mousex
    global mousey
    global mouse
    window.clear()
    #draw status label
    status = "<R>Restart simulation <SPACE>paused:"+str(paused)+" <G>Grouping:"+str(GROUPING)+" <S>Spacing:"+str(SPACING)
    status = status + " <M>Mouse:"+mouse+" position: "+str(mousex)+","+str(mousey)
    status = status + " <D>Delete all bricks"
    if not mouse == 'None':
        status = status + ' - click mouse to lay brick :)'
    label = pyglet.text.Label(status,
                        font_name='Kenvector Future Thin',
                        font_size=10,
                        x=0, y=window.height-11
                    )
    label.draw()
    #draw all bricks
    for brick in boids.bricks:
        brick.draw()
    #draw all boids
    for boid in boids.boids:
        boid.draw()
    
def init():
    global boids
    boids = Boids()

def mouse_click(x, y, button, modifiers):
    global boids
    global mouse
    if button==pyglet.window.mouse.LEFT:
        boids.add_brick(x,y,mouse)

def get_mouse(x,y,dx,dy):
    global mousex
    global mousey
    global mouse
    mousex = x
    mousey = y

def key_pressed(key, mod):
    global paused
    global GROUPING
    global SPACING
    global mouse
    global boids

    #SPACE - pause simulation
    if key == pyglet.window.key.SPACE:
        if paused:
            paused = False
        else:
            paused = True
    #S - spacing on/off
    if key == pyglet.window.key.S:
        if SPACING:
            SPACING = False
        else:
            SPACING = True
    #G - grouping on/off
    if key == pyglet.window.key.G:
        if GROUPING:
            GROUPING = False
        else:
            GROUPING = True
    #M - switch mouse behaviour
    if key == pyglet.window.key.M:
        if mouse == 'None':
            mouse = 'Follow' 
        elif mouse == 'Follow':
            mouse = 'Fear'
        else:
            mouse = 'None'
    #D - delete all bricks        
    if key == pyglet.window.key.D:
        boids.bricks=[]
    #R - restart simulation
    if key == pyglet.window.key.R:
        init()

#start simulation
init()
pyglet.clock.schedule_interval(tick,1/25)
window.push_handlers(
    on_draw=draw,
    on_key_press=key_pressed,
    on_mouse_motion=get_mouse,
    on_mouse_press=mouse_click
)
pyglet.app.run()
