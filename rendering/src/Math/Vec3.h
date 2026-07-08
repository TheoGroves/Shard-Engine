#pragma once

#include <cmath>

struct Vec3
{
    float x, y, z;

    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}

    Vec3 operator+(const Vec3& r) const { return {x+r.x, y+r.y, z+r.z}; }
    Vec3 operator-(const Vec3& r) const { return {x-r.x, y-r.y, z-r.z}; }
    Vec3 operator*(float s) const { return {x*s, y*s, z*s}; }
    Vec3 operator/(float s) const { return {x/s, y/s, z/s}; }
};

inline float Dot(const Vec3& a, const Vec3& b)
{
    return a.x*b.x + a.y*b.y + a.z*b.z;
}

inline Vec3 Cross(const Vec3& a, const Vec3& b)
{
    return {
        a.y*b.z - a.z*b.y,
        a.z*b.x - a.x*b.z, 
        a.x*b.y - a.y*b.x
    };
}

inline float Length(const Vec3& a)
{
    return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
}

inline Vec3 Normalize(const Vec3& a)
{
    float len = Length(a);

    if (len == 0.0f) 
        return {0.0f, 0.0f, 0.0f};
        
    return {
        a.x / len, 
        a.y / len, 
        a.z / len
    };
}