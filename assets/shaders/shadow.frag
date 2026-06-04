#version 330 core

uniform sampler2D tex;

in vec2 uv;

void main() {
    if (texture(tex, uv).a < 0.5)
    {
        discard;
    }
}