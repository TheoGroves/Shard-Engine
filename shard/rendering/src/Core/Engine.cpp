#include "Engine.h"
#include "imgui.h"
#include "backends/imgui_impl_glfw.h"
#include "backends/imgui_impl_opengl3.h"
#include <format>
#include <iostream>
#include <utility>

#define ANSI_RESET   "\033[0m"
#define ANSI_YELLOW  "\033[33m"
#define ANSI_RED     "\033[31m"
#define ANSI_GREY    "\033[90m"
#define ANSI_CYAN    "\033[36m"
#define ANSI_GREEN   "\033[32m"
#define ANSI_BRIGHT_RED  "\033[91m"

Engine* Engine::sInstance = nullptr;

void Engine::GLFWErrorCallback(int error, const char* description)
{
    if (sInstance)
        sInstance->LogError(std::format("GLFW {}: {}", error, description));
}

void APIENTRY Engine::GLDebug(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam)
{
    if (!sInstance)
        return;

    switch (severity)
    {
    case GL_DEBUG_SEVERITY_HIGH:
        sInstance->LogError(message);
        break;
    case GL_DEBUG_SEVERITY_MEDIUM:
        sInstance->LogWarning(message);
        break;
    case GL_DEBUG_SEVERITY_LOW:
        sInstance->LogMessage(message);
        break;
    case GL_DEBUG_SEVERITY_NOTIFICATION:
        break;
    }
}

void Engine::LogMessage(std::string_view message)
{
    mPendingLogs.push_back({ LogEntry::Level::Info, std::string(message) });
}

void Engine::LogDebug(std::string_view message) 
{
    mPendingLogs.push_back({ LogEntry::Level::Debug, std::string(message) });
}

void Engine::LogWarning(std::string_view warning)
{
    mPendingLogs.push_back({ LogEntry::Level::Warning, std::string(warning) });
}

void Engine::LogError(std::string_view error)
{
    mPendingLogs.push_back({ LogEntry::Level::Error, std::string(error) });
}

std::vector<LogEntry> Engine::ConsumeLogs()
{
    auto logs = std::move(mPendingLogs);
    mPendingLogs.clear();
    return logs;
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

    ImGuiIO& io = ImGui::GetIO();

    if (!io.WantCaptureKeyboard)
    {
        input.forward  = glfwGetKey(window, GLFW_KEY_W)          == GLFW_PRESS;
        input.backward = glfwGetKey(window, GLFW_KEY_S)          == GLFW_PRESS;
        input.left     = glfwGetKey(window, GLFW_KEY_A)          == GLFW_PRESS;
        input.right    = glfwGetKey(window, GLFW_KEY_D)          == GLFW_PRESS;
        input.up       = glfwGetKey(window, GLFW_KEY_E)          == GLFW_PRESS;
        input.down     = glfwGetKey(window, GLFW_KEY_Q)          == GLFW_PRESS;
        input.jump     = glfwGetKey(window, GLFW_KEY_SPACE)      == GLFW_PRESS;
        input.sprint   = glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS;
        input.escape   = glfwGetKey(window, GLFW_KEY_ESCAPE)     == GLFW_PRESS;
    }

    double x, y;
    glfwGetCursorPos(window, &x, &y);

    if (mFirstMouse)
    {
        mLastMouseX = x;
        mLastMouseY = y;
        mFirstMouse = false;
    }

    int cursorMode = glfwGetInputMode(window, GLFW_CURSOR);

    if (io.WantCaptureMouse && cursorMode == GLFW_CURSOR_NORMAL)
    {
        input.mouseDeltaX = 0.0f;
        input.mouseDeltaY = 0.0f;
    } else 
    {
        input.mouseDeltaX = static_cast<float>(x - mLastMouseX);
        input.mouseDeltaY = static_cast<float>(mLastMouseY - y);
    }

    mLastMouseX = x;
    mLastMouseY = y;

    return input;
}

bool Engine::Initialize(unsigned int screenWidth, unsigned int screenHeight, std::string title)
{
    sInstance = this;

    glfwSetErrorCallback(GLFWErrorCallback);

    if (!glfwInit())
    {
        this->LogError("Failed to initialize GLFW.");
        return false;
    }
    this->LogDebug("GLFW initialized successfully.");

    if (!mWindow.Create(screenWidth, screenHeight, title))
    {
        glfwTerminate();
        this->LogError("Failed to create OpenGL context.");
        return false;
    }

    this->LogMessage(std::format("Created Window of size {}x{}", screenWidth, screenHeight));

    if (glewInit() != GLEW_OK)
    {
        this->LogError("Failed to initialize GLEW.");
        glfwTerminate();
        return false;
    }
    this->LogDebug("GLEW initialized successfully.");

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    (void)io;

    io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
    io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;

    ImGui::StyleColorsDark();

    ImGui_ImplGlfw_InitForOpenGL(GetNativeWindow(), true);
    ImGui_ImplOpenGL3_Init("#version 460 core");

    this->LogDebug("ImGui initialized successfully.");

    mShadowMapper.CreateResources();

    glEnable(GL_DEBUG_OUTPUT);
    glDebugMessageCallback(GLDebug, nullptr);

    const GLubyte* vendor   = glGetString(GL_VENDOR);
    const GLubyte* renderer = glGetString(GL_RENDERER);
    const GLubyte* version  = glGetString(GL_VERSION);

    this->LogMessage(std::format("GPU Vendor: {}", reinterpret_cast<const char*>(vendor)));
    this->LogMessage(std::format("Renderer  : {}", reinterpret_cast<const char*>(renderer)));
    this->LogMessage(std::format("GL Version: {}", reinterpret_cast<const char*>(version)));

    glClearColor(0.05f, 0.07f, 0.09f, 1.0f);

    mWidth  = screenWidth;
    mHeight = screenHeight;

    return true;
}

