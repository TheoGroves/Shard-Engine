#version 330 core

in vec3 dir;
out vec4 color;

uniform sampler2D env_map;

void main() {
    vec3 d = normalize(dir);

    vec2 uv;
    uv.x = atan(d.z, d.x) / (2.0 * 3.14159265) + 0.5;
    uv.y = asin(d.y) / 3.14159265 + 0.5;

    float exposure = 2.5;
    vec3 env = texture(env_map, uv).rgb;
    env = vec3(1.0) - exp(-env * exposure);
    color = vec4(env, 1.0);
}