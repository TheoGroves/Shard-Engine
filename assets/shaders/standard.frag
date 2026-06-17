#version 330 core

uniform sampler2D tex;
uniform sampler2D normal_map;
uniform sampler2D env_map;
uniform sampler2D height_map;
uniform sampler2D orm_map;

uniform sampler2D shadow_map;

uniform vec3 light_dir;
uniform vec3 cam_pos;
uniform float height_scale;
uniform float tonemapExposure;

in mat3 TBN;
in mat4 out_model;
in vec3 fragPos;
in vec2 uv;
in vec4 fragPosLightSpace;

out vec4 color;

float ShadowCalculation(vec4 fragPosLightSpace, vec3 n, vec3 l)
{
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;

    if(projCoords.z > 1.0)
        return 0.0;

    float currentDepth = projCoords.z;
    float bias = 0.0015 * (1.0 - dot(n, l)) + 0.0002;

    float shadow = 0.0;

    vec2 texelSize = 1.0 / textureSize(shadow_map, 0);

    for(int x = -1; x <= 1; x++)
    {
        for(int y = -1; y <= 1; y++)
        {
            float closestDepth = texture(shadow_map, projCoords.xy + vec2(x, y) * texelSize).r;
            shadow += (currentDepth - bias > closestDepth) ? 1.0 : 0.0;
        }
    }

    shadow /= 9.0;

    return shadow;
}

float DistributionGGX(vec3 N, vec3 H, float roughness)
{
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    return a2 / (3.14159265 * denom * denom);
}

float GeometryShlickGGX(float NdotV, float roughness)
{
    float r = roughness + 1.0;
    float k = (r * r) / 8.0;

    return NdotV / (NdotV * (1.0 - k) + k);
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
{
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    return GeometryShlickGGX(NdotV, roughness) * GeometryShlickGGX(NdotL, roughness);
}

vec3 FresnelSchlick(float cosTheta, vec3 F0)
{
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

void main() {
    vec3 viewDir = normalize(cam_pos - fragPos);
    vec3 view = normalize(TBN * viewDir);

    float denom = max(view.z, 0.2);

    float height = texture(height_map, uv).r;
    height = height * 2.0 - 1.0;

    vec2 parallaxDir = view.xy / denom;
    vec2 parallaxOffset = parallaxDir * (height * height_scale);

    vec2 uvParallax = uv - parallaxOffset;

    vec3 nMap = texture(normal_map, uvParallax).rgb;
    nMap = nMap * 2.0 - 1.0;

    vec3 n = normalize(TBN * nMap);
    vec3 l = normalize(light_dir);
    vec3 v = normalize(cam_pos - fragPos);

    // PBR model
    vec3 orm = texture(orm_map, uvParallax).rgb;

    vec4 baseSample = texture(tex, uvParallax);

    if(baseSample.a < 0.5)
        discard;

    vec3 albedo = baseSample.rgb;

    float metallic = orm.b;
    float roughness = clamp(orm.g, 0.04, 1.0);
    float ao = orm.r;

    vec3 F0 = mix(vec3(0.04), albedo, metallic);

    vec3 L = normalize(light_dir);
    vec3 V = normalize(cam_pos - fragPos);
    vec3 H = normalize(L + V);

    float NdotL = max(dot(n, L), 0.0);
    float NdotV = max(dot(n, V), 0.0);
    float NdotH = max(dot(n, H), 0.0);
    float VdotH = max(dot(V, H), 0.0);

    float NDF = DistributionGGX(n, H, roughness);
    float G   = GeometrySmith(n, V, L, roughness);
    vec3  F   = FresnelSchlick(VdotH, F0);

    vec3 specular = (NDF * G * F) / max(4.0 * NdotV * NdotL, 0.001);

    vec3 kS = F;
    vec3 kD = (1.0 - kS) * (1.0 - metallic);

    vec3 diffuse = kD * albedo / 3.14159265;

    float shadow = ShadowCalculation(fragPosLightSpace, n, L);
    float sunVisibility = step(0.0, light_dir.y);

    float lightIntensity = 3.0;
    vec3 direct = (diffuse + specular) * NdotL * lightIntensity * sunVisibility * (1.0 - shadow);

    vec3 ambient = albedo * ao * 0.08;

    ambient += vec3(0.1) * albedo;

    vec3 colorFinal = direct + ambient;

    vec3 hdr = colorFinal;

    hdr = vec3(1.0) - exp(-hdr * tonemapExposure);

    color = vec4(hdr, 1.0);
}