#version 330 core

uniform float camHeight;
in vec3 vDir;
out vec4 color;

uniform vec3 sun_dir;
uniform vec3 sun_color;

uniform float air;
uniform float aerosols;
uniform float ozone;

uniform float time;

uniform float cloud_coverage;
uniform float cloud_density;
vec2 cloud_wind = vec2(0.01, 0.06);

const float PI = 3.14159265;

const float PLANET_RADIUS = 6371000.0;
const float ATMOS_RADIUS  = 6671000.0;

const float HR = 8000.0;
const float HM = 1200.0;

const vec3 BETA_R = vec3(5.802e-6, 13.558e-6, 33.100e-6);
const vec3 BETA_M = vec3(21e-6);
const vec3 BETA_O = vec3(0.650e-6, 1.881e-6, 0.085e-6);

bool raySphereIntersect(vec3 ro, vec3 rd, float radius, out float t0, out float t1)
{
    float b = dot(ro, rd);
    float c = dot(ro, ro) - radius * radius;

    float h = b * b - c;
    if (h < 0.0)
        return false;

    h = sqrt(h);
    t0 = -b - h;
    t1 = -b + h;
    return true;
}

float getHeight(vec3 p)
{
    return max(length(p) - PLANET_RADIUS, 0.0);
}

float rayleighDensity(float h)
{
    return exp(-h / HR);
}

float mieDensity(float h)
{
    return exp(-h / HM);
}

float ozoneDensity(float h)
{
    float x = (h - 25000.0) / 15000.0;
    return exp(-4.0 * x * x);
}

float rayleighPhase(float mu)
{
    return (3.0 / (16.0 * PI)) * (1.0 + mu * mu);
}

float miePhase(float mu)
{
    float g = 0.76;
    float g2 = g * g;

    return (1.0 - g2) /
           (4.0 * PI * pow(1.0 + g2 - 2.0 * g * mu, 1.5));
}

vec3 opticalDepth(vec3 ro, vec3 rd, float maxDist)
{
    const int STEPS = 16;

    float stepSize = maxDist / float(STEPS);

    float dR = 0.0;
    float dM = 0.0;
    float dO = 0.0;

    for (int i = 0; i < STEPS; i++)
    {
        float t = (float(i) + 0.5) * stepSize;
        vec3 p = ro + rd * t;

        float h = getHeight(p);

        dR += rayleighDensity(h) * stepSize;
        dM += mieDensity(h) * stepSize;
        dO += ozoneDensity(h) * stepSize;
    }

    return vec3(dR, dM, dO);
}

vec3 atmosphere(vec3 cameraPos, vec3 viewDir, vec3 sunDir)
{
    float t0, t1;

    if (!raySphereIntersect(cameraPos, viewDir, ATMOS_RADIUS, t0, t1))
        return vec3(0.0);

 if (!raySphereIntersect(cameraPos, viewDir, ATMOS_RADIUS, t0, t1))
    return vec3(0.0);

    t0 = max(t0, 0.0);

    float ground0, ground1;

    if (raySphereIntersect(cameraPos, viewDir, PLANET_RADIUS, ground0, ground1))
    {
        if (ground0 > 0.0)
            t1 = min(t1, ground0);
    }

    if (t1 <= t0)
        return vec3(0.0);

    const int STEPS = 32;
    float segment = (t1 - t0) / float(STEPS);

    float mu = dot(viewDir, sunDir);

    float phaseR = rayleighPhase(mu);
    float phaseM = miePhase(mu);

    vec3 result = vec3(0.0);

    for (int i = 0; i < STEPS; i++)
    {
        float tA = t0 + float(i) * segment;
        float tB = t0 + float(i + 1) * segment;

        vec3 pA = cameraPos + viewDir * tA;
        vec3 pB = cameraPos + viewDir * tB;

        float hA = getHeight(pA);
        float hB = getHeight(pB);

        float rA = rayleighDensity(hA);
        float rB = rayleighDensity(hB);

        float mA = mieDensity(hA);
        float mB = mieDensity(hB);

        float oA = ozoneDensity(hA);
        float oB = ozoneDensity(hB);

        float t = 0.5 * (tA + tB);
        float r = 0.5 * (rA + rB);
        float m = 0.5 * (mA + mB);
        float o = 0.5 * (oA + oB);
        vec3 p = vec3(0.5, 0.5 , 0.5) * (pA + pB);

        float ground0, ground1;

        bool inShadow = false;

        if(raySphereIntersect(p, sunDir, PLANET_RADIUS, ground0, ground1))
        {
            if(ground1 > 0.0)
                inShadow = true;
        }

        if(inShadow)
            continue;

        float sun0, sun1;
        raySphereIntersect(p, sunDir, ATMOS_RADIUS, sun0, sun1);

        vec3 sunOD  = opticalDepth(p, sunDir, sun1);
        vec3 viewOD = opticalDepth(cameraPos, viewDir, t);

        vec3 tau = BETA_R * air * (sunOD.x + viewOD.x) + BETA_M * aerosols * (sunOD.y + viewOD.y) + BETA_O * ozone * (sunOD.z + viewOD.z);

        vec3 transmittance = exp(-tau);

        vec3 scatter = r * BETA_R * air * phaseR + m * BETA_M * aerosols * phaseM;

        result += scatter * transmittance * segment;
    }

    return result * sun_color;
}

