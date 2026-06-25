#pragma once
#include <algorithm>
#include <cmath>

struct Vec3
{
    float x;
    float y;
    float z;

    Vec3() = default;
    Vec3(float x_, float y_, float z_)
        : x(x_), y(y_), z(z_) {}

    Vec3& operator+=(const Vec3& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
};

inline Vec3 operator+(const Vec3& a, const Vec3& b)
{
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

inline Vec3 operator-(const Vec3& a, const Vec3& b)
{
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}

inline Vec3 operator*(const Vec3& a, float b)
{
    return {a.x * b, a.y * b, a.z * b};
}

inline Vec3 operator/(const Vec3& a, float b)
{
    return a * (1.0f / b);
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

inline float Dot(const Vec3& a, const Vec3& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline Vec3 Cross(const Vec3& a, const Vec3& b)
{
    return Vec3{
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

inline float Magnitude(const Vec3& a)
{
    return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
}

inline Vec3 Normalize(const Vec3& a)
{
    float length = Magnitude(a);

    if (length > 0.0f) {
        float invLength = 1.0f / length;
        return {
            a.x * invLength,
            a.y * invLength,
            a.z * invLength
        };
    }

    return {0.0f, 0.0f, 0.0f};
}