#pragma once
#include <vector>
#include "Vec3.h"
#include "CollisionData.h"
#include "Geometry.h"
#include "SpatialGrid.h"

struct ClosestResult
{
    Vec3 segmentPoint;
    Vec3 trianglePoint;
};

Vec3 ClosestPointOnTriangle(const Vec3& p, const Vec3& a, const Vec3& b, const Vec3& c);
CollisionData SphereTriangleCollision(const Vec3& centre, float radius, const Vec3& a, const Vec3& b, const Vec3& c);
Segment GetSegment(const Vec3& pos, const Capsule& capsule);
Vec3 TriangleNormal(const Vec3& a, const Vec3& b, const Vec3& c);
Segment ClosestSegmentSegment(const Segment& p, const Segment& q);
ClosestResult ClosestSegmentTriangle(const Segment& seg, const Vec3& a, const Vec3& b, const Vec3& c);
CollisionData CapsuleTriangleCollision(const Vec3& pos, const Capsule& capsule, const Vec3& a, const Vec3& b, const Vec3& c);
CollisionData SolveCapsule(Vec3& pos, const Capsule& capsule, const std::vector<Triangle>& triangles, const SpatialGrid& grid);