float sunDisc(vec3 viewDir, vec3 sunDir)
{
    float mu = clamp(dot(viewDir, sunDir), -1.0, 1.0);

    float angle = acos(mu);

    float sunRadius = radians(0.27);

    float disk = 1.0 - smoothstep(
        sunRadius * 0.85,
        sunRadius,
        angle
    );

    return disk;
}


float proceduralSunFlare(vec3 viewDir, vec3 sunDir)
{
    float mu = clamp(dot(viewDir, sunDir), -1.0, 1.0);
    float angle = acos(mu);

    float corona = exp(-angle * 180.0);
    corona *= 0.35;


    float halo = exp(-angle * 35.0);
    halo *= 0.12;

    float radial = angle * 90.0;

    float rays = 12.0;

    vec3 up = abs(sunDir.y) < 0.99 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0);

    vec3 tangent = normalize(cross(up, sunDir));
    vec3 bitangent = cross(sunDir, tangent);

    float x = dot(viewDir, tangent);
    float y = dot(viewDir, bitangent);

    float azimuth = atan(y, x);

    float rayPattern = pow(abs(cos(azimuth * rays)), 18.0);

    float rayFalloff = exp(-radial * 0.45);

    float spikes = rayPattern * rayFalloff * 0.18;

    return corona + halo + spikes;
}

// Clouds
float hash31(vec3 p)
{
    p = fract(p * 0.1031);
    p += dot(p, p.yzx + 33.33);
    return fract((p.x + p.y) * p.z);
}

float noise3D(vec3 p)
{
    vec3 i = floor(p);
    vec3 f = fract(p);

    f = f * f * (3.0 - 2.0 * f);

    float n000 = hash31(i + vec3(0, 0, 0));
    float n100 = hash31(i + vec3(1, 0, 0));
    float n010 = hash31(i + vec3(0, 1, 0));
    float n110 = hash31(i + vec3(1, 1, 0));

    float n001 = hash31(i + vec3(0, 0, 1));
    float n101 = hash31(i + vec3(1, 0, 1));
    float n011 = hash31(i + vec3(0, 1, 1));
    float n111 = hash31(i + vec3(1, 1, 1));

    float x00 = mix(n000, n100, f.x);
    float x10 = mix(n010, n110, f.x);
    float x01 = mix(n001, n101, f.x);
    float x11 = mix(n011, n111, f.x);

    float y0 = mix(x00, x10, f.y);
    float y1 = mix(x01, x11, f.y);

    return mix(y0, y1, f.z);
}

