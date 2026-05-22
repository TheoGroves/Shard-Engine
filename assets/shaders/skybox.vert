#version 330 core

in vec3 in_pos;

out vec3 dir;

uniform mat4 view;
uniform mat4 proj;

void main() {
    dir = in_pos;

    mat4 rotView = mat4(mat3(view));

    vec4 pos = proj * rotView * vec4(in_pos, 1.0);
    gl_Position = pos.xyww;
}