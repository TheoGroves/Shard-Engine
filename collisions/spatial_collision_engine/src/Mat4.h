#pragma once
#include <array>
#include "Vec3.h"

struct Mat4
{
    std::array<float, 16> m;
};

inline const float& M(const Mat4& mat, int row, int col)
{
    return mat.m[row * 4 + col];
}

inline Vec3 operator*(const Mat4& mat, const Vec3& v)
{
    return Vec3(
        M(mat,0,0)*v.x + M(mat,0,1)*v.y + M(mat,0,2)*v.z + M(mat,0,3),
        M(mat,1,0)*v.x + M(mat,1,1)*v.y + M(mat,1,2)*v.z + M(mat,1,3),
        M(mat,2,0)*v.x + M(mat,2,1)*v.y + M(mat,2,2)*v.z + M(mat,2,3)
    );
}