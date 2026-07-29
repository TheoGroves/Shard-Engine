#pragma once

#include <cmath>
#include <algorithm>

constexpr float PI = 3.14159f;

struct Vec3
{
    float x, y, z;

    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}

    Vec3 operator+(const Vec3& r) const { return {x+r.x, y+r.y, z+r.z}; }
    Vec3 operator-(const Vec3& r) const { return {x-r.x, y-r.y, z-r.z}; }
    Vec3 operator*(float s) const { return {x*s, y*s, z*s}; }
    Vec3 operator/(float s) const { return {x/s, y/s, z/s}; }

    Vec3& operator+=(const Vec3& other)
    {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }

    Vec3& operator-=(const Vec3& other)
    {
        x -= other.x;
        y -= other.y;
        z -= other.z;
        return *this;
    }
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

inline float Magnitude(const Vec3& a)
{
    return Length(a);
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

inline Vec3 Minimum(const Vec3& a, const Vec3& b)
{
    return {
        std::min(a.x, b.x),
        std::min(a.y, b.y),
        std::min(a.z, b.z)
    };
}

inline Vec3 Maximum(const Vec3& a, const Vec3& b)
{
    return {
        std::max(a.x, b.x),
        std::max(a.y, b.y),
        std::max(a.z, b.z)
    };
}

inline Vec3 Round(const Vec3& v, unsigned int digits = 0)
{
    float factor = std::pow(10.0f, digits);
    return {
        std::round(v.x * factor) / factor,
        std::round(v.y * factor) / factor,
        std::round(v.z * factor) / factor
    };
}

inline Vec3 Radians(const Vec3& v)
{
    return {
        v.x * (PI / 180),
        v.y * (PI / 180),
        v.z * (PI / 180)
    };
}

inline Vec3 Degrees(const Vec3& v)
{
    return {
        v.x * (180 / PI),
        v.y * (180 / PI),
        v.z * (180 / PI)
    };
}