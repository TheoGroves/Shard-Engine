#pragma once
#include <vector>
#include "Vec3.h"
#include "CollisionData.h"
#include "Geometry.h"
#include "SpatialGrid.h"

Vec3 ClosestPointOnTriangle(const Vec3& p, const Vec3& a, const Vec3& b, const Vec3& c);
CollisionData SphereTriangleCollision(const Vec3& centre, float radius, const Vec3& a, const Vec3& b, const Vec3& c);
Segment GetSegment(const Vec3& pos, const Capsule& capsule);
CollisionData CapsuleTriangleCollision(const Vec3& pos, const Capsule& capsule, const Vec3& a, const Vec3& b, const Vec3& c);
CollisionData SolveCapsule(Vec3& pos, const Capsule& capsule, const std::vector<Triangle>& triangles, const SpatialGrid& grid);