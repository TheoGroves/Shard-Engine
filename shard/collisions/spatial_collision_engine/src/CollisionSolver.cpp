#include <cmath>
#include <algorithm>
#include <vector>
#include <unordered_set>
#include <cfloat>
#include "CollisionSolver.h"
#include "Vec3.h"
#include "CollisionData.h"
#include "Geometry.h"
#include "BVH.h"

constexpr float EPS = 1e-6f;
constexpr float overFetch = 2.0f;

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
    float half = std::max(0.0f, capsule.height * 0.5f - capsule.radius);
    Vec3 p0 = pos + Vec3(0, -half + capsule.offset, 0);
    Vec3 p1 = pos + Vec3(0, half + capsule.offset, 0);

    return Segment{p0, p1};
}

Vec3 TriangleNormal(const Vec3& a, const Vec3& b, const Vec3& c)
{
    return Normalize(Cross(b-a, c-a));
}

Segment ClosestSegmentSegment(const Segment& p, const Segment& q)
{
    Vec3 d1 = p.p1 - p.p0;
    Vec3 d2 = q.p1 - q.p0;
    Vec3 r  = p.p0 - q.p0;

    float a = Dot(d1, d1);
    float e = Dot(d2, d2);
    float f = Dot(d2, r);

    float s, t;

    if (a < EPS && e < EPS)
        return {p.p0, q.p0};

    if (a < EPS) {
        s = 0.0f;
        t = std::clamp(f / e, 0.0f, 1.0f);
    }
    else {
        float c = Dot(d1, r);

        if ( e < EPS) {
            t = 0.0f;
            s = std::clamp(-c/a, 0.0f, 1.0f);
        } else {
            float b = Dot(d1, d2);
            float denom = a*e - b*b;

            if (denom > EPS)
                s = std::clamp((b*f - c*e) / denom, 0.0f, 1.0f);
            else
                s = 0.0f;
            
            t = (b*s + f) / e;

            if (t < 0.0f) {
                t = 0.0f;
                s = std::clamp(-c/a, 0.0f, 1.0f);
            } else if (t > 1.0f) {
                t = 1.0f;
                s = std::clamp((b-c)/a, 0.0f, 1.0f);
            }
        }
    }

    return {
        p.p0 + d1*s,
        q.p0 + d2*t
    };
}

ClosestResult ClosestSegmentTriangle(const Segment& seg, const Vec3& a, const Vec3& b, const Vec3& c)
{
    ClosestResult best;
    float bestDistSq = FLT_MAX;

    auto Test = [&](const Vec3& s, const Vec3& t)
    {
        float d2 = Dot(s - t, s - t);

        if (d2 < bestDistSq)
        {
            bestDistSq = d2;
            best.segmentPoint = s;
            best.trianglePoint = t;
        }
    };

    Test(seg.p0, ClosestPointOnTriangle(seg.p0, a, b, c));
    Test(seg.p1, ClosestPointOnTriangle(seg.p1, a, b, c));

    Segment r = ClosestSegmentSegment(seg, {a,b});
    Test(r.p0, r.p1);

    r = ClosestSegmentSegment(seg, {b, c});
    Test(r.p0, r.p1);

    r = ClosestSegmentSegment(seg, {c, a});
    Test(r.p0, r.p1);

    return best;
}

CollisionData CapsuleTriangleCollision(const Vec3& pos, const Capsule& capsule, const Vec3& a, const Vec3& b, const Vec3& c)
{
    Segment seg = GetSegment(pos, capsule);

    ClosestResult r = ClosestSegmentTriangle(seg, a, b, c);

    Vec3 delta = r.segmentPoint - r.trianglePoint;

    float d = Magnitude(delta);

    if (d >= capsule.radius)
        return {false, {}};

    Vec3 normal;

    if (d < EPS)
        normal = TriangleNormal(a,b,c);
    else
        normal = delta / d;

    return {true, normal * (capsule.radius - d)};
}

CollisionData SolveCapsule(Vec3& pos, const Capsule& capsule, const std::vector<Triangle>& triangles, const BVH& bvh)
{
    bool grounded = false;
    Vec3 groundedNormal = Vec3(0.0f, 0.0f, 0.0f);
    float r = capsule.radius;

    float half = capsule.height * 0.5f;

    Vec3 minBounds = pos - Vec3(r*overFetch, half*overFetch, r*overFetch);
    Vec3 maxBounds = pos + Vec3(r*overFetch, half*overFetch, r*overFetch);

    std::vector<int> candidates = bvh.Query(minBounds, maxBounds);

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