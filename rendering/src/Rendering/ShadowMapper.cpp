#include "ShadowMapper.h"
#include <GL/glew.h>

ShadowMapper::ShadowMapper(int shadowSize)
    : mSize(shadowSize)
{
}

void ShadowMapper::CreateResources()
{
    glCreateTextures(GL_TEXTURE_2D, 1, &mDepthTexture);
    
    glTextureStorage2D(
        mDepthTexture,
        1,
        GL_DEPTH_COMPONENT24,
        mSize,
        mSize
    );

    glTextureParameteri(mDepthTexture, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTextureParameteri(mDepthTexture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTextureParameteri(mDepthTexture, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTextureParameteri(mDepthTexture, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);

    float border[] = {1.0f, 1.0f, 1.0f, 1.0f};
    glTextureParameterfv(mDepthTexture, GL_TEXTURE_BORDER_COLOR, border);

    // Frame buffer
    glCreateFramebuffers(1, &mFBO);
    glNamedFramebufferTexture(mFBO, GL_DEPTH_ATTACHMENT, mDepthTexture, 0);

    glNamedFramebufferDrawBuffer(mFBO, GL_NONE);
    glNamedFramebufferReadBuffer(mFBO, GL_NONE);

    // Depth Shader
    mShader.LoadFromFile(
        "assets/shaders/shadow.vert",
        "assets/shaders/shadow.frag"
    );

    // Light Projection
    mProj = Ortho(-20, 20, -20, 20, 0.1, 50.0);
}

void ShadowMapper::Initialize(const Vec3& lightDir)
{
    mLightDir = Normalize(lightDir);
}

void ShadowMapper::Update(const Vec3& lightDir, const Vec3& target)
{
    mLightDir = Normalize(lightDir);

    Vec3 lightPos = target + mLightDir * 20.0f;

    mView = LookAt(lightPos, target, Vec3(0.0f, 1.0f, 0.0f));

    mLightSpace = mProj * mView;
}

void ShadowMapper::BeginRender()
{
    glBindFramebuffer(GL_FRAMEBUFFER, mFBO);

    glViewport(0, 0, mSize, mSize);
    glClearDepth(1.0);
    glClear(GL_DEPTH_BUFFER_BIT);

    glEnable(GL_DEPTH_TEST);
}

void ShadowMapper::EndRender(int screenWidth, int screenHeight)
{
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0, 0, screenWidth, screenHeight);
}

void ShadowMapper::RenderDepthMesh(GLuint vao, int indexCount, const Mat4& model)
{
    mShader.Use();

    mShader.SetMat4("uModel", model);
    mShader.SetMat4("uLightSpace", mLightSpace);

    glBindVertexArray(vao);
    glDrawElements(GL_TRIANGLES, indexCount, GL_UNSIGNED_INT, nullptr);
}