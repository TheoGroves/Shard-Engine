#pragma once
#include <vector>
#include "Vec4.h"
#include "Geometry.h"
#include "BVH.h"

struct RayHit
{
    Vec3 point;
    int triIndex;
    float distance;
};

float RayTriangleIntersection(const Vec3& origin, const Vec3& dir, const Vec3& v0, const Vec3& v1, const Vec3& v2);
RayHit Raycast(const Vec3& origin, const Vec3& dir, const std::vector<Triangle>& triangles, const BVH& bvh);