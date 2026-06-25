#include <iostream>
#include "SpatialGrid.h"
#include "Vec3.h"

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