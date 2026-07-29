#pragma once
#include "Vec3.h"

struct Segment {
    Vec3 p0;
    Vec3 p1;
};

struct Triangle {
    Vec3 a;
    Vec3 b;
    Vec3 c;
};

struct Capsule {
    float radius;
    float height;
    float offset;
};