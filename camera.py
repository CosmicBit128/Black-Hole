from settings import *


class Camera:
    def __init__(self, pos, yaw, pitch, roll):
        self.position = glm.vec3(pos)
        self.yaw = glm.radians(yaw)
        self.pitch = glm.radians(pitch)
        self.roll = glm.radians(roll)

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.dir = glm.vec3(0, 0, -1)

        self.projMat = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.modelViewMat = glm.mat4()

    def update(self):
        self.update_vectors()
        self.update_view_matrix()

    def update_view_matrix(self):
        self.modelViewMat = glm.lookAt(self.position, self.position + self.dir, self.up)

    def update_vectors(self):
        self.dir.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.dir.y = glm.sin(self.pitch)
        self.dir.z = glm.sin(self.yaw) * glm.cos(self.pitch)

        self.forward.x = glm.cos(self.yaw)
        self.forward.y = 0
        self.forward.z = glm.sin(self.yaw)

        self.dir = glm.normalize(self.dir)
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_left(self, velocity):
        self.position -= self.right * velocity

    def move_right(self, velocity):
        self.position += self.right * velocity

    def move_up(self, velocity):
        self.position += self.up * velocity

    def move_down(self, velocity):
        self.position -= self.up * velocity

    def move_forward(self, velocity):
        self.position += self.forward * velocity

    def move_back(self, velocity):
        self.position -= self.forward * velocity