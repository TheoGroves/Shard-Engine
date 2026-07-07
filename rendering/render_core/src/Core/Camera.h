#pragma once

#include <numbers>
#include "Math/Vec3.h"
#include "Math/Mat4.h"

constexpr float degToRad = std::numbers::pi_v<float> / 180.0f;

struct Camera
{
    Vec3 position = {0, 0, 0};
    Vec3 forward  = {0, 0, 1};
    Vec3 up       = {0, 1, 0};
    Vec3 right    = {1, 0, 0};
    Vec3 worldUp  = {0, 1, 0};

    Vec3 rotation = {0, 0, 0};

    float fov = 70 * degToRad;
    float aspect = 1.778f;
    float nearPlane = 0.1f;
    float farPlane = 100.0f;

    Mat4 GetView() const
    {
        return LookAt(position, position + forward, up);
    }

    Mat4 GetProjection() const 
    {
        return Perspective(fov, aspect, nearPlane, farPlane);
    }
};

inline Vec3 ForwardFromEuler(const Vec3& rot)
{
    float pitch = rot.x;
    float yaw   = rot.y;

    float cp = cosf(pitch);
    float sp = sinf(pitch);
    float cy = cosf(yaw);
    float sy = sinf(yaw);

    Vec3 forward;

    forward.x = cy * cp;
    forward.y = sp;
    forward.z = sy * cp;

    return Normalize(forward);
}

inline void UpdateCameraVectors(Camera& cam)
{
    cam.forward = ForwardFromEuler(cam.rotation);
    cam.right = Normalize(Cross(cam.forward, cam.worldUp));
    cam.up = Normalize(Cross(cam.right, cam.forward));
}