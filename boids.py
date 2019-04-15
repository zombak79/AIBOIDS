import pyglet
import random
import math
from pyglet import gl

WIDTH = 1024
HEIGHT = 768

BOID_RADIUS = 8
BOID_COUNT = 50
BOID_SPEED = 5
MAX_SPEED = 10

DESIRED_DISTANCE = 20
EYESIGHT_RADIUS = 200

SPACING = True
GROUPING = True

INERTIA = 0.25
LOCAL_PART = 0.25
GLOBAL_PART = 0.5


COHESION_FACTOR = 0.01
SEPARATION_FACTOR = 0.1
ALIGNMENT_FACTOR = 0.6


window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

paused = False


class Boid:
    def __init__(self,id=0):
        #init boid randomly
        self.id=id
        self.r = BOID_RADIUS
        self.x = random.randint(0+BOID_RADIUS,WIDTH-BOID_RADIUS)
        self.y = random.randint(0+BOID_RADIUS,HEIGHT-BOID_RADIUS)
        self.vx = 0
        self.vy = 0
        self.vx = random.randint(-1*MAX_SPEED,1*MAX_SPEED)
        self.vy = random.randint(-1*MAX_SPEED,1*MAX_SPEED)
        # self.vx = random.randint(-1*0,1*MAX_SPEED)
        # self.vy = random.randint(-1*0,1*MAX_SPEED)
        self.lx = 0
        self.ly = 0
        self.gx = 0
        self.gy = 0
        self.top_speed = 0.01
        self.cx = 0 
        self.cy = 0
        self.sx = 0 
        self.sy = 0
        self.ax = 0 
        self.ay = 0

    def draw(self):
        #draw boid
        self.circle(self.x,self.y,self.r)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (self.x, self.y, self.x+int(self.vx), self.y+int(self.vy))))

    def circle(self, x, y, radius):
        iterations = 20
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
            # koef = (float(speed)/float(self.top_speed))*float(MAX_SPEED)
            # #print(self.vx,self.vy,speed,self.top_speed,koef)
            # desired_speed = speed * koef
            
            # koef = speed/desired_speed
            # #print(self.vx,self.vy,speed,self.top_speed,koef)
            # self.vx = self.vx*koef
            # self.vy = self.vy*koef

    
    def set_new_v(self):
        #calc new (vx,vy)
        self.vx = self.vx*INERTIA + LOCAL_PART*self.lx + GLOBAL_PART*self.gx
        self.vy = self.vy*INERTIA + LOCAL_PART*self.ly + GLOBAL_PART*self.gy

    def distance(self,boid):
        return math.sqrt(((self.x-boid.x)**2)+((self.y-boid.y)**2))

    #http://www.vergenet.net/~conrad/boids/pseudocode.html
    #Rule 1: Boids try to fly towards the centre of mass of neighbouring boids. (cohesion)
    def cohesion(self,boids):
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
            x=(x/count-self.x)*COHESION_FACTOR
            y=(y/count-self.y)*COHESION_FACTOR
        else:
            x=0
            y=0

        self.cx = x
        self.cy = y


    #Rule 2: Boids try to keep a small distance away from other objects (including other boids). (separation)
    def separation(self,boids):
        count = 0
        x=0
        y=0
        for neighbour in boids.boids:
            if not self.id == neighbour.id:
                if self.distance(neighbour)<DESIRED_DISTANCE:
                    x=x-(neighbour.x-self.x)
                    y=y-(neighbour.y-self.y)
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


    def tick(self):
        self.vx+=self.ax+self.sx+self.cx 
        self.vy+=self.ay+self.sy+self.cy
        #trunc (vx,vy)
        # self.vx = int(self.vx)
        # self.vy = int(self.vy)
        #move boid in (vx,vy) direction
        if self.get_speed()>MAX_SPEED:
            self.set_speed()
        self.x += int(self.vx)
        self.y += int(self.vy)
        if self.x > WIDTH:
            self.x -= WIDTH
        if self.y>HEIGHT:
            self.y -= HEIGHT 
        if self.x<0:
            self.x += WIDTH
        if self.y<0:
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
        maxv = 0
        if not paused:
            #iterate all boids for actions with neighbours (local behavior)
            # for evaluated in range(0,len(self.boids)):
            #     tx = 0
            #     ty = 0
            #     cnt = 1
                
            #     for neighbour in range(0,len(self.boids)):
            #         if not evaluated == neighbour:
            #             distance = math.sqrt(((self.boids[neighbour].x-self.boids[evaluated].x)**2)+((self.boids[neighbour].y-self.boids[evaluated].y)**2))
            #             if distance == 0:
            #                 distance = 1
            #             if distance<DESIRED_DISTANCE and SPACING:
            #                 ax = -(self.boids[neighbour].x-self.boids[evaluated].x)/distance
            #                 ay = -(self.boids[neighbour].y-self.boids[evaluated].y)/distance
            #                 self.boids[evaluated].lx += ax*BOID_SPEED
            #                 self.boids[evaluated].ly += ay*BOID_SPEED
            #             if distance<EYESIGHT_RADIUS and GROUPING:
            #                 ax = (self.boids[neighbour].x-self.boids[evaluated].x)/distance
            #                 ay = (self.boids[neighbour].y-self.boids[evaluated].y)/distance
            #                 self.boids[evaluated].lx += ax*BOID_SPEED
            #                 self.boids[evaluated].ly += ay*BOID_SPEED
            #             if distance<EYESIGHT_RADIUS:
            #                 tx += self.boids[neighbour].vx
            #                 ty += self.boids[neighbour].vy
            #                 cnt += 1
            #     self.boids[evaluated].gx = tx/cnt
            #     self.boids[evaluated].gy = ty/cnt
            #     self.boids[evaluated].set_new_v()
            #     if self.boids[evaluated].get_speed()>maxv:
            #         maxv = self.boids[evaluated].get_speed()
            #     #print(maxv,self.boids[evaluated].get_speed())    
            # # print((tx/(len(self.boids)+1),ty/(len(self.boids)+1)))    
            # for boid in self.boids:
            #     boid.top_speed = maxv                


            #move all boids
            for boid in self.boids:
                boid.cohesion(self)
                boid.separation(self)
                boid.alignment(self)
                boid.tick()



boids = Boids()
pressed_keys = []


def tick(td):
    boids.tick()
        
    
def draw():
    window.clear()
    for boid in boids.boids:
        boid.draw()


def init():
    global boids
    boids = Boids()
    maxv = 0
    for boid in boids.boids:
        if boid.get_speed()>maxv:
            maxv = boid.get_speed()

    for boid in boids.boids:
        boid.top_speed = maxv

def key_pressed(key, mod):
    global pressed_keys
    global paused
    if key == pyglet.window.key.SPACE:
        if paused:
            paused = False
        else:
            paused = True
    

init()
pyglet.clock.schedule_interval(tick,1/30)
window.push_handlers(
    on_draw=draw,
    on_key_press=key_pressed,
    #on_key_release=key_released,
    #on_resize=lambda w, h: print(w, h),
)

pyglet.app.run()
