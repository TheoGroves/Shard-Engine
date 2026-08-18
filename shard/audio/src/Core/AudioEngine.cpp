#include "AudioEngine.h"
#include "AudioLoader.h"

void AudioEngine::Initialize()
{
    device = alcOpenDevice(nullptr);

    context = alcCreateContext(device, nullptr);

    alcMakeContextCurrent(context);

    alDopplerFactor(1.0f);
    alSpeedOfSound(343.0f);
}

ALuint AudioEngine::LoadAudio(const std::string& path)
{
    // Check if the audio has already been loaded
    auto it = buffers.find(path);

    if (it != buffers.end())
    {
        return it->second;
    }

    // Get the audio data from the .wav file
    AudioData audioData = AudioLoader::LoadWAV(path);

    // Generate a buffer and give it the data we loaded
    ALuint buffer;
    alGenBuffers(1, &buffer);

    alBufferData(
        buffer,
        audioData.format,
        audioData.data.data(),
        static_cast<ALsizei>(audioData.data.size()),
        audioData.sampleRate
    );

    // Add to cache
    buffers[path] = buffer;

    return buffer;
}

void AudioEngine::SetListener(const Vec3& position, const Vec3& velocity, const Vec3& forward, const Vec3& up)
{
    // Provide the engine with a listener location and direction to allow spatial audio and simulated doppler effect
    alListenerfv(AL_POSITION, &position.x);
    alListenerfv(AL_VELOCITY, &velocity.x);
    ALfloat orientation[] = {
        forward.x, forward.y, forward.z,
        up.x, up.y, up.z
    };

    alListenerfv(AL_ORIENTATION, orientation);
}

void AudioEngine::Play(ALuint buffer, const Vec3& position, const Vec3& velocity)
{
    // Create a source to play the sound from
    ALuint source;
    alGenSources(1, &source);

    alSourcei(source, AL_BUFFER, buffer);

    // Provide the source with position and velocity for spatial audio
    alSourcefv(source, AL_POSITION, &position.x);
    alSourcefv(source, AL_VELOCITY, &velocity.x);

    // **TODO**: implement proper distance attenuation settings
    alSourcef(source, AL_REFERENCE_DISTANCE, 1.0f);
    alSourcef(source, AL_MAX_DISTANCE, 100.0f);
    alSourcef(source, AL_ROLLOFF_FACTOR, 1.0f);

    alSourcePlay(source);

    // Add to list of sources to be deleted once the audio has finished
    sources.push_back(source);
}

void AudioEngine::Cleanup()
{
    // Loop through every source and check if it has finished.
    for (auto it = sources.begin(); it != sources.end();)
    {
        ALint state;

        alGetSourcei(*it, AL_SOURCE_STATE, &state);
        
        if (state == AL_STOPPED)
        {
            // Delete the source if it has finished
            alDeleteSources(1, &*it);
            it = sources.erase(it);
        } else
        {
            it++;
        }
    }
}

void AudioEngine::Shutdown()
{
    // Delete buffers and clear the cache
    for (const auto& [path, buffer] : buffers)
    {
        alDeleteBuffers(1, &buffer);
    }

    buffers.clear();
}