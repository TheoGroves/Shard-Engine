#include <cmath>
#include <algorithm>
#include <vector>
#include <unordered_set>
#include "CollisionSolver.h"
#include "Vec3.h"
#include "CollisionData.h"
#include "Geometry.h"
#include "SpatialGrid.h"

Vec3 ClosestPointOnTriangle(const Vec3& p, const Vec3& a, const Vec3& b, const Vec3& c)
{
    Vec3 ab = b - a;
    Vec3 ac = c - a;
    Vec3 ap = p - a;

    float d1 = Dot(ab, ap);
    float d2 = Dot(ac, ap);

    if (d1 <= 0 && d2 <= 0) {
        return a;
    }

    Vec3 bp = p - b;
    float d3 = Dot(ab, bp);
    float d4 = Dot(ac, bp);

    if (d3 >= 0 && d4 <= d3) {
        return b;
    }

    float vc = d1 * d4 - d3 * d2;
    if (vc <= 0 && d1 >= 0 && d3 <= 0) {
        float den = (d1 - d3);
        float v;

        if (std::abs(den) < 1e-8f) {
            v = 0.0f;
        } else {
            v = d1 / den;
        }

        v = std::max(0.0f, std::min(1.0f, v));
        return a + ab * v;
    }

    Vec3 cp = p - c;
    float d5 = Dot(ab, cp);
    float d6 = Dot(ac, cp);

    if (d6 >= 0 && d5 <= d6) {
        return c;
    }

    float vb = d5 * d2 - d1 * d6;
    if (vb <= 0 && d2 >= 0 && d6 <= 0) {
        float w = d2 / (d2 - d6);
        return a + ac * w;
    }

    float va = d3 * d6 - d5 * d4;
    if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0) {
        float w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        return b + (c - b) * w;
    }

    float sum = va + vb + vc;
    if (std::abs(sum ) < 1e-8f) return a;

    float denom = 1.0 / sum;
    float v = vb * denom;
    float w = vc * denom;
    return a + ab*v + ac*w;
}

CollisionData SphereTriangleCollision(const Vec3& centre, float radius, const Vec3& a, const Vec3& b, const Vec3& c) 
{
    Vec3 closest = ClosestPointOnTriangle(centre, a, b, c);

    Vec3 delta = centre - closest;
    float dist = Magnitude(delta);

    if (dist >= radius) {
        return CollisionData{false, Vec3(0,0,0)};
    }

    Vec3 normal;
    if (dist < 1e-6f) {
        normal = Vec3(0, 1, 0);
    } else {
        normal = delta / dist;
    }
    
    return CollisionData{true, normal * (radius - dist)};
}

Segment GetSegment(const Vec3& pos, const Capsule& capsule) 
{
    float half = std::max(0.0, capsule.height * 0.5 - capsule.radius);
    Vec3 p0 = pos + Vec3(0, -half + capsule.offset, 0);
    Vec3 p1 = pos + Vec3(0, half + capsule.offset, 0);

    return Segment{p0, p1};
}

CollisionData CapsuleTriangleCollision(const Vec3& pos, const Capsule& capsule, const Vec3& a, const Vec3& b, const Vec3& c)
{
    Segment seg = GetSegment(pos, capsule);

    Vec3 correction = {0.0f, 0.0f, 0.0f};

    CollisionData hit0 = SphereTriangleCollision(seg.p0, capsule.radius, a, b, c);
    CollisionData hit1 = SphereTriangleCollision(seg.p1, capsule.radius, a, b, c);

    if (hit0.collision) {
        correction += hit0.collisionVector;
    }

    if (hit1.collision) {
        correction += hit1.collisionVector;
    }

    if (Magnitude(correction) < 1e-6f) {
        return CollisionData{false, correction};
    }

    return CollisionData{true, correction};
}

CollisionData SolveCapsule(Vec3& pos, const Capsule& capsule, const std::vector<Triangle>& triangles, const SpatialGrid& grid)
{
    bool grounded = false;
    Vec3 groundedNormal = Vec3(0.0f, 0.0f, 0.0f);
    float r = capsule.radius;

    float half = capsule.height * 0.5f;

    Vec3 minBounds = pos - Vec3(r, half, r);
    Vec3 maxBounds = pos + Vec3(r, half, r);

    std::unordered_set<int> candidates = grid.Query(minBounds, maxBounds);

    for (const auto& triIndex: candidates) {
        const Triangle& tri = triangles[triIndex];

        CollisionData collisionData = CapsuleTriangleCollision(pos, capsule, tri.a, tri.b, tri.c);

        if (collisionData.collision) {
            Vec3 correction = collisionData.collisionVector;
            pos += correction;

            Vec3 n = Normalize(correction);

            if (n.y > 0.5) {
                grounded = true;
                groundedNormal = n;
            }
        }
    }

    return CollisionData{grounded, groundedNormal};
}