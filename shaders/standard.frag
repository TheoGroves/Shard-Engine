#version 330 core

uniform vec3 light_dir;
uniform vec3 cam_pos;
uniform float shininess;

in mat3 TBN;
in mat4 out_model;
in vec3 fragPos;
in vec2 uv;

out vec4 color;

void main() {
    vec3 n = normalize(TBN[2]);
    vec3 l = normalize(light_dir);
    vec3 v = normalize(cam_pos - fragPos);

    vec3 r = normalize(reflect(-v, n));

    float diff = max(0.0, dot(n, l));

    vec3 h = normalize(l + v);
    float spec = pow(max(dot(n, h), 0.0), shininess);

    vec3 finalColour = 0.025 + diff + vec3(0.1) * spec * uv.x;

    color = vec4(pow(finalColour, vec3(1.0/2.2)), 1.0);
}