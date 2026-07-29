#pragma once

#include <cmath>
#include <array>
#include <immintrin.h>
#include "Vec3.h"

// Column-major Mat4
struct alignas(16) Mat4
{
    std::array<float,16> m{};

    static Mat4 Identity()
    {
        Mat4 r = {};
        r.m[0] = r.m[5] = r.m[10] = r.m[15] = 1.0f;
        return r;
    }
};

// SIMD matrix-matrix multiplication
inline Mat4 operator*(const Mat4& a, const Mat4& b)
{
    Mat4 r{};

    // Load columns
    __m128 a0 = _mm_load_ps(&a.m[0]);
    __m128 a1 = _mm_load_ps(&a.m[4]);
    __m128 a2 = _mm_load_ps(&a.m[8]);
    __m128 a3 = _mm_load_ps(&a.m[12]);

    #ifdef __FMA__
        // Column 0
        __m128 c0 = _mm_mul_ps(_mm_set1_ps(b.m[0]), a0);
        c0 = _mm_fmadd_ps(_mm_set1_ps(b.m[1]), a1, c0);
        c0 = _mm_fmadd_ps(_mm_set1_ps(b.m[2]), a2, c0);
        c0 = _mm_fmadd_ps(_mm_set1_ps(b.m[3]), a3, c0);
        _mm_store_ps(&r.m[0], c0);

        // Column 1
        __m128 c1 = _mm_mul_ps(_mm_set1_ps(b.m[4]), a0);
        c1 = _mm_fmadd_ps(_mm_set1_ps(b.m[5]), a1, c1);
        c1 = _mm_fmadd_ps(_mm_set1_ps(b.m[6]), a2, c1);
        c1 = _mm_fmadd_ps(_mm_set1_ps(b.m[7]), a3, c1);
        _mm_store_ps(&r.m[4], c1);

        // Column 2
        __m128 c2 = _mm_mul_ps(_mm_set1_ps(b.m[8]), a0);
        c2 = _mm_fmadd_ps(_mm_set1_ps(b.m[9]), a1, c2);
        c2 = _mm_fmadd_ps(_mm_set1_ps(b.m[10]), a2, c2);
        c2 = _mm_fmadd_ps(_mm_set1_ps(b.m[11]), a3, c2);
        _mm_store_ps(&r.m[8], c2);

        // Column 3
        __m128 c3 = _mm_mul_ps(_mm_set1_ps(b.m[12]), a0);
        c3 = _mm_fmadd_ps(_mm_set1_ps(b.m[13]), a1, c3);
        c3 = _mm_fmadd_ps(_mm_set1_ps(b.m[14]), a2, c3);
        c3 = _mm_fmadd_ps(_mm_set1_ps(b.m[15]), a3, c3);
        _mm_store_ps(&r.m[12], c3);
    #else
        // Column 0
        __m128 c0 = _mm_mul_ps(_mm_set1_ps(b.m[0]), a0);
        c0 = _mm_add_ps(c0, _mm_mul_ps(_mm_set1_ps(b.m[1]), a1));
        c0 = _mm_add_ps(c0, _mm_mul_ps(_mm_set1_ps(b.m[2]), a2));
        c0 = _mm_add_ps(c0, _mm_mul_ps(_mm_set1_ps(b.m[3]), a3));
        _mm_store_ps(&r.m[0], c0);

        // Column 1
        __m128 c1 = _mm_mul_ps(_mm_set1_ps(b.m[4]), a0);
        c1 = _mm_add_ps(c1, _mm_mul_ps(_mm_set1_ps(b.m[5]), a1));
        c1 = _mm_add_ps(c1, _mm_mul_ps(_mm_set1_ps(b.m[6]), a2));
        c1 = _mm_add_ps(c1, _mm_mul_ps(_mm_set1_ps(b.m[7]), a3));
        _mm_store_ps(&r.m[4], c1);

        // Column 2
        __m128 c2 = _mm_mul_ps(_mm_set1_ps(b.m[8]), a0);
        c2 = _mm_add_ps(c2, _mm_mul_ps(_mm_set1_ps(b.m[9]), a1));
        c2 = _mm_add_ps(c2, _mm_mul_ps(_mm_set1_ps(b.m[10]), a2));
        c2 = _mm_add_ps(c2, _mm_mul_ps(_mm_set1_ps(b.m[11]), a3));
        _mm_store_ps(&r.m[8], c2);

        // Column 3
        __m128 c3 = _mm_mul_ps(_mm_set1_ps(b.m[12]), a0);
        c3 = _mm_add_ps(c3, _mm_mul_ps(_mm_set1_ps(b.m[13]), a1));
        c3 = _mm_add_ps(c3, _mm_mul_ps(_mm_set1_ps(b.m[14]), a2));
        c3 = _mm_add_ps(c3, _mm_mul_ps(_mm_set1_ps(b.m[15]), a3));
        _mm_store_ps(&r.m[12], c3);
    #endif

    return r;
}