// Rendering
void Engine::BeginFrame()
{
    mWindow.PollEvents();

    glEnable(GL_DEPTH_TEST);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    ImGuiWindowFlags window_flags = ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoDocking;

    const ImGuiViewport* viewport = ImGui::GetMainViewport();

    ImGui::SetNextWindowPos(viewport->WorkPos);
    ImGui::SetNextWindowSize(viewport->WorkSize);
    ImGui::SetNextWindowViewport(viewport->ID);

    window_flags |=
        ImGuiWindowFlags_NoTitleBar |
        ImGuiWindowFlags_NoCollapse |
        ImGuiWindowFlags_NoResize |
        ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoBringToFrontOnFocus |
        ImGuiWindowFlags_NoNavFocus;

    ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);

    ImGui::Begin("DockSpace", nullptr, window_flags);

    ImGui::PopStyleVar(2);

    ImGuiID dockspace_id = ImGui::GetID("MainDockSpace");
    ImGui::DockSpace(dockspace_id, ImVec2(0.0f, 0.0f));
}

void Engine::EndFrame()
{
    ImGui::End();

    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

    ImGuiIO& io = ImGui::GetIO();

    if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable)
    {
        GLFWwindow* backup = glfwGetCurrentContext();
        ImGui::UpdatePlatformWindows();
        ImGui::RenderPlatformWindowsDefault();

        glfwMakeContextCurrent(backup);
    }

    mWindow.SwapBuffers();
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

// Shadowmapping
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

// UI
bool Engine::Begin(const char* name)
{
    return ImGui::Begin(name);
}

void Engine::End()
{
    ImGui::End();
}

void Engine::Text(const char* text)
{
    ImGui::Text("%s", text);
}

void Engine::TextColoured(const char* text, Vec3 col)
{
    ImGui::TextColored(ImVec4(col.x, col.y, col.z, 1.0f), "%s", text);
}

bool Engine::Button(const char* label, float width, float height)
{
    return ImGui::Button(label, ImVec2(width, height));
}

float Engine::SliderFloat(const char* label, float& value, float min, float max)
{
    ImGui::SliderFloat(label, &value, min, max);
    return value;
}

int Engine::SliderInt(const char* label, int& value, int min, int max)
{
    ImGui::SliderInt(label, &value, min, max);
    return value;
}

std::pair<bool, bool> Engine::Checkbox(const char* label, bool value)
{
    bool changed = ImGui::Checkbox(label, &value);

    return { changed, value };
}

void Engine::SameLine()
{
    ImGui::SameLine();
}

void Engine::Separator()
{
    ImGui::Separator();
}

void Engine::Image(GLuint texture, float width, float height)
{
    ImGui::Image((ImTextureID)(intptr_t)texture, ImVec2(width, height), ImVec2(0,1), ImVec2(1,0));
}

void Engine::BeginChild(const char* name, float width, float height)
{
    ImGui::BeginChild(name, ImVec2(width, height), true);
}

void Engine::EndChild()
{
    ImGui::EndChild();
}

bool Engine::TreeNode(const char* label)
{
    return ImGui::TreeNode(label);
}

bool Engine::TreeNodeEx(const char* id, const char* label, int flags)
{
    return ImGui::TreeNodeEx(id, static_cast<ImGuiTreeNodeFlags>(flags), "%s", label);
}

void Engine::TreePop()
{
    ImGui::TreePop();
}

bool Engine::IsItemClicked()
{
    return ImGui::IsItemClicked();
}

bool Engine::IsWindowClicked()
{
    return ImGui::IsWindowHovered() && ImGui::IsMouseClicked(ImGuiMouseButton_Left);
}

bool Engine::Selectable(const char* label, bool selected)
{
    return ImGui::Selectable(label, selected);
}

bool Engine::CollapsingHeader(const char* label)
{
    return ImGui::CollapsingHeader(label);
}

