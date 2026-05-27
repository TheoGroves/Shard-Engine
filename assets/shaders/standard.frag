#version 330 core

uniform sampler2D tex;
uniform sampler2D normal_map;
uniform sampler2D env_map;
uniform sampler2D height_map;

uniform sampler2D shadow_map;

uniform vec3 light_dir;
uniform vec3 cam_pos;
uniform float roughness;
uniform float height_scale;

in mat3 TBN;
in mat4 out_model;
in vec3 fragPos;
in vec2 uv;
in vec4 fragPosLightSpace;

out vec4 color;

float ShadowCalculation(vec4 fragPosLightSpace)
{
    vec3 projCoords =
        fragPosLightSpace.xyz /
        fragPosLightSpace.w;

    projCoords = projCoords * 0.5 + 0.5;

    float closestDepth =
        texture(shadow_map, projCoords.xy).r;

    float currentDepth = projCoords.z;

    float bias = 0.005;

    float shadow =
        currentDepth - bias > closestDepth
        ? 1.0 : 0.0;

    if(projCoords.z > 1.0)
        shadow = 0.0;

    return shadow;
}

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

    float shadow = ShadowCalculation(fragPosLightSpace);

    vec3 lighting = texColour * 0.025 + (1.0 - shadow) * texColour * diff + vec3(0.1) * spec * (1.0 - shadow) + env * fresnel;

    color = vec4(pow(lighting, vec3(1.0/2.2)), 1.0);
}