// SIMD matrix-vector multiplication
inline Vec3 operator*(const Mat4& m, const Vec3& v)
{
    // Load columns
    __m128 m0 = _mm_load_ps(&m.m[0]);
    __m128 m1 = _mm_load_ps(&m.m[4]);
    __m128 m2 = _mm_load_ps(&m.m[8]);
    __m128 m3 = _mm_load_ps(&m.m[12]);

    // Calculate transformed vector
    __m128 res = _mm_mul_ps(_mm_set1_ps(v.x), m0);

    #ifdef __FMA__
        res = _mm_fmadd_ps(_mm_set1_ps(v.y), m1, res);
        res = _mm_fmadd_ps(_mm_set1_ps(v.z), m2, res);
    #else
        res = _mm_add_ps(res, _mm_mul_ps(_mm_set1_ps(v.y), m1));
        res = _mm_add_ps(res, _mm_mul_ps(_mm_set1_ps(v.z), m2));
    #endif

    res = _mm_add_ps(res, m3);

    // Store as scalar
    alignas(16) float outFloats[4];
    _mm_store_ps(outFloats, res);

    return Vec3(outFloats[0], outFloats[1], outFloats[2]);
}

inline Mat4 Translate(const Vec3& v)
{
    Mat4 r = Mat4::Identity();

    r.m[12] = v.x;
    r.m[13] = v.y;
    r.m[14] = v.z;

    return r;
}

inline Mat4 Scale(const Vec3& s) 
{
    Mat4 r = Mat4::Identity();

    r.m[0] =  s.x;
    r.m[5] =  s.y;
    r.m[10] = s.z;

    return r;
}

inline Mat4 RotateX(float rad)
{
    Mat4 r = Mat4::Identity();

    float c = std::cos(rad);
    float s = std::sin(rad);

    r.m[5] =   c;
    r.m[6] =   s;
    r.m[9] =  -s;
    r.m[10] =  c;

    return r;
}

inline Mat4 RotateY(float rad)
{
    Mat4 r = Mat4::Identity();

    float c = std::cos(rad);
    float s = std::sin(rad);

    r.m[0] =  c;
    r.m[2] = -s;
    r.m[8] =  s;
    r.m[10] = c;

    return r;
}

inline Mat4 RotateZ(float rad)
{
    Mat4 r = Mat4::Identity();

    float c = std::cos(rad);
    float s = std::sin(rad);

    r.m[0] = c;
    r.m[1] = s;
    r.m[4] = -s;
    r.m[5] = c;

    return r;
}

inline Mat4 ModelMatrix(const Vec3& position, const Vec3& rotation, const Vec3& scale)
{
    return Translate(position) * RotateZ(rotation.z) * RotateY(rotation.y) * RotateX(rotation.x) * Scale(scale);
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