#version 330 core

in vec2 uv;

out vec4 color;

uniform sampler2D tex;
uniform float brightness;

void main()
{
    vec4 tex = texture(tex, uv);
    color = vec4(tex.rgb*brightness, tex.a);
}