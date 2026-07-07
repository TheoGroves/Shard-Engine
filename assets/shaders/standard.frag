#version 460 core


uniform sampler2D uAlbedo;
uniform sampler2D uNormal;
uniform sampler2D uHeightMap;
uniform sampler2D uOrmMap;
uniform sampler2D uEnvMap;

uniform sampler2D uShadowMap;

uniform vec3 uLightDir;
uniform vec3 uCamPos;
uniform float uHeightScale;
uniform float uTonemapExposure;

in mat3 vTBN;
in vec3 vPos;
in mat4 vModel;
in vec2 vUV;
in vec4 vFragPosLightSpace;

out vec4 FragColor;

const vec2 poisson[16] = vec2[](
    vec2(-0.942,-0.399),
    vec2( 0.945,-0.769),
    vec2(-0.094,-0.929),
    vec2( 0.345, 0.294),
    vec2(-0.916, 0.458),
    vec2(-0.815,-0.879),
    vec2(-0.383, 0.277),
    vec2( 0.975, 0.756),
    vec2( 0.443,-0.975),
    vec2( 0.537,-0.474),
    vec2(-0.265,-0.418),
    vec2( 0.792, 0.191),
    vec2(-0.242, 0.998),
    vec2(-0.814, 0.914),
    vec2( 0.200, 0.786),
    vec2( 0.144,-0.141)
);

float ShadowCalculation(vec4 fragPosLightSpace, vec3 n, vec3 l)
{
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;

    if (projCoords.z > 1.0)
        return 0.0;

    float currentDepth = projCoords.z;
    float bias = 0.015 * (1.0 - dot(n, l)) + 0.002;

    float shadow = 0.0;

    vec2 texelSize = 1.0 / textureSize(uShadowMap, 0);

    // PCF 3x3 Poisson Sampling
    float radius = 2.0;

    for(int i = 0; i < 16; i++)
    {
        float depth = texture(
            uShadowMap,
            projCoords.xy + poisson[i] * texelSize * radius
        ).r;
        
        shadow += currentDepth - bias > depth ? 1.0 : 0.0;
    }
    shadow /= 16.0;

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

void main()
{
    vec3 viewDir = normalize(uCamPos - vPos);
    vec3 view = normalize(vTBN * viewDir);

    float denom = max(view.z, 0.2);

    float height = texture(uHeightMap, vUV).r;
    height = height * 2.0 - 1.0;

    vec2 parallaxDir = view.xy / denom;
    vec2 parallaxOffset = parallaxDir * (height * uHeightScale);

    vec2 uvParallax = fract(vUV - parallaxOffset);

    vec3 nMap = texture(uNormal, uvParallax).rgb;
    nMap = nMap * 2.0 - 1.0;

    vec3 n = normalize(vTBN * nMap);
    vec3 l = normalize(-uLightDir);
    vec3 v = viewDir;

    // Cook-Torrance Reflectance model
    vec3 orm = texture(uOrmMap, uvParallax).rgb;

    vec4 baseSample = texture(uAlbedo, uvParallax);

    if(baseSample.a < 0.5)
        discard;

    vec3 albedo = baseSample.rgb;

    float metallic = orm.b;
    float roughness = clamp(orm.g, 0.04, 1.0);
    float ao = orm.r;

    vec3 F0 = mix(vec3(0.04), albedo, metallic);

    vec3 L = l;
    vec3 V = viewDir;
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

    float shadow = ShadowCalculation(vFragPosLightSpace, n, L);
    float sunVisibility = smoothstep(-0.1, 0.2, uLightDir.y);

    float lightIntensity = 3.0;
    vec3 direct = (diffuse + specular) * NdotL * lightIntensity * (1.0-sunVisibility) * (1.0 - shadow);

    vec3 ambient = albedo * ao * 0.08;

    ambient += vec3(0.1) * albedo;

    vec3 hdr = direct + ambient;
    hdr = vec3(1.0) - exp(-hdr * uTonemapExposure);

    FragColor = vec4(hdr, 1.0);
}