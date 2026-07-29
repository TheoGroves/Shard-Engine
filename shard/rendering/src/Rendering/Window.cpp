#include "Window.h"
#include <iostream>

bool Window::Create(int width, int height, const std::string& title)
{
    mWidth = width;
    mHeight = height;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    mWindow = glfwCreateWindow(width, height, title.c_str(), nullptr, nullptr);

    if (!mWindow)
        return false;

    glfwMakeContextCurrent(mWindow);

    glfwSwapInterval(0);

    return true;
}

Window::~Window()
{
    Destroy();
}

void Window::Destroy()
{
    if (mWindow)
    {
        glfwDestroyWindow(mWindow);
        mWindow = nullptr;
    }
}

bool Window::ShouldClose() const
{
    return glfwWindowShouldClose(mWindow);
}

void Window::PollEvents() const
{
    glfwPollEvents();
}

void Window::SwapBuffers() const
{
    glfwSwapBuffers(mWindow);
}

GLFWwindow* Window::GetNativeWindow() const
{
    return mWindow;
}