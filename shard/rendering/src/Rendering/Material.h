#pragma once
#include <memory>
#include "Shader.h"

struct Material
{
    std::shared_ptr<Shader> shader;
    GLuint albedo = 0;
};
