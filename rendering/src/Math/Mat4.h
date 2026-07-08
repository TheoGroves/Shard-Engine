#pragma once

#include <cmath>
#include <array>
#include "Vec3.h"

// Column-major Mat4
struct Mat4
{
    std::array<float,16> m{};

    static Mat4 Identity()
    {
        Mat4 r = {};
        r.m[0] = r.m[5] = r.m[10] = r.m[15] = 1.0f;
        return r;
    }
};

inline Mat4 operator*(const Mat4& a, const Mat4& b)
{
    Mat4 r{};

    for (int col = 0; col < 4; col++)
    {
        for (int row = 0; row < 4; row++)
        {
            r.m[col * 4 + row] =
                a.m[0 * 4 + row] * b.m[col * 4 + 0] +
                a.m[1 * 4 + row] * b.m[col * 4 + 1] +
                a.m[2 * 4 + row] * b.m[col * 4 + 2] +
                a.m[3 * 4 + row] * b.m[col * 4 + 3];
        }
    }

    return r;
}

inline Mat4 Translate(const Vec3& v)
{
    Mat4 r = Mat4::Identity();

    r.m[12] = v.x;
    r.m[13] = v.y;
    r.m[14] = v.z;

    return r;
}

inline Mat4 Perspective(float fov, float aspect, float near, float far)
{
    Mat4 r = {};

    float t = 1.0f / std::tan(fov * 0.5f);

    r.m[0] = t / aspect;
    r.m[5] = t;
    r.m[10] = (far + near) / (near - far);
    r.m[11] = -1.0f;
    r.m[14] = (2.0f * far * near) / (near - far); 
    
    return r;
}

inline Mat4 Ortho(float left, float right, float bottom, float top, float near, float far)
{
    Mat4 r = {};

    r.m[0]  = 2.0f / (right - left);
    r.m[5]  = 2.0f / (top - bottom);
    r.m[10] = -2.0f / (far - near);

    r.m[12] = -(right + left) / (right - left);
    r.m[13] = -(top + bottom) / (top - bottom);
    r.m[14] = -(far + near) / (far - near);

    r.m[15] = 1.0f;

    return r;
}

inline Mat4 LookAt(Vec3 eye, Vec3 target, Vec3 up)
{
    Vec3 f = Normalize(target - eye);
    Vec3 r = Normalize(Cross(f, up));
    Vec3 u = Normalize(Cross(r, f));

    Mat4 matrix = Mat4::Identity();

    matrix.m[0] = r.x; matrix.m[4] = r.y; matrix.m[8]  = r.z;
    matrix.m[1] = u.x; matrix.m[5] = u.y; matrix.m[9]  = u.z;
    matrix.m[2] =-f.x; matrix.m[6] =-f.y; matrix.m[10] =-f.z;

    matrix.m[12] = -Dot(r, eye);
    matrix.m[13] = -Dot(u, eye);
    matrix.m[14] =  Dot(f, eye);

    return matrix;
}