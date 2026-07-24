#version 330 core

in vec3 vDir;
out vec4 FragColor;

uniform sampler2D uEnvMap;
uniform float uExposure;
uniform float uRotation;

void main() {
    vec3 d = normalize(vDir);

    float rotRad = radians(uRotation);

    float c = cos(rotRad);
    float s = sin(rotRad);

    d = vec3(
        c * d.x + s * d.z,
        d.y,
        -s * d.x + c * d.z
    );

    vec2 uv;
    uv.x = atan(d.z, d.x) / (2.0 * 3.14159265) + 0.5;
    uv.y = asin(d.y) / 3.14159265 + 0.5;

    vec3 env = texture(uEnvMap, uv).rgb;
    env = vec3(1.0) - exp(-env * uExposure);
    FragColor = vec4(env, 1.0);
}