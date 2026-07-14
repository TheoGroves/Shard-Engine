#pragma once

struct Input
{
    bool forward = false;
    bool backward = false;
    bool left = false;
    bool right = false;
    bool up = false;
    bool down = false;
    bool jump = false;
    bool sprint = false;

    float mouseDeltaX = 0.0f;
    float mouseDeltaY = 0.0f;
};