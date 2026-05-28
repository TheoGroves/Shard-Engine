#version 330 core

in vec3 in_pos;
in vec2 in_uv_map;
in vec3 in_normal;
in vec3 in_tangent;

out mat3 TBN;
out vec3 fragPos;
out mat4 out_model;
out vec2 uv;
out vec4 fragPosLightSpace;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

uniform float uv_scale;

uniform mat4 light_space;

void main() {
    mat4 mvp = proj * view * model;

    mat3 model3 = mat3(model);
    mat3 normalMatrix = transpose(inverse(mat3(model)));

    vec3 T = normalize(model3 * in_tangent);
    vec3 N = normalize(normalMatrix * in_normal);

    T = normalize(T - dot(T, N) * N);
    vec3 B = cross(N, T);

    TBN = mat3(T, B, N);

    gl_Position = mvp * vec4(in_pos, 1.0);

    fragPos = vec3(model * vec4(in_pos, 1.0));
    out_model = model;
    uv = in_uv_map * uv_scale;
    fragPosLightSpace = light_space * vec4(fragPos, 1.0);
}