std::pair<bool, std::string> Engine::InputText(const char* label, const std::string& value)
{
    auto& buffer = mInputBuffers[label];

    if (buffer[0] == '\0')
    {
        strncpy(buffer.data(), value.c_str(), buffer.size());
        buffer[buffer.size() - 1] = '\0';
    }

    bool changed = ImGui::InputText(
        label,
        buffer.data(),
        buffer.size()
    );

    return { changed, std::string(buffer.data()) };
}

bool Engine::BeginPopupContextItem()
{
    return ImGui::BeginPopupContextItem();
}

bool Engine::BeginPopup(const char* id)
{
    return ImGui::BeginPopup(id);
}

void Engine::EndPopup()
{
    ImGui::EndPopup();
}

bool Engine::MenuItem(const char* label)
{
    return ImGui::MenuItem(label);
}

std::pair<bool, float> Engine::DragFloat(const char* label, float value, float speed, float min, float max)
{
    float original = value;

    bool changed = ImGui::DragFloat(
        label,
        &value,
        speed,
        min,
        max
    );

    return { changed, value };
}

bool Engine::DragFloat3(const char* label, Vec3& v, float speed, float min, float max)
{
    return ImGui::DragFloat3(label, &v.x, speed, min, max, "%.1f");
}

std::pair<bool, int> Engine::DragInt(const char* label, int value, float speed, int min, int max)
{
    bool changed = ImGui::DragInt(
        label,
        &value,
        speed,
        min,
        max
    );

    return { changed, value };
}

bool Engine::ColourEdit3(const char* label, Vec3& colour)
{
    return ImGui::ColorEdit3(label, &colour.x);
}

void Engine::SeparatorText(const char* text)
{
    ImGui::SeparatorText(text);
}

void Engine::PushID(int id)
{
    ImGui::PushID(id);
}

void Engine::PushID(const char* id)
{
    ImGui::PushID(id);
}

void Engine::PopId()
{
    ImGui::PopID();
}

void Engine::OpenPopup(const char* id)
{
    ImGui::OpenPopup(id);
}

bool Engine::ImageButton(const char* id, GLuint texture, float width, float height)
{
    return ImGui::ImageButton(id, (ImTextureID)(intptr_t)texture, ImVec2(width, height), ImVec2(0,1), ImVec2(1,0));
}

bool Engine::IsItemHovered()
{
    return ImGui::IsItemHovered();
}

void Engine::SetNextItemWidth(float width)
{
    ImGui::SetNextItemWidth(width);
}

void Engine::BeginDisabled(bool disabled)
{
    ImGui::BeginDisabled(disabled);
}

void Engine::EndDisabled()
{
    ImGui::EndDisabled();
}

void Engine::SetTooltip(const char* text)
{
    ImGui::SetTooltip("%s", text);
}

void Engine::BeginTooltip()
{
    ImGui::BeginTooltip();
}

void Engine::EndTooltip()
{
    ImGui::EndTooltip();
}

void Engine::ScrollToBottom()
{
    ImGui::SetScrollHereY(1.0f);
}

Vec3 Engine::GetAvailableRegion()
{
    ImVec2 size = ImGui::GetContentRegionAvail();

    return Vec3(size.x, size.y, 0.0f);
}

bool Engine::BeginDragDropSource()
{
    return ImGui::BeginDragDropSource();
}

void Engine::EndDragDropSource()
{
    return ImGui::EndDragDropSource();
}

bool Engine::BeginDragDropTarget()
{
    return ImGui::BeginDragDropTarget();
}

int Engine::AcceptDragDropPayload(const char* type)
{
    const ImGuiPayload* payload = ImGui::AcceptDragDropPayload(type);

    if (!payload)
        return -1;

    if (payload->DataSize != sizeof(int))
        return -1;

    return *static_cast<int*>(payload->Data);
}
void Engine::EndDragDropTarget()
{
    ImGui::EndDragDropTarget();
}

bool Engine::BeginPopupContextWindow()
{
    return ImGui::BeginPopupContextWindow(nullptr, ImGuiPopupFlags_NoOpenOverItems);
}

void Engine::SetDragDropPayload(const char* type, int id)
{
    ImGui::SetDragDropPayload(type, &id, sizeof(int));
}

void Engine::Dummy(float width, float height)
{
    return ImGui::Dummy(ImVec2(width, height));
}

bool Engine::BeginMenuBar()
{
    return ImGui::BeginMenuBar();
}

bool Engine::BeginMenu(const char* label)
{
    return ImGui::BeginMenu(label);
}

void Engine::EndMenu()
{
    ImGui::EndMenu();
}

void Engine::EndMenuBar()
{
    ImGui::EndMenuBar();
}

// Helpers
GLFWwindow* Engine::GetNativeWindow() const
{
    return mWindow.GetNativeWindow();
}

int Engine::GetWidth()
{
    return mWidth;
}

int Engine::GetHeight()
{
    return mHeight;
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
    this->LogMessage("Engine shutting down.");

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    mWindow.Destroy();
    glfwTerminate();

    mRunning = false;

    this->LogMessage("Engine shutdown complete.");

    sInstance = nullptr;
}