#version 330 core

uniform sampler2D uTex;

in vec2 vUV;

void main() {
    if (texture(uTex, vUV).a < 0.5)
    {
        discard;
    }
}