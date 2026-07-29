#include <iostream>
#include <cstdint>
#include <algorithm>
#include "BVH.h"
#include "Vec3.h"
#include "Mat4.h"
#include "Geometry.h"

std::vector<Triangle> GetWorldTriangles(const std::vector<Vec3>& vertices, const std::vector<uint32_t>& indices, const Mat4& model)
{
    std::vector<Triangle> tris;

    for (size_t i = 0; i < indices.size(); i += 3) {
        uint32_t i0 = indices[i];
        uint32_t i1 = indices[i+1];
        uint32_t i2 = indices[i+2];

        Vec3 p0 = model * vertices[i0];
        Vec3 p1 = model * vertices[i1];
        Vec3 p2 = model * vertices[i2];

        tris.emplace_back(Triangle{p0, p1, p2});
    }

    return tris;
}

void BVH::Build(const std::vector<Triangle>& tris)
{
    triangles = tris;

    std::vector<int> indices(tris.size());
    for (int i = 0; i < (int)tris.size(); i++)
        indices[i] = i;
    
    nodes.clear();
    BuildNode(indices);
}

int BVH::BuildNode(std::vector<int>& triIndices)
{
    BVHNode node;

    // Calculate bounds
    node.minBounds = Vec3{1e9f, 1e9f, 1e9f};
    node.maxBounds = Vec3{-1e9f, -1e9f, -1e9f};

    for (int i : triIndices) {
        const Triangle& t = triangles[i];

        node.minBounds = Minimum(node.minBounds, Minimum(Minimum(t.a, t.b), t.c));
        node.maxBounds = Maximum(node.maxBounds, Maximum(Maximum(t.a, t.b), t.c));
    }

    // Check if is leaf
    if (triIndices.size() <= 8) {
        node.triangleIndices = triIndices;
        nodes.push_back(node);
        return (int)nodes.size() - 1;
    }

    // Choose split axis
    Vec3 extent = node.maxBounds - node.minBounds;

    int axis = 0;
    if (extent.y > extent.x) axis = 1;
    if (extent.z > (axis == 0 ? extent.x : extent.y)) axis = 2;

    // Sort by centroid location
    std::sort(triIndices.begin(), triIndices.end(),
        [&](int a, int b) 
        {
        Vec3 ca = (triangles[a].a + triangles[a].b + triangles[a].c) / 3.0f;
        Vec3 cb = (triangles[b].a + triangles[b].b + triangles[b].c) / 3.0f;

        return (&ca.x)[axis] < (&cb.x)[axis];
        });
    
    int mid = triIndices.size() / 2;

    std::vector<int> leftTris(triIndices.begin(), triIndices.begin() + mid);
    std::vector<int> rightTris(triIndices.begin() + mid, triIndices.end());

    int nodeIndex = nodes.size();
    nodes.push_back(node);

    int leftIndex = BuildNode(leftTris);
    int rightIndex = BuildNode(rightTris);

    nodes[nodeIndex].left = leftIndex;
    nodes[nodeIndex].right = rightIndex;

    return nodeIndex;
}

void BVH::QueryNode(int idx, const Vec3& minB, const Vec3& maxB, std::vector<int>& out) const 
{
    const BVHNode& node = nodes[idx];

    if (node.maxBounds.x < minB.x || node.minBounds.x > maxB.x) return;
    if (node.maxBounds.y < minB.y || node.minBounds.y > maxB.y) return;
    if (node.maxBounds.z < minB.z || node.minBounds.z > maxB.z) return;

    if (node.isLeaf()) 
    {
        out.insert(out.end(), node.triangleIndices.begin(), node.triangleIndices.end());
        return;
    }

    QueryNode(node.left, minB, maxB, out);
    QueryNode(node.right, minB, maxB, out);
}

std::vector<int> BVH::Query(const Vec3& minB, const Vec3& maxB) const
{
    std::vector<int> out;
    if (!nodes.empty())
        QueryNode(0, minB, maxB, out);
    return out;
}