#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aUV;

out vec2 vUV;

uniform mat4 uModel;
uniform mat4 uLightSpace;

void main() {
    vUV = aUV;
    gl_Position = uLightSpace * uModel * vec4(aPos, 1.0);
}