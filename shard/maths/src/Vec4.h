#pragma once

#include "vec4_asm.h"

class Vec4 {
protected:
    // Union means x, y, z, w occupy the same memory locations as the vec4_raw does
    union {
        vec4_raw m_data;
        struct {
            float x;
            float y;
            float z;
            float w;
        };
    };

public:
    Vec4()
        : m_data{0.0f, 0.0f, 0.0f, 0.0f} {}

    Vec4(float x, float y, float z, float w = 0.0f)
        : m_data{x, y, z, w} {}

    Vec4 operator+(const Vec4& rhs) const {
        Vec4 result;
        vec4_add(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec4 operator-(const Vec4& rhs) const {
        Vec4 result;
        vec4_sub(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec4 operator*(float scalar) const {
        Vec4 result;
        vec4_mul_s(&m_data, &scalar, &result.m_data);
        return result;
    }

    Vec4 operator/(float scalar) const {
        Vec4 result;
        vec4_div_s(&m_data, &scalar, &result.m_data);
        return result;
    }

    Vec4& operator+=(const Vec4& rhs) {
        vec4_add(&m_data, &rhs.m_data, &m_data);
        return *this;
    }

    Vec4& operator-=(const Vec4& rhs) {
        vec4_sub(&m_data, &rhs.m_data, &m_data);
        return *this;
    }

    float Dot(const Vec4& rhs) const {
        return vec4_dot(&m_data, &rhs.m_data);
    }

    Vec4 Cross(const Vec4& rhs) const {
        Vec4 result;
        vec4_cross(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    float Length() const {
        return vec4_length(&m_data);
    }

    float Magnitude() const {
        return vec4_length(&m_data);
    }

    Vec4 Normalized() const {
        Vec4 result;
        vec4_normalize(&m_data, &result.m_data);
        return result;
    }

    Vec4 Minimum(const Vec4& rhs) const {
        Vec4 result;
        vec4_minimum(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec4 Maximum(const Vec4& rhs) const {
        Vec4 result;
        vec4_maximum(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec4 Round() const {
        Vec4 result;
        vec4_round(&m_data, &result.m_data);
        return result;
    }

    Vec4 Radians() const {
        Vec4 result;
        vec4_radians(&m_data, &result.m_data);
        return result;
    }

    Vec4 Degrees() const {
        Vec4 result;
        vec4_degrees(&m_data, &result.m_data);
        return result;
    }
};

inline float Dot(const Vec4& a, const Vec4& b)
{
    return a.Dot(b);
}

inline Vec4 Cross(const Vec4& a, const Vec4& b)
{
    return a.Cross(b);
}

inline float Length(const Vec4& v)
{
    return v.Length();
}

inline float Magnitude(const Vec4& v) {
    return Length(v);
}

inline Vec4 Normalize(const Vec4& v)
{
    return v.Normalized();
}

inline Vec4 Minimum(const Vec4& a, const Vec4& b) 
{
    return a.Minimum(b);
}

inline Vec4 Maximum(const Vec4& a, const Vec4& b) 
{
    return a.Maximum(b);
}

inline Vec4 Round(const Vec4& v)
{
    return v.Round();
}

inline Vec4 Degrees(const Vec4& v)
{
    return v.Degrees();
}

inline Vec4 Radians(const Vec4& v)
{
    return v.Radians();
}

// Vec3 derives from Vec4 however only has an x, y, z component
// Internally works as a Vec4 just with w initialized as 0.0
class Vec3 : public Vec4 {
public:
    Vec3()
        : Vec4(0.0f, 0.0f, 0.0f, 0.0f) {}

    Vec3(float x, float y, float z)
        : Vec4(x, y, z, 0.0f) {}

    Vec3(const Vec4& v)
        : Vec4(v.x, v.y, v.z, 0.0f) {}

    Vec3 operator+(const Vec3& rhs) const {
        Vec3 result;
        vec4_add(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec3 operator-(const Vec3& rhs) const {
        Vec3 result;
        vec4_sub(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec3 operator*(float scalar) const {
        Vec3 result;
        vec4_mul_s(&m_data, &scalar, &result.m_data);
        return result;
    }

    Vec3 operator/(float scalar) const {
        Vec3 result;
        vec4_div_s(&m_data, &scalar, &result.m_data);
        return result;
    }

    Vec3& operator+=(const Vec3& rhs) {
        vec4_add(&m_data, &rhs.m_data, &m_data);
        return *this;
    }

    Vec3& operator-=(const Vec3& rhs) {
        vec4_sub(&m_data, &rhs.m_data, &m_data);
        return *this;
    }

    float Dot(const Vec3& rhs) const {
        return vec4_dot(&m_data, &rhs.m_data);
    }

    Vec3 Cross(const Vec3& rhs) const {
        Vec3 result;
        vec4_cross(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec3 Normalized() const {
        Vec3 result;
        vec4_normalize(&m_data, &result.m_data);
        return result;
    }

    Vec3 Minimum(const Vec3& rhs) const {
        Vec3 result;
        vec4_minimum(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec3 Maximum(const Vec3& rhs) const {
        Vec3 result;
        vec4_maximum(&m_data, &rhs.m_data, &result.m_data);
        return result;
    }

    Vec3 Round() const {
        Vec3 result;
        vec4_round(&m_data, &result.m_data);
        return result;
    }

    Vec3 Radians() const {
        Vec3 result;
        vec4_radians(&m_data, &result.m_data);
        return result;
    }

    Vec3 Degrees() const {
        Vec3 result;
        vec4_degrees(&m_data, &result.m_data);
        return result;
    }
};

// Vec3 overloads
inline float Dot(const Vec3& a, const Vec3& b)
{
    return a.Dot(b);
}

inline Vec3 Cross(const Vec3& a, const Vec3& b)
{
    return a.Cross(b);
}

inline float Length(const Vec3& v)
{
    return v.Length();
}

inline float Magnitude(const Vec3& v) {
    return Length(v);
}

inline Vec3 Normalize(const Vec3& v)
{
    return v.Normalized();
}

inline Vec3 Minimum(const Vec3& a, const Vec3& b) 
{
    return a.Minimum(b);
}

inline Vec3 Maximum(const Vec3& a, const Vec3& b) 
{
    return a.Maximum(b);
}

inline Vec3 Round(const Vec3& v)
{
    return v.Round();
}

inline Vec3 Degrees(const Vec3& v)
{
    return v.Degrees();
}

inline Vec3 Radians(const Vec3& v)
{
    return v.Radians();
}