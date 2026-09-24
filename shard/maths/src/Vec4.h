#pragma once

#include "vec4_asm.h"

class Vec4 {
private:
    vec4_raw m_data;

public:
    float x;
    float y;
    float z;
    float w;

    Vec4()
        : x(0.0f), y(0.0f), z(0.0f), w(0.0f) {}

    Vec4(float x, float y, float z, float w = 0.0f)
        : x(x), y(y), z(z), w(w) {}

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

using Vec3 = Vec4;

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