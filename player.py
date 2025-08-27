import pygame as pg
from camera import Camera
from settings import *


class Player(Camera):
    def __init__(self, app, pos=PLAYER_POS, yaw=YAW, pitch=PITCH, roll=ROLL):
        self.app = app
        self.rotate = True
        self.zoom = 1
        self.scr_center = WIN_RES/2

        # Used for animation
        self.mov = (0, 0, 0)
        self.rot = (0, 0, 0)
        super().__init__(pos, yaw, pitch, roll)

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        self.position += self.mov
        self.yaw += self.rot[0]
        self.pitch += self.rot[1]
        self.roll += self.rot[2]
        self.ddir = glm.vec3(self.yaw, self.pitch, self.roll)
        super().update()

    def mouse_control(self):
        if self.rotate:
            mpos = pg.mouse.get_pos()
            dx = mpos[0] - self.scr_center.x
            dy = mpos[1] - self.scr_center.y

            if dx:
                self.rotate_yaw(delta_x=dx * MOUSE_SENSITIVITY)
            if dy:
                self.rotate_pitch(delta_y=dy * MOUSE_SENSITIVITY)
            pg.mouse.set_pos(self.scr_center)
            # dx, dy = pg.mouse.get_rel()
            # if dx:
            #     self.rotate_yaw(delta_x=dx * MOUSE_SENSITIVITY)
            # if dy:
            #     self.rotate_pitch(delta_y=dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED# * self.app.dt
        if key_state[pg.K_w]:
            self.move_forward(vel)
        if key_state[pg.K_s]:
            self.move_back(vel)
        if key_state[pg.K_d]:
            self.move_right(vel)
        if key_state[pg.K_a]:
            self.move_left(vel)
        if key_state[pg.K_SPACE]:
            self.move_up(vel)
        if key_state[pg.K_LSHIFT]:
            self.move_down(vel)

        if key_state[pg.K_LEFT]:
            self.roll += 0.01
        if key_state[pg.K_RIGHT]:
            self.roll -= 0.01

        if key_state[pg.K_c]:
            self.zoom = 4
        else:
            self.zoom = 1