#pragma once
#include <AL/al.h>
#include <AL/alc.h>
#include <vector>
#include <string>
#include <cstdint>

struct AudioData
{
    std::vector<char> data;

    ALenum format;
    ALsizei sampleRate;

    uint16_t channels;
    uint16_t bitsPerSample;
};

namespace AudioLoader
{
    AudioData LoadWAV(const std::string& path);
};