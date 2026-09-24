#pragma once

#include <cstddef>

struct alignas(16) vec4_raw {
    float x;
    float y;
    float z;
    float w;
};

extern "C" {
    void vec4_add(const vec4_raw* a, const vec4_raw* b, vec4_raw* result);
    void vec4_sub(const vec4_raw* a, const vec4_raw* b, vec4_raw* result);

    void vec4_mul_s(const vec4_raw* v, const float* scalar, vec4_raw* result);
    void vec4_div_s(const vec4_raw* v, const float* scalar, vec4_raw* result);

    float vec4_dot(const vec4_raw* a, const vec4_raw* b);

    void vec4_cross(const vec4_raw* a, const vec4_raw* b, vec4_raw* result);

    float vec4_length(const vec4_raw* v);
    void vec4_normalize(const vec4_raw* v, vec4_raw* result);

    void vec4_minimum(const vec4_raw* a, const vec4_raw* b, vec4_raw* result);
    void vec4_maximum(const vec4_raw* a, const vec4_raw* b, vec4_raw* result);

    void vec4_round(const vec4_raw* v, vec4_raw* result);

    void vec4_radians(const vec4_raw* v, vec4_raw* result);
    void vec4_degrees(const vec4_raw* v, vec4_raw* result);
}