float fbm(vec3 p)
{
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < 4; i++)
    {
        value += noise3D(p) * amplitude;

        p *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

float cloudDensity(vec3 p)
{
    float h = length(p) - PLANET_RADIUS;

    const float CLOUD_BASE = 1500.0;
    const float CLOUD_TOP  = 10000.0;

    float height01 = clamp((h - CLOUD_BASE) / (CLOUD_TOP - CLOUD_BASE), 0.0, 1.0);

    float heightShape = smoothstep(0.0, 0.15, height01) * (1.0 - smoothstep(0.75, 1.0, height01));

    vec3 q = p - vec3(0.0, PLANET_RADIUS, 0.0);

    q.xz *= 0.00012;
    q.y *= 0.00020;

    q.xz += cloud_wind * time;

    float n = fbm(q);

    float d = smoothstep(cloud_coverage, cloud_coverage + 0.18, n);

    return d * heightShape * cloud_density;
}

bool cloudLayerIntersect(vec3 ro, vec3 rd, out float startT, out float endT)
{
    const float CLOUD_BASE = 1500.0;
    const float CLOUD_TOP  = 10000.0;

    float innerRadius = PLANET_RADIUS + CLOUD_BASE;
    float outerRadius = PLANET_RADIUS + CLOUD_TOP;

    float outer0, outer1;
    float inner0, inner1;

    if (!raySphereIntersect(ro, rd, outerRadius, outer0, outer1)) {
        return false;
    }

    bool hitsInner = raySphereIntersect(ro, rd, innerRadius, inner0, inner1);

    float cameraRadius = length(ro);

    if (cameraRadius < innerRadius)
    {
        startT = max(inner1, 0.0);
        endT = max(outer1, 0.0);
    }
    else if (cameraRadius < outerRadius)
    {
        startT = 0.0;
        endT = max(outer1, 0.0);
    }
    else
    {
        startT = max(outer0, 0.0);

        if (!hitsInner)
            return false;

        endT = inner0;
    }

    float ground0, ground1;

    if (raySphereIntersect(ro, rd, PLANET_RADIUS, ground0, ground1))
    {
        if (ground0 > 0.0)
        {
            endT = min(endT, ground0);
        }
    }

    if (endT <= startT)
        return false;

    return true;
}

vec4 clouds(vec3 cameraPos, vec3 viewDir, vec3 sunDir)
{
    float startT;
    float endT;

    if (!cloudLayerIntersect(cameraPos, viewDir, startT, endT)) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }

    const int STEPS = 48;

    float segment = (endT - startT) / float(STEPS);

    vec3 result = vec3(0.0);
    float transmittance = 1.0;

    for (int i = 0; i < STEPS; i++)
    {
        float tA = startT + float(i) * segment;
        float tB = startT + float(i + 1) * segment;

        vec3 pA = cameraPos + viewDir * tA;
        vec3 pB = cameraPos + viewDir * tB;

        float dA = cloudDensity(pA);
        float dB = cloudDensity(pB);

        float t = 0.5 * (tA + tB);
        vec3 p = vec3(0.5, 0.5, 0.5) * (pA + pB);
        float d = 0.5 * (dA + dB);

        float density = 0.5 * (dA + dB);

        if (density <= 0.001)
            continue;

        float sun0, sun1;
        raySphereIntersect(p, sunDir, ATMOS_RADIUS, sun0, sun1);

        float sunDist = max(sun1, 0.0);

        vec3 sunOD = opticalDepth(p, sunDir, sunDist);

        vec3 sunTau = BETA_R * air * sunOD.x + BETA_M * aerosols * sunOD.y + BETA_O * ozone * sunOD.z;

        vec3 sunTransmittance = exp(-sunTau);

        float cloudShadow = exp(-cloudDensity(p + sunDir * 1500.0) * 1.5);
        cloudShadow = mix(0.3, 1.0, cloudShadow);

        float height =
            clamp((length(p) - PLANET_RADIUS - 1500.0) / 3500.0, 0.0, 1.0);

        float sunLight = max(sunDir.y, 0.0);

        float light = mix(0.35, 1.0, height);

        light *= mix(0.65, 1.0, sunLight);

        vec3 cloudColor = vec3(1.0, 0.98, 0.95) * sun_color * sunTransmittance * cloudShadow * light;

        float extinction = density * segment * 0.00035;

        float alpha = 1.0 - exp(-extinction);

        result += cloudColor * alpha * transmittance;

        transmittance *= 1.0 - alpha;

        if (transmittance < 0.01)
            break;
    }

    return vec4(result, transmittance);
}

void main()
{
    vec3 cameraPos = vec3(0.0, PLANET_RADIUS + max(2.0, camHeight), 0.0);

    vec3 viewDir = normalize(vDir);
    vec3 sunDir = normalize(sun_dir);

    vec3 col = atmosphere(cameraPos, viewDir, sunDir);

    vec4 cloudResult = clouds(cameraPos, viewDir, sunDir);

    col *= cloudResult.a;

    col += cloudResult.rgb;

    float sun = sunDisc(viewDir, sunDir);

    float sun0, sun1;

    raySphereIntersect(cameraPos, sunDir, ATMOS_RADIUS, sun0, sun1);

    vec3 sunOD = opticalDepth(cameraPos, sunDir, sun1);

    vec3 sunTau = BETA_R * air * sunOD.x + BETA_M * aerosols * sunOD.y + BETA_O * ozone * sunOD.z;

    vec3 sunTransmittance = exp(-sunTau);

    col += sun_color * sunTransmittance * sun * 25.0;

    float flare = proceduralSunFlare(viewDir, sunDir);

    col += sun_color * flare * sunTransmittance;

    col = 1.0 - exp(-col * 8.0);

    col = pow(col, vec3(1.0 / 2.2));

    color = vec4(col, 1.0);
}