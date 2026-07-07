#version 460 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aUV;
layout(location = 2) in vec3 aNormal;
layout(location = 3) in vec3 aTangent;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;

uniform float uUVScale;

uniform mat4 uLightSpace;

out mat3 vTBN;
out vec3 vPos;
out mat4 vModel;
out vec2 vUV;
out vec4 vFragPosLightSpace;

void main()
{
    mat4 mvp = uProj * uView * uModel;

    mat3 model3 = mat3(uModel);
    mat3 normalMatrix = transpose(inverse(mat3(uModel)));

    vec3 T = normalize(model3 * aTangent);
    vec3 N = normalize(normalMatrix * aNormal);

    T = normalize(T - dot(T, N) * N);
    vec3 B = cross(N, T);

    vTBN = mat3(T, B, N);

    gl_Position = mvp * vec4(aPos, 1.0);

    vPos = vec3(uModel * vec4(aPos, 1.0));
    vModel = uModel;
    vUV = aUV * uUVScale;
    vFragPosLightSpace = uLightSpace * vec4(vPos, 1.0);
}