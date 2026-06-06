#version 330 core

in vec2 uv;

out vec4 color;

uniform sampler2D tex;

void main()
{
    color = texture(tex, uv);
    if (color.a < 0.5)
    {
        discard;
    }
}