#version 400

in vec2 UV;
out vec4 fragColor;

uniform float Zoom;
uniform float Time;
uniform float CloudMinRadius;
uniform float CloudMaxRadius;
uniform float CloudHeight;
uniform float CloudDensity;
uniform float StepSize;
uniform float MaxSteps;

uniform vec2 FOV;
uniform vec2 WinRes;
uniform vec3 CamDir;
uniform vec3 CamPos;
uniform vec3 LightPos;
uniform vec3 LightColor;
uniform sampler2D Sampler0;
uniform samplerCube Sampler1;

const float PI = 3.14159;
struct object {
    vec3 pos;
    float radius;
    float gravity;
    vec3 color;
    float density;
};
const int NUM_OBJECTS = 1;
object objects[NUM_OBJECTS];

// Camera forward from yaw/pitch
float yaw   = CamDir.x;
float pitch = CamDir.y;
float roll  = CamDir.z;

vec3 F = normalize(vec3(
    cos(yaw) * cos(pitch),
    sin(pitch),
    sin(yaw) * cos(pitch)
));

// Build initial camera basis
vec3 worldUp = vec3(0.0, 1.0, 0.0);
vec3 R = normalize(cross(F, worldUp));   // right
vec3 U = normalize(cross(R, F));         // up

// Rotate basis vectors around F by roll
float c = cos(roll);
float s = sin(roll);
vec3 Rr = c * R + s * U;   // rolled right
vec3 Ur = -s * R + c * U;  // rolled up

// Map pixel to NDC ([-1,1]) and use focal lengths via tan(FOV/2)
vec2 ndc = UV * 2.0 - 1.0;
float tanX = tan(0.5 * (FOV.x / Zoom));
float tanY = tan(0.5 * (FOV.y / Zoom));

// Build pinhole ray
vec3 dir = normalize(F + ndc.x * tanX * Rr + ndc.y * tanY * Ur);



void main() {
    // Objects
    objects[0] = object(vec3(0.0, 0.0, 0.0), 4.0, 3.6, vec3(0.0, 0.0, 0.0), 1.0);

    vec3 color = vec3(0.0);

    vec3 ray_pos = CamPos;
    vec3 ray_vel = dir;
    vec4 ray_col = vec4(0.0);
    vec3 old_pos = ray_pos;
    float light_strength = 0.0;
    for (int i = 0; i < MaxSteps; i++) {
        for (int o = 0; o < NUM_OBJECTS; o++) {
            // Calculate distance
            object obj = objects[o];
            vec3 to_obj = obj.pos - ray_pos;
            float dist_sq = dot(to_obj, to_obj);
            float dist = sqrt(dist_sq);

            if (dist < obj.radius) {
                ray_col = vec4(mix(obj.color, ray_col.rgb, ray_col.a), obj.density);
            }

            // Apply gravity
            float force = (obj.gravity) / (dist_sq + 1.0);
            ray_vel += normalize(to_obj) * force * StepSize;
        }

        ray_pos += ray_vel*StepSize;
        
        float r = length(ray_pos.xz);
        float omega = 5.0 / sqrt(r + 0.01);
        float theta = atan(ray_pos.z, ray_pos.x) + (Time*0.2+3.0) * omega;
        vec2 uv = vec2(theta / (2.0*PI), r / CloudMaxRadius);

        // Sample density
        float texVal = 4.0*clamp(texture(Sampler0, uv).r, 0.0, 1.0);
        float verticalFade = smoothstep(CloudHeight, CloudHeight*0.01, abs(ray_pos.y));
        float radialFade = smoothstep(CloudMinRadius, CloudMinRadius+1.0, r) * (1.0 - smoothstep(CloudMaxRadius-1.0, CloudMaxRadius, r));
        float falloff = clamp(2.4*sin(PI*(r-CloudMinRadius)/(CloudMaxRadius-4.0-CloudMinRadius)), 0.0, 1.0);
        float density = verticalFade * radialFade * CloudDensity * falloff;

        // Skip if empty
        if (density > 0.001) {
            // Attenuation (1 / distance² falloff)
            float dist2 = dot(LightPos - ray_pos, LightPos - ray_pos);
            float atten = 4.0 / (max(dist2, 0.02) * 0.1);

            // Scattering contribution
            vec3 scatterColor = LightColor * atten * density * StepSize;

            // Accumulate with transmittance
            ray_col.rgb += (1.0 - ray_col.a) * scatterColor * texVal;
            ray_col.a += density * StepSize;

            // Early exit if opaque
            if (ray_col.a > 0.95) break;
        }

    }

    vec4 skybox = texture(Sampler1, normalize(ray_vel));
    fragColor = vec4(mix(ray_col.rgb, skybox.rgb, 1.0-ray_col.a), 1.0);
}
