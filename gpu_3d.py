from settings import *
import moderngl as mgl
from PIL import Image
import pygame as pg
import subprocess
#from program import ShaderProgram
#from scene import Scene
from player import Player
from post import PostProcess


class Renderer:
    def __init__(self, win_res, framerate: float = 60.0):
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 0)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

        pg.display.set_mode(win_res, flags=FLAGS)
        self.ctx = mgl.create_context()

        self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.font = pg.font.Font('acme_7.ttf', 21)
        self.music = pg.mixer.Sound('res/ObservingTheStar.mp3') # Credit: https://opengameart.org/content/another-space-background-track
        self.fps = framerate

        # Time
        self.clock = pg.time.Clock()
        self.time = 0
        self.dt = 0
        self.record = False

        # Setup modules
        self.on_init()

    def on_init(self):
        self.player = Player(self)
        #self.shader_program = ShaderProgram(self) # 17.3 1.2 3.3  ||  3.74 0 0
        self.post = PostProcess(self)
        self.player.rotate = not self.player.rotate

        if self.record:
            self.ffmpeg = subprocess.Popen([
                'ffmpeg', '-y',
                '-f', 'rawvideo',
                '-pixel_format', 'rgb24',
                '-video_size', f'{int(WIN_RES.x*SCALING)}x{int(WIN_RES.y*SCALING)}',
                '-framerate', f'{self.fps}',
                '-i', '-', '-c:v', 'libx264', 'blackhole11.mp4'
            ], stdin=subprocess.PIPE)

    def update(self):
        self.player.update()
        #self.shader_program.update()

        self.dt = self.clock.tick(0)
        self.time += 1/self.fps # pg.time.get_ticks()*0.001

    def render(self):
        self.post.render()
        pg.display.flip()

    def events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                if self.record:
                    self.ffmpeg.stdin.close()   # tell ffmpeg no more frames are coming
                    self.ffmpeg.wait()          # wait for ffmpeg to finalize the file
                pg.quit()
                raise SystemExit(0)
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.mouse.set_pos(self.player.scr_center)
                    pg.mouse.set_visible(self.player.rotate)
                    self.player.rotate = not self.player.rotate
            
    def run(self):
        self.music.play(-1)
        while True:
            self.events()
            self.update()
            self.render()

    def create_mgl_texture_from_surface(self, surface):
        surf_data = pg.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()
        texture = self.ctx.texture((width, height), 4, data=surf_data)
        texture.build_mipmaps()
        texture.filter = (mgl.LINEAR, mgl.LINEAR)
        texture.repeat_x = False
        texture.repeat_y = False
        return texture, width, height

    def load_texture(self, ctx, path):
        img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
        return ctx.texture(img.size, 3, img.convert('RGB').tobytes())

    def load_texture_cube(self, ctx, folder):
        faces = ['right', 'left', 'bottom', 'top', 'front', 'back']
        imgs = [Image.open(f'{folder}/{name}.png').transpose(Image.FLIP_TOP_BOTTOM) for name in faces]
        size = imgs[0].size
        tex_cube = ctx.texture_cube(size, 3, None)

        for i, img in enumerate(imgs):
            data = img.convert('RGB').tobytes()
            tex_cube.write(face=i, data=data)

        tex_cube.build_mipmaps()
        #tex_cube.use(location=0)  # Bind to texture unit 0
        return tex_cube

if __name__ == '__main__':
    eng = Renderer(WIN_RES, 60.0)
    eng.run()