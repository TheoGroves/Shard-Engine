#version 330 core

uniform sampler2D tex;
uniform sampler2D normal_map;

in mat3 TBN;
in vec2 uv;

out vec4 color;

void main()
{
    vec4 tex = texture(tex, uv).rgba;
    if (tex.a < 0.5)
    {
        discard;
    }
    vec3 nMap = texture(normal_map, uv).rgb;
    nMap = nMap * 2.0 - 1.0;

    vec3 n = normalize(TBN * nMap);

    color = vec4(n * 0.5 + 0.5, 1.0);
}