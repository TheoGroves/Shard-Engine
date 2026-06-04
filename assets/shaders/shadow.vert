#version 330 core

in vec3 in_pos;
in vec2 in_uv_map;

out vec2 uv;

uniform mat4 model;
uniform mat4 light_space;

void main() {
    uv = in_uv_map;
    gl_Position = light_space * model * vec4(in_pos, 1.0);
}