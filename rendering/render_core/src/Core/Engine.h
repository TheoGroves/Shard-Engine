#pragma once

#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <string>
#include <string_view>
#include <unordered_map>
#include <cstdint>
#include <vector>
#include <filesystem>
#include "Rendering/Window.h"
#include "Rendering/Shader.h"
#include "Rendering/Material.h"
#include "Rendering/Shadowmapper.h"
#include "Math/Mat4.h"
#include "Math/Vec3.h"
#include "Core/Input.h"

struct ShaderState
{
    std::filesystem::path vertex;
    std::filesystem::path fragment;

    bool operator==(const ShaderState& other) const
    {
        return vertex == other.vertex && fragment == other.fragment;
    }

    bool operator!=(const ShaderState& other) const
    {
        return !(*this == other);
    }
};

class Engine
{
public:
    static void LogMessage(std::string_view message);
    static void LogWarning(std::string_view warning);
    static void LogError(std::string_view error);

    GLuint CreateTextureRGBA(int width, int height, const std::vector<uint8_t>& pixels);
    GLuint CreateTextureRGB32F(int width, int height, const std::vector<float>& pixels);

    void UpdateInt(int matID, const std::string& uniform, int value);
    void UpdateFloat(int matID, const std::string& uniform, float value);
    void UpdateVec3(int matID, const std::string& uniform, Vec3 value);
    void UpdateMat4(int matID, const std::string& uniform, const Mat4& matrix);

    void BindTexture(GLuint texture, GLuint unit);

    Input GetInput();

    bool Initialize(unsigned int screenWidth, unsigned int screenHeight, std::string title);
    
    void BeginFrame();
    void EndFrame();

    int CreateMaterial(const std::string& frag, const std::string& vert);
    int CreateMesh(const float* vertices, size_t vertexFloatCount, const uint32_t* indices, size_t indexCount);
    void DrawMesh(int meshID, int materialID, const Mat4& model);

    void BeginShadows(Vec3 lightDir, Vec3 target);
    void EndShadows();

    Mat4 GetLightSpaceMatrix() const;
    GLuint GetShadowDepth() const;

    void DrawShadow(int meshID, const Mat4& model);

    GLFWwindow* GetNativeWindow() const;

    void DisableDepthMask();
    void EnableDepthMask();
    void DisableCullFace();
    void EnableCullFace();
    void DisableDepthTest();
    void EnableDepthTest();

    void HideMouse();
    void ShowMouse();

    void Shutdown();

    bool ShouldClose() const;
private:
    static void GLFWErrorCallback(int error, const char* description);
    static void APIENTRY GLDebug(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam);

    double mLastMouseX = 0.0;
    double mLastMouseY = 0.0;
    bool mFirstMouse = true;

    Window mWindow;
    bool mRunning = true;

    Shader mShader;
    ShaderState mCurrentShader;

    struct Mesh
    {
        GLuint vao = 0;
        GLuint vbo = 0;
        GLuint ebo = 0;
        int indexCount = 0;
    };

    std::unordered_map<int, Mesh> mMeshes;
    int mNextMeshID = 1;

    std::unordered_map<int, Material> mMaterials;
    int mNextMaterialID = 1;

    ShadowMapper mShadowMapper;

    int mWidth = 0;
    int mHeight = 0;
};