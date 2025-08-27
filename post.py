from moderngl import TRIANGLE_STRIP
from settings import *
from PIL import Image
import numpy as np
import json
import glm


class PostProcess:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.font = app.font
        self.r = 64
        self.s = 0.02
        self.text = True


        # Textures
        self.halo = self.app.load_texture(self.ctx, 'res/accretion_disc.png')
        self.skybox = self.app.load_texture_cube(self.ctx, 'res/skybox')

        # Text
        pos = self.app.player.position
        self.generate_text(f"FPS: {self.app.clock.get_fps():.2f} | Pos: {pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f} | Rot: {self.app.player.yaw:.2f}, {self.app.player.pitch:.2f}")

        # Setup framebuffer
        self.post_fbo_texture = self.ctx.texture((int(WIN_RES.x)//SCALING, int(WIN_RES.y)//SCALING), 4)
        self.post_fbo = self.ctx.framebuffer(
            color_attachments=[self.post_fbo_texture]
        )

        # Post-Processing Render Passes
        self.passes = {
            'raytracing': [],
            'text': []
        }

        self.quad_vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0
        ], dtype='f4')

        self.quad_buffer = self.ctx.buffer(self.quad_vertices.tobytes())

        for post in self.passes.keys():
            prog = self.get_program(post)
            uniforms = self.get_uniforms(post)
            vao = self.ctx.simple_vertex_array(prog, self.quad_buffer, 'Position')

            self.passes[post] = [prog, uniforms, self.quad_buffer, vao]

        self.set_uniforms_on_init()

    def render(self):
        # 1. Ray Tracing pass -> to offscreen FBO
        raytracing_pass = self.passes['raytracing']
        prog, uniforms, _, vao = raytracing_pass

        # Set uniforms before rendering
        for k, v in uniforms['update']['write'].items():
            prog[k].write(eval(v))
        for k, v in uniforms['update']['value'].items():
            prog[k].value = eval(v)

        self.halo.use(0)
        self.skybox.use(1)

        self.post_fbo.use()
        self.post_fbo.clear(color=BG_COLOR)
        vao.render(TRIANGLE_STRIP)

        # Send rendered frame to ffmpeg stream
        if self.app.record:
            pixels = self.post_fbo.read(components=3, alignment=1)
            img = Image.frombytes("RGB", (int(WIN_RES.x*SCALING), int(WIN_RES.y*SCALING)), pixels)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            self.app.ffmpeg.stdin.write(img.tobytes())
        # 2. Text pass → using result of FBO → to screen
        text_pass = self.passes['text']
        prog, uniforms, _, vao = text_pass

        # Bind FBO texture to sampler
        self.ctx.screen.use()
        self.ctx.clear(color=BG_COLOR)

        pos = self.app.player.position
        rot = self.app.player.ddir
        self.generate_text(f"FPS: {self.app.clock.get_fps():.2f} | Pos: {pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f} | Rot: {rot.x:.2f}, {rot.y:.2f}, {rot.z:.2f}")

        self.post_fbo_texture.use(location=0)
        if self.text: self.text_texture.use(location=1)

        # Set text pass uniforms
        for k, v in uniforms['update']['write'].items():
            prog[k].write(eval(v))
        for k, v in uniforms['update']['value'].items():
            prog[k].value = eval(v)

        vao.render(TRIANGLE_STRIP)

    def generate_text(self, text: str):
        fps_surface = self.font.render(text, True, (255, 255, 255))
        self.text_size = [0, 0]
        self.text_texture, self.text_size[0], self.text_size[1] = self.app.create_mgl_texture_from_surface(fps_surface)

    def set_uniforms_on_init(self):
        for shader in self.passes.keys():
            for k, v in self.passes[shader][1]['init']['write'].items():
                self.passes[shader][0][k].write(eval(v))

            for k, v in self.passes[shader][1]['init']['value'].items():
                self.passes[shader][0][k].value = eval(v)

    def get_uniforms(self, name):
        with open(f'shaders/post/{name}.json', 'r') as f:
            data = json.load(f)
        for k, v in data['update']['value'].items():
            if isinstance(data['update']['value'][k], (list, tuple)):
                data['update']['value'][k] = [float(i) for i in v]
        return data
    
    def get_program(self, shader_name):
        with open(f'shaders/post/screen.vsh') as file:
            vertex_shader = file.read()
        with open(f'shaders/post/{shader_name}.fsh') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program