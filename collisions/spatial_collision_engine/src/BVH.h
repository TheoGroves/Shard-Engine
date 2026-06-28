#pragma once
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <functional>
#include <algorithm>
#include <cstddef>
#include <cmath>
#include <cstdint>
#include "Vec3.h"
#include "Mat4.h"
#include "Geometry.h"

struct BVHNode
{
    Vec3 minBounds;
    Vec3 maxBounds;

    int left = -1;
    int right = -1;

    std::vector<int> triangleIndices;

    bool isLeaf() const { return left == -1; }
};

class BVH
{
public:
    std::vector<BVHNode> nodes;
    std::vector<Triangle> triangles;

    void Build(const std::vector<Triangle>& tris);

    std::vector<int> Query(const Vec3& minB, const Vec3& maxB) const;

private:
    int BuildNode(std::vector<int>& triIndices);
    BVHNode CreateLeaf(const std::vector<int>& triIndices);
    void QueryNode(int idx, const Vec3& minB, const Vec3& maxB, std::vector<int>& out) const;
};

std::vector<Triangle> GetWorldTriangles(const std::vector<Vec3>& vertices, const std::vector<uint32_t>& indices, const Mat4& model);