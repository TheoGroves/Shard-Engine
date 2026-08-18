#pragma once
#include <AL/al.h>
#include <AL/alc.h>
#include <string>
#include <vector>
#include <unordered_map>
#include <iostream>
#include "Vec3.h"

class AudioEngine
{
public:
    void Initialize();
    ALuint LoadAudio(const std::string& path);
    void SetListener(const Vec3& position, const Vec3& velocity, const Vec3& forward, const Vec3& up);
    void Play(ALuint buffer, const Vec3& position, const Vec3& velocity);
    void Cleanup();
    void Shutdown();
private:
    ALCdevice* device = nullptr;
    ALCcontext* context = nullptr;

    std::vector<ALuint> sources;
    std::unordered_map<std::string, ALuint> buffers;
};