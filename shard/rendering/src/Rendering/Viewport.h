#pragma once

#include <GL/glew.h>

struct Viewport
{
    GLuint fbo = 0;
    GLuint colour = 0;
    GLuint depth = 0;

    int width = 1280;
    int height = 720;

    void Create(int w, int h);
    void Destroy();
    void Resize(int w, int h);

    void Bind();

    void Unbind(int windowWidth, int windowHeight);

private:
    void CreateAttachments();
};