#version 330 core

layout(location = 0) in vec3 aPos;

out vec3 vDir;

uniform mat4 uView;
uniform mat4 uProj;

void main() {
    vDir = aPos;

    mat4 rotView = mat4(mat3(uView));

    vec4 pos = uProj * rotView * vec4(aPos, 1.0);
    gl_Position = pos.xyww;
}