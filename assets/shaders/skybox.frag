#version 330 core

in vec3 vDir;
out vec4 FragColor;

uniform sampler2D uEnvMap;

void main() {
    vec3 d = normalize(vDir);

    vec2 uv;
    uv.x = atan(d.z, d.x) / (2.0 * 3.14159265) + 0.5;
    uv.y = asin(d.y) / 3.14159265 + 0.5;

    float exposure = 2.5;
    vec3 env = texture(uEnvMap, uv).rgb;
    env = vec3(1.0) - exp(-env * exposure);
    FragColor = vec4(env, 1.0);
}