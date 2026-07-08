#pragma once

#include <GL/glew.h>
#include "Math/Mat4.h"
#include "Math/Vec3.h"
#include "Rendering/Shader.h"
#include <string>

class ShadowMapper
{
public:
    ShadowMapper(int shadowSize = 2048);

    void CreateResources();
    void Initialize(const Vec3& lightDir);

    void Update(const Vec3& lightDir, const Vec3& target);

    void BeginRender();
    void EndRender(int screenWidth, int screenHeight);

    void RenderDepthMesh(GLuint vao, int indexCount, const Mat4& model);

    const Mat4& GetLightSpaceMatrix() const { return mLightSpace; }
    GLuint GetDepthTexture() const { return mDepthTexture; }

private:
    int mSize;

    GLuint mFBO = 0;
    GLuint mDepthTexture = 0;

    Shader mShader;

    Mat4 mProj;
    Mat4 mView;
    Mat4 mLightSpace;

    Vec3 mLightDir;
};