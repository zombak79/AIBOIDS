import pyglet
import random
import math
from pyglet import gl

WIDTH = 800
HEIGHT = 600

BOID_RADIUS = 10
BOID_COUNT = 20

window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

boids = []

class Boid:
    def __init__(self):
        self.r = BOID_RADIUS
        self.x = random.randint(0+BOID_RADIUS,WIDTH-BOID_RADIUS)
        self.y = random.randint(0+BOID_RADIUS,HEIGHT-BOID_RADIUS)
        self.vx = random.randint(-20,20)
        self.vy = random.randint(-20,20)

    def draw(self):
        self.circle(self.x,self.y,self.r)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (self.x, self.y, self.x+self.vx, self.y+self.vy)))

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



def tick(td):
    pass

def draw():
    window.clear()
    for boid in boids:
        boid.draw()


def init():
    for i in range(0,BOID_COUNT):
        boid = Boid()
        boids.append(boid)


init()
pyglet.clock.schedule_interval(tick,1/20)
window.push_handlers(
    on_draw=draw,
    #on_key_press=pgsnk.key_pressed,
    #on_key_release=pgsnk.key_released,
    #on_resize=lambda w, h: print(w, h),
)

pyglet.app.run()
