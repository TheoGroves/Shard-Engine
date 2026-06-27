#version 330 core

in vec3 dir;
out vec4 color;

uniform vec3 sun_dir;
uniform vec3 sun_color;

uniform float air;
uniform float aerosols;
uniform float ozone;

const float PI = 3.14159265;

const float PLANET_RADIUS = 6371000.0;
const float ATMOS_RADIUS  = 6471000.0;

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

    t0 = max(t0, 0.0);

    const int STEPS = 32;
    float segment = (t1 - t0) / float(STEPS);

    float mu = dot(viewDir, sunDir);

    float phaseR = rayleighPhase(mu);
    float phaseM = miePhase(mu);

    vec3 result = vec3(0.0);

    for (int i = 0; i < STEPS; i++)
    {
        float t = t0 + (float(i) + 0.5) * segment;
        vec3 p = cameraPos + viewDir * t;

        float h = getHeight(p);

        float r = rayleighDensity(h);
        float m = mieDensity(h);
        float o = ozoneDensity(h);

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

        vec3 tau =
            BETA_R * air      * (sunOD.x + viewOD.x) +
            BETA_M * aerosols * (sunOD.y + viewOD.y) +
            BETA_O * ozone    * (sunOD.z + viewOD.z);

        vec3 transmittance = exp(-tau);

        vec3 scatter =
            r * BETA_R * air * phaseR +
            m * BETA_M * aerosols * phaseM;

        result += scatter * transmittance * segment;
    }

    return result * sun_color;
}

void main()
{
    vec3 cameraPos = vec3(0.0, PLANET_RADIUS + 2.0, 0.0);

    vec3 viewDir = normalize(dir);
    vec3 sunDir = normalize(sun_dir);

    vec3 col = atmosphere(cameraPos, viewDir, sunDir);

float mu = dot(viewDir, sunDir);

    if (mu > 0.9999)
    {
        float sun0, sun1;
        raySphereIntersect(cameraPos, sunDir, ATMOS_RADIUS, sun0, sun1);

        vec3 sunOD = opticalDepth(cameraPos, sunDir, sun1);

        vec3 sunTau =
            BETA_R * air      * sunOD.x +
            BETA_M * aerosols * sunOD.y +
            BETA_O * ozone    * sunOD.z;

        vec3 sunTransmittance = exp(-sunTau);

        col += sun_color * sunTransmittance * 25.0;
    }

    col = 1.0 - exp(-col * 8.0);

    col = pow(col, vec3(1.0 / 2.2));

    color = vec4(col, 1.0);
}