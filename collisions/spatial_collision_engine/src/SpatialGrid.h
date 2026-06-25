#pragma once
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <functional>
#include <algorithm>
#include <cstddef>
#include <cmath>
#include "Vec3.h"

struct Cell {
    int x;
    int y;
    int z;

    bool operator==(const Cell& other) const noexcept
    {
        return x == other.x &&
               y == other.y &&
               z == other.z; 
    }
};

struct CellHash {
    size_t operator()(const Cell& c) const noexcept {
        size_t h1 = std::hash<int>{}(c.x);
        size_t h2 = std::hash<int>{}(c.y);
        size_t h3 = std::hash<int>{}(c.z);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }
};

class SpatialGrid
{
private:
    std::unordered_map<Cell, std::vector<int>, CellHash> cells;
public:
    float cellSize;

    SpatialGrid(float cellSize);
    void Clear();
    Cell WorldToCell(const Vec3& p) const;
    void InsertTriangle(unsigned int triIndex, Vec3 a, Vec3 b, Vec3 c);
    std::unordered_set<int> Query(Vec3 minBounds, Vec3 maxBounds) const;
};