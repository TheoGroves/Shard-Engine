#pragma once

#include <GLFW/glfw3.h>
#include <string>

class Window
{
public:
    Window() = default;
    ~Window();

    bool Create(int width, int height, const std::string& title);
    void Destroy();

    bool ShouldClose() const;
    void PollEvents() const;
    void SwapBuffers() const;

    GLFWwindow* GetNativeWindow() const;

private:
    GLFWwindow* mWindow = nullptr;

    int mWidth = 0;
    int mHeight = 0;
};