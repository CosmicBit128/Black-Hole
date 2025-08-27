#version 400

in vec2 UV;
out vec4 fragColor;

uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform vec2 TextPos;
uniform vec2 TextSize;
uniform vec2 ScreenSize;

void main() {
    vec2 uv = UV;
    vec4 scene_color = texture(Sampler0, uv);

    vec2 screen_uv = uv * ScreenSize;

    // check if inside FPS rect
    vec2 rel = screen_uv - TextPos;
    if (rel.x >= 0.0 && rel.x < TextSize.x && rel.y >= 0.0 && rel.y < TextSize.y) {
        vec2 fps_uv = rel / TextSize;
        vec4 fps_color = texture(Sampler1, fps_uv);
        fragColor = mix(scene_color, fps_color, fps_color.a);
    } else {
        fragColor = scene_color;
    }
}
