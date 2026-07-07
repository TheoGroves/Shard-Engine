#include "Engine.h"
#include <format>
#include <iostream>
#include <utility>

constexpr std::string engineVersion = "0.1.1";

#define ANSI_RESET   "\033[0m"
#define ANSI_YELLOW  "\033[33m"
#define ANSI_RED     "\033[31m"

void Engine::GLFWErrorCallback(int error, const char* description)
{
    LogError(std::format("GLFW {}: {}", error, description));
}

void APIENTRY Engine::GLDebug(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam)
{
    switch (severity)
    {
    case GL_DEBUG_SEVERITY_HIGH:
        LogError(message);
        break;
    case GL_DEBUG_SEVERITY_MEDIUM:
        LogWarning(message);
        break;
    case GL_DEBUG_SEVERITY_LOW:
        LogWarning(message);
        break;
    case GL_DEBUG_SEVERITY_NOTIFICATION:
        LogMessage(message);
        break;
    }
}

void Engine::LogMessage(std::string_view message)
{
    std::cout << ANSI_RESET << "[SYSTEM] " << message << "\n";
}

void Engine::LogWarning(std::string_view warning)
{
    std::cout << ANSI_YELLOW << "[WARNING] " << warning << ANSI_RESET << "\n";
}

void Engine::LogError(std::string_view error)
{
    std::cerr << ANSI_RED << "[ERROR] " << error << ANSI_RESET << "\n";
}

void Engine::UpdateInt(int matID, const std::string& uniform, int value)
{
    auto matIt = mMaterials.find(matID);

    if (matIt == mMaterials.end())
        return;
    
    Material& material = matIt->second;
    material.shader->SetInt(uniform, value);
}

void Engine::UpdateFloat(int matID, const std::string& uniform, float value)
{
    auto matIt = mMaterials.find(matID);

    if (matIt == mMaterials.end())
        return;
    
    Material& material = matIt->second;
    material.shader->SetFloat(uniform, value);
}

void Engine::UpdateVec3(int matID, const std::string& uniform, Vec3 value)
{
    auto matIt = mMaterials.find(matID);

    if (matIt == mMaterials.end())
        return;
    
    Material& material = matIt->second;
    material.shader->SetVec3(uniform, value);
}

void Engine::UpdateMat4(int matID, const std::string& uniform, const Mat4& matrix)
{
    auto matIt = mMaterials.find(matID);

    if (matIt == mMaterials.end())
        return;
    
    Material& material = matIt->second;
    material.shader->SetMat4(uniform, matrix);
}

GLuint Engine::CreateTextureRGBA(int width, int height, const std::vector<uint8_t>& pixels)
{
    GLuint texture;
    glCreateTextures(GL_TEXTURE_2D, 1, &texture);

    glTextureStorage2D(texture, 1, GL_RGBA8, width, height);

    glTextureSubImage2D(
        texture,
        0,
        0, 0,
        width, 
        height,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        pixels.data()
    );

    glGenerateTextureMipmap(texture);

    glTextureParameteri(texture, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTextureParameteri(texture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTextureParameteri(texture, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTextureParameteri(texture, GL_TEXTURE_WRAP_T, GL_REPEAT);

    return texture;
}

GLuint Engine::CreateTextureRGB32F(int width, int height, const std::vector<float>& pixels)
{
    GLuint texture;
    glCreateTextures(GL_TEXTURE_2D, 1, &texture);

    glTextureStorage2D(texture, 1, GL_RGB32F, width, height);

    glTextureSubImage2D(
        texture,
        0,
        0, 0,
        width, 
        height, 
        GL_RGB,
        GL_FLOAT,
        pixels.data()
    );

    glTextureParameteri(texture, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTextureParameteri(texture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTextureParameteri(texture, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTextureParameteri(texture, GL_TEXTURE_WRAP_T, GL_REPEAT);

    return texture;
}

void Engine::BindTexture(GLuint texture, GLuint unit)
{
    glBindTextureUnit(unit, texture);   
}

Input Engine::GetInput()
{
    Input input{};

    GLFWwindow* window = mWindow.GetNativeWindow();

    input.forward  = glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS;
    input.backward = glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS;
    input.left     = glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS;
    input.right    = glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS;

    double x, y;
    glfwGetCursorPos(window, &x, &y);

    if (mFirstMouse)
    {
        mLastMouseX = x;
        mLastMouseY = y;
        mFirstMouse = false;
    }

    input.mouseDeltaX = static_cast<float>(x - mLastMouseX);
    input.mouseDeltaY = static_cast<float>(mLastMouseY - y);

    mLastMouseX = x;
    mLastMouseY = y;

    return input;
}

bool Engine::Initialize(unsigned int screenWidth, unsigned int screenHeight, std::string title)
{
    LogMessage(std::format("SHARD RENDERER v{}", engineVersion));
    LogMessage(std::format("Compiled on: {} at {}", (std::string)__DATE__,  __TIME__));

    glfwSetErrorCallback(GLFWErrorCallback);

    if (!glfwInit())
    {
        LogError("Failed to initialize GLFW.");
        return false;
    }
    LogMessage("GLFW initialized successfully.");

    if (!mWindow.Create(screenWidth, screenHeight, title))
    {
        glfwTerminate();
        LogError("Failed to create OpenGL context.");
        return false;
    }

    LogMessage(std::format("Created Window of size {}x{}", screenWidth, screenHeight));

    if (glewInit() != GLEW_OK)
    {
        LogError("Failed to initialize GLEW.");
        glfwTerminate();
        return false;
    }
    LogMessage("GLEW initialized successfully.");

    mShadowMapper.CreateResources();

    glEnable(GL_DEBUG_OUTPUT);
    glDebugMessageCallback(GLDebug, nullptr);

    const GLubyte* vendor   = glGetString(GL_VENDOR);
    const GLubyte* renderer = glGetString(GL_RENDERER);
    const GLubyte* version  = glGetString(GL_VERSION);

    LogMessage(std::format("GPU Vendor: {}", reinterpret_cast<const char*>(vendor)));
    LogMessage(std::format("Renderer  : {}", reinterpret_cast<const char*>(renderer)));
    LogMessage(std::format("GL Version: {}", reinterpret_cast<const char*>(version)));

    glClearColor(0.05f, 0.07f, 0.09f, 1.0f);

    mWidth  = screenWidth;
    mHeight = screenHeight;

    return true;
}

void Engine::BeginFrame()
{
    glEnable(GL_DEPTH_TEST);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void Engine::EndFrame()
{
    mWindow.SwapBuffers();
    mWindow.PollEvents();
}

int Engine::CreateMesh(const float* vertices, size_t vertexFloatCount, const uint32_t* indices, size_t indexCount)
{
    Mesh mesh{};

    glGenVertexArrays(1, &mesh.vao);
    glBindVertexArray(mesh.vao);
    
    glGenBuffers(1, &mesh.vbo);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.vbo);
    glBufferData(
        GL_ARRAY_BUFFER,
        vertexFloatCount * sizeof(float),
        vertices,
        GL_STATIC_DRAW
    );

    glGenBuffers(1, &mesh.ebo);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.ebo);
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, 
        indexCount * sizeof(uint32_t),
        indices, 
        GL_STATIC_DRAW
    );

    constexpr GLsizei stride = 11 * sizeof(float);

    // position
    glVertexAttribPointer(
        0, 
        3, 
        GL_FLOAT, 
        GL_FALSE, 
        stride, 
        (void*)0
    );
    glEnableVertexAttribArray(0);

    // uv map
    glVertexAttribPointer(
        1, 
        2, 
        GL_FLOAT, 
        GL_FALSE, 
        stride, 
        (void*)(3 * sizeof(float))
    );
    glEnableVertexAttribArray(1);

    // normals
    glVertexAttribPointer(
        2, 
        3, 
        GL_FLOAT, 
        GL_FALSE, 
        stride, 
        (void*)(5 * sizeof(float))
    );
    glEnableVertexAttribArray(2);

    // tangents
    glVertexAttribPointer(
        3, 
        3, 
        GL_FLOAT, 
        GL_FALSE, 
        stride, 
        (void*)(8 * sizeof(float))
    );
    glEnableVertexAttribArray(3);

    mesh.indexCount = static_cast<GLsizei>(indexCount);

    int id = mNextMeshID++;
    mMeshes[id] = mesh;

    return id;
}

int Engine::CreateMaterial(const std::string& frag, const std::string& vert)
{
    auto shader = std::make_shared<Shader>();
    shader->LoadFromFile(vert, frag);

    Material mat;
    mat.shader = shader;

    int id = mNextMaterialID++;
    mMaterials[id] = std::move(mat);

    return id;
}

void Engine::DrawMesh(int meshID, int materialID, const Mat4& model)
{
    auto meshIt = mMeshes.find(meshID);
    auto matIt = mMaterials.find(materialID);

    if (meshIt == mMeshes.end() || matIt == mMaterials.end())
        return;
    
    Mesh& mesh = meshIt->second;
    Material& material = matIt->second;

    material.shader->Use();

    material.shader->SetMat4("uModel", model);

    glBindVertexArray(mesh.vao);
    glDrawElements(GL_TRIANGLES, mesh.indexCount, GL_UNSIGNED_INT, 0);
}

void Engine::BeginShadows(Vec3 lightDir, Vec3 target)
{
    mShadowMapper.Update(lightDir, target);
    mShadowMapper.BeginRender();
}

void Engine::EndShadows()
{
    mShadowMapper.EndRender(mWidth, mHeight);
}

Mat4 Engine::GetLightSpaceMatrix() const
{
    return mShadowMapper.GetLightSpaceMatrix();
}

GLuint Engine::GetShadowDepth() const
{
    return mShadowMapper.GetDepthTexture();
}

void Engine::DrawShadow(int meshID, const Mat4& model)
{
    auto meshIt = mMeshes.find(meshID);
    if (meshIt == mMeshes.end())
        return;

    Mesh& mesh = meshIt->second;

    mShadowMapper.RenderDepthMesh(mesh.vao, mesh.indexCount, model);
}

GLFWwindow* Engine::GetNativeWindow() const
{
    return mWindow.GetNativeWindow();
}

void Engine::DisableDepthMask()
{
    glDepthMask(GL_FALSE);
}

void Engine::EnableDepthMask()
{
    glDepthMask(GL_TRUE);
}

void Engine::DisableCullFace()
{
    glDisable(GL_CULL_FACE);
}

void Engine::EnableCullFace()
{
    glEnable(GL_CULL_FACE);
}

void Engine::DisableDepthTest()
{
    glDisable(GL_DEPTH_TEST);
}

void Engine::EnableDepthTest()
{
    glEnable(GL_DEPTH_TEST);
}

void Engine::HideMouse()
{
    glfwSetInputMode(GetNativeWindow(), GLFW_CURSOR, GLFW_CURSOR_DISABLED);
}

void Engine::ShowMouse()
{
    glfwSetInputMode(GetNativeWindow(), GLFW_CURSOR, GLFW_CURSOR_NORMAL);
}

bool Engine::ShouldClose() const
{
    return mWindow.ShouldClose();
}

void Engine::Shutdown()
{
    LogMessage("Engine shutting down.");

    mWindow.Destroy();
    glfwTerminate();
    mRunning = false;

    LogMessage("Engine shutdown complete.");
}