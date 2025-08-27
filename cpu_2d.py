import pygame as pg
import numpy as np
import glm

pg.init()

win_res = glm.vec2(1280, 720)
win = pg.display.set_mode(win_res)
clock = pg.time.Clock()

steps = 0
num = 64
speed = 1
fov = glm.radians(96)
cam_pos = glm.vec2(0, win_res[1]//2)
angles = np.linspace(-fov/2, fov/2, num)
vels = [(speed*glm.cos(ang), speed*glm.sin(ang)) for ang in angles]
rays = [(cam_pos, vels[i]) for i in range(num)]
last = rays

objects = [
    # pos, radius, gravity, color
    ((win_res.x*2, win_res.y//2), 48, 48, '#ff00ff'),
    ((2*win_res.x//3, win_res.y//2), 24, 0, '#00ffff')
]

while True:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            raise SystemExit(0)
        
    dt = clock.tick(60)
        
    last = rays
    new_rays = []
    out = []
    for i, (pos, vel) in enumerate(rays):
        pos = glm.vec2(pos)
        vel = glm.vec2(vel)
        for obj in objects:
            # Calculate distance
            dx = obj[0][0] - pos[0]
            dy = obj[0][1] - pos[1]
            dist_sq = dx*dx + dy*dy
            dist = glm.sqrt(dist_sq)

            # Absorb Rays
            if dist < obj[1] or steps > 1024:
                out.append((i, obj[3]))
                break

            # Apply Gravity
            force = (obj[2]*speed) / (dist_sq + 1)
            ax = force * dx / dist
            ay = force * dy / dist

            vel += (ax*dt, ay*dt)
            pos += vel
        
        new_rays.append((pos, vel))

    for i, (index, _) in enumerate(out):
        rays.pop(index-i)
        new_rays.pop(index-i)
    last = rays
    rays = new_rays
    steps += 1

    for i in range(len(rays)):
        pg.draw.line(win, '#ff0000', rays[i][0], last[i][0], 2)
    for obj in objects:
        pg.draw.circle(win, obj[3], obj[0], obj[1])

    pg.display.flip()