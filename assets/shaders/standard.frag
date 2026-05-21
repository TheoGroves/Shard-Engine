#version 330 core

uniform sampler2D tex;
uniform sampler2D normal_map;

uniform vec3 light_dir;
uniform vec3 cam_pos;
uniform float roughness;

in mat3 TBN;
in mat4 out_model;
in vec3 fragPos;
in vec2 uv;

out vec4 color;

void main() {
    vec3 nMap = texture(normal_map, uv).rgb;
    nMap = nMap * 2.0 - 1.0;

    vec3 n = normalize(TBN * nMap);
    vec3 l = normalize(light_dir);
    vec3 v = normalize(cam_pos - fragPos);

    vec3 r = normalize(reflect(-v, n));

    float diff = max(0.0, dot(n, l));

    vec3 h = normalize(l + v);
    float spec = pow(max(dot(n, h), 0.0), roughness);

    vec3 texColour = pow(texture(tex, uv).rgb, vec3(2.2));

    vec3 finalColour = texColour * 0.025 + texColour * diff + vec3(0.1) * spec;

    color = vec4(pow(finalColour, vec3(1.0/2.2)), 1.0);
}