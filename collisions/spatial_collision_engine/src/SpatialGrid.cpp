#include <iostream>
#include <cstdint>
#include "SpatialGrid.h"
#include "Vec3.h"
#include "Mat4.h"
#include "Geometry.h"

SpatialGrid::SpatialGrid(float cs)
    : cellSize(cs)
{
}

void SpatialGrid::Clear()
{
    cells.clear();
}

Cell SpatialGrid::WorldToCell(const Vec3& p) const
{
    return Cell{
        static_cast<int>(std::floor(p.x / cellSize)),
        static_cast<int>(std::floor(p.y / cellSize)),
        static_cast<int>(std::floor(p.z / cellSize))
    };
}

void SpatialGrid::InsertTriangle(unsigned int triIndex, Vec3 a, Vec3 b, Vec3 c)
{
    Vec3 minBounds = Minimum(Minimum(a, b), c);
    Vec3 maxBounds = Maximum(Maximum(a, b), c);

    Cell minCell = WorldToCell(minBounds);
    Cell maxCell = WorldToCell(maxBounds);

    for (int x = minCell.x; x <= maxCell.x; x++)
    {
        for (int y = minCell.y; y <= maxCell.y; y++)
        {
            for (int z = minCell.z; z <= maxCell.z; z++)
            {
                cells[Cell{x,y,z}].push_back(triIndex);
            }
        }
    }
}

std::unordered_set<int> SpatialGrid::Query(Vec3 minBounds, Vec3 maxBounds) const
{
    std::unordered_set<int> results;

    results.reserve(512);

    Cell minCell = WorldToCell(minBounds);
    Cell maxCell = WorldToCell(maxBounds);

    for (int x = minCell.x; x <= maxCell.x; x++)
    {
        for (int y = minCell.y; y <= maxCell.y; y++)
        {
            for (int z = minCell.z; z <= maxCell.z; z++)
            {
                Cell c{x, y, z};
                auto it = cells.find(c);
                if (it != cells.end())
                {
                    results.insert(it->second.begin(), it->second.end());
                }
            }
        }
    }

    return results;
}

std::vector<Triangle> SpatialGrid::InsertMesh(const std::vector<Vec3>& vertices, const std::vector<uint32_t>& indices, const Mat4& model)
{
    std::vector<Triangle> tris;

    for (const Triangle& tri : GetWorldTriangles(vertices, indices, model)) {
        unsigned int idx = static_cast<unsigned int>(tris.size());

        tris.push_back(tri);

        InsertTriangle(idx, tri.a, tri.b, tri.c);
    }

    return tris;
}

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

