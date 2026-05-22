#version 330 core

uniform sampler2D tex;
uniform sampler2D normal_map;
uniform sampler2D env_map;
uniform sampler2D height_map;

uniform vec3 light_dir;
uniform vec3 cam_pos;
uniform float roughness;
uniform float height_scale;

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

    vec3 r = normalize(reflect(-l, n));
    float fresnel = pow(1.0 - max(dot(n,v), 0.0), 5.0);
    vec2 envUV;
    envUV.x = atan(r.z, r.x) / (2.0*3.14159265) + 0.5;
    envUV.y = asin(r.y) / 3.14159265 + 0.5;
    float exposure = 0.6;
    vec3 env = texture(env_map, envUV).rgb;
    env = vec3(1.0) - exp(-env * exposure);

    float diff = max(0.0, dot(n, l));

    vec3 h = normalize(l + v);
    float spec = pow(max(dot(n, h), 0.0), roughness);

    vec3 texColour = pow(texture(tex, uv).rgb, vec3(2.2));

    vec3 finalColour = texColour * 0.025 + texColour * diff + vec3(0.1) * spec + env * fresnel;

    color = vec4(pow(finalColour, vec3(1.0/2.2)), 1.0);
}