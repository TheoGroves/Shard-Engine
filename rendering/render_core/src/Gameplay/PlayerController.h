#pragma once
#include "Core/Camera.h"
#include "Core/Input.h"

struct PlayerController
{
    float moveSpeed = 5.0f;
    float mouseSensitivity = 0.0025f;

    void Update(Camera& cam, const Input& input, float deltaTime)
    {
        Vec3 moveDir{0,0,0};

        if (input.forward)
            moveDir = moveDir + cam.forward;

        if (input.backward)
            moveDir = moveDir - cam.forward;

        if (input.right)
            moveDir = moveDir + cam.right;

        if (input.left)
            moveDir = moveDir - cam.right;

        if (Length(moveDir) > 0.0f)
            cam.position = cam.position + Normalize(moveDir) * moveSpeed * deltaTime;

        cam.rotation.y += input.mouseDeltaX * mouseSensitivity;
        cam.rotation.x += input.mouseDeltaY * mouseSensitivity;

        if (cam.rotation.x > 1.5f) cam.rotation.x = 1.5f;
        if (cam.rotation.x < -1.5f) cam.rotation.x = -1.5f;

        UpdateCameraVectors(cam);
    }
};