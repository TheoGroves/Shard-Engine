#include <cmath>
#include <unordered_set>
#include "Raycast.h"
#include "Vec3.h"
#include "Geometry.h"
#include "SpatialGrid.h"

float RayTriangleIntersection(const Vec3& origin, const Vec3& dir, const Vec3& v0, const Vec3& v1, const Vec3& v2)
{
    constexpr float EPS = 1e-8f;

    Vec3 edge1 = v1 - v0;
    Vec3 edge2 = v2 - v0;

    Vec3 h = Cross(dir, edge2);
    float a = Dot(edge1, h);

    if (std::abs(a) < EPS) {
        return -1.0f;
    }

    float f = 1.0f / a;
    Vec3 s = origin - v0;
    float u = f * Dot(s, h);

    if (u < 0.0f || u > 1.0f) {
        return -1.0f;
    }
    
    Vec3 q = Cross(s, edge1);
    float v = f * Dot(dir, q);

    if (v < 0.0f || u + v > 1.0f) {
        return -1.0f;
    }

    float t = f * Dot(edge2, q);

    if (t > EPS) {
        return t;
    }

    return -1.0f;
}

RayHit Raycast(const Vec3& origin, const Vec3& dir, const std::vector<Triangle>& triangles, const SpatialGrid& grid)
{
    float bestT = INFINITY;
    RayHit rayHit;
    rayHit.point = origin;
    rayHit.triIndex = -1;
    Triangle hitTri;

    std::unordered_set<int> candidates = grid.Query(Minimum(origin, origin + dir * 1000), Maximum(origin, origin + dir * 1000));

    for (const auto& triIndex: candidates) {
        const Triangle& tri = triangles[triIndex];

        float t = RayTriangleIntersection(origin, dir, tri.a, tri.b, tri.c);

        if (t > 0.0 && t < bestT) {
            bestT = t;
            rayHit.point = origin + dir * t;
            rayHit.triIndex = triIndex;
        }
    }

    return rayHit;
}