#include "Viewport.h"

void Viewport::Create(int w, int h)
{
    width = w;
    height = h;

    glCreateFramebuffers(1, &fbo);

    CreateAttachments();
};

void Viewport::Destroy()
{
    if (colour)
        glDeleteTextures(1, &colour);

    if (depth)
        glDeleteRenderbuffers(1, &depth);

    if (fbo)
        glDeleteFramebuffers(1, &fbo);

    colour = 0;
    depth = 0;
    fbo = 0;
}

void Viewport::Resize(int w, int h)
{
    if (w == width && h == height)
        return;

    width = w;
    height = h;

    if (colour)
        glDeleteTextures(1, &colour);

    if (depth)
        glDeleteRenderbuffers(1, &depth);

    CreateAttachments();
}

void Viewport::Bind()
{
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glViewport(0,0,width,height);

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void Viewport::Unbind(int windowWidth, int windowHeight)
{
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0,0,windowWidth,windowHeight);
}

void Viewport::CreateAttachments()
{
    glCreateTextures(GL_TEXTURE_2D, 1, &colour);
    glTextureStorage2D(colour, 1, GL_RGBA8, width, height);

    glTextureParameteri(colour, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTextureParameteri(colour, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glNamedFramebufferTexture(fbo, GL_COLOR_ATTACHMENT0, colour, 0);

    glCreateRenderbuffers(1, &depth);
    glNamedRenderbufferStorage(depth, GL_DEPTH24_STENCIL8, width, height);

    glNamedFramebufferRenderbuffer(
        fbo,
        GL_DEPTH_STENCIL_ATTACHMENT,
        GL_RENDERBUFFER,
        depth
    );
}