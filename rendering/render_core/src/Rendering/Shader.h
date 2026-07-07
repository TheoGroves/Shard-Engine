#pragma once

#include <GL/glew.h>
#include <string>
#include "Math/Mat4.h"
#include "Math/Vec3.h"

class Shader
{
public:
    Shader() = default;
    ~Shader();

    bool LoadFromFile(const std::string& vertexPath,
                      const std::string& fragmentPath);

    void Use() const;

    void SetInt(const std::string& name, const int& value);
    void SetFloat(const std::string& name, const float& value);
    void SetVec3(const std::string& name, const Vec3& vector);
    void SetMat4(const std::string& name, const Mat4& mat);

private:
    GLuint mProgram = 0;

    std::string LoadFile(const std::string& path);
    GLuint Compile(GLenum type, const std::string& source);
};