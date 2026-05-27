#version 330 core

in vec3 in_pos;

uniform mat4 model;
uniform mat4 light_space;

void main() {
    gl_Position = light_space * model * vec4(in_pos, 1.0);
}