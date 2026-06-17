#version 330 core

in vec3 dir;
out vec4 color;

uniform vec3 sun_dir;
uniform vec3 sun_color;

const float PI = 3.14159265;
const float g = 0.76;

const float PLANET_RADIUS = 6371000.0;
const float ATMOS_RADIUS  = 6471000.0;

const float HR = 8000.0;
const float HM = 1200.0;

const vec3 BETA_M = vec3(21e-6);
const vec3 BETA_R = vec3(5.802e-6, 13.558e-6, 33.100e-6);

bool raySphereIntersect(vec3 ro, vec3 rd, float radius, out float t0, out float t1)
{
    float b = dot(ro, rd);
    float c = dot(ro, ro) - radius * radius;

    float h = b*b - c;

    if(h < 0.0)
        return false;

    h = sqrt(h);

    t0 = -b - h;
    t1 = -b + h;

    return true;
}

float getHeight(vec3 p)
{
    return length(p) - PLANET_RADIUS;
}

float densityRayleigh(float height)
{
    return exp(-height / HR);
}

float densityMie(float height)
{
    return exp(-height / HM);
}

vec2 opticalDepth(vec3 ro, vec3 rd, float maxDist)
{
    const int STEPS = 8;

    float stepSize = maxDist / float(STEPS);

    float depthR = 0.0;
    float depthM = 0.0;

    for(int i=0;i<STEPS;i++)
    {
        float t = (float(i)+0.5) * stepSize;

        vec3 p = ro + rd*t;

        float h = getHeight(p);

        depthR += densityRayleigh(h) * stepSize;
        depthM += densityMie(h) * stepSize;
    }

    return vec2(depthR, depthM);
}

float rayleighPhase(float mu)
{
    return (3.0/(16.0*PI))*(1.0+mu*mu);
}

float miePhase(float mu)
{
    float gg = g * g;

    return
        (3.0 * (1.0 - gg) * (1.0 + mu * mu)) /
        (8.0 * PI * (2.0 + gg) *
         pow(1.0 + gg - 2.0 * g * mu, 1.5));
}

vec3 atmosphere(vec3 cameraPos, vec3 viewDir, vec3 sunDir)
{
    float t0, t1;

    if(!raySphereIntersect(cameraPos, viewDir, ATMOS_RADIUS, t0, t1))
    {
        return vec3(0.0);
    }

    t0 = max(t0, 0.0);

    const int VIEW_STEPS = 16;

    float segment = (t1 - t0) / float(VIEW_STEPS);

    vec3 result = vec3(0.0);

    float accumulatedR = 0.0;
    float accumulatedM = 0.0;

    float mu = dot(viewDir, sunDir);

    float phaseR = rayleighPhase(mu);
    float phaseM = miePhase(mu);

    for(int i=0;i<VIEW_STEPS;i++)
    {
        float t = t0 + (float(i)+0.5)*segment;

        vec3 samplePos = cameraPos + viewDir*t;

        float height = getHeight(samplePos);

        float localR = densityRayleigh(height);

        float localM = densityMie(height);

        accumulatedR += localR * segment;
        accumulatedM += localM * segment;

        float p0, p1;

        bool inShadow = false;

        if(raySphereIntersect(samplePos, sunDir, PLANET_RADIUS, p0, p1))
        {
            if(p1 > 0.0)
                inShadow = true;
        }

        if(inShadow)
            continue;

        float s0, s1;
        raySphereIntersect(samplePos, sunDir, ATMOS_RADIUS, s0, s1);

        vec2 sunDepth = opticalDepth(samplePos, sunDir, s1);

        vec3 tau = BETA_R * (accumulatedR + sunDepth.x) + BETA_M * (accumulatedM + sunDepth.y);

        vec3 transmittance = exp(-tau);

        result += transmittance * (localR * BETA_R * phaseR + localM * BETA_M * phaseM) * segment;
    }

    return result;
}

void main()
{
    vec3 cameraPos = vec3(0.0, PLANET_RADIUS + 2.0, 0.0);

    vec3 viewDir = normalize(dir);
    vec3 sunDir  = normalize(sun_dir);

    vec3 col = atmosphere(cameraPos, viewDir, sunDir)*8;

    float sunAmount = smoothstep(0.99995, 0.99999, dot(viewDir, sunDir));

    col += sun_color * 20000.0 * sunAmount;

    col = col / (col + vec3(1.0));

    col = pow(col, vec3(1.0 / 2.2));

    color = vec4(col, 1.0);
}