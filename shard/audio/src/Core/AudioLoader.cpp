#include "AudioLoader.h"

#include <fstream>
#include <stdexcept>
#include <cstring>

namespace AudioLoader
{
    AudioData LoadWAV(const std::string& path)
    {
        // Load audio file as raw binary
        std::ifstream file(path, std::ios::binary);

        if (!file)
            throw std::runtime_error("Failed to open WAV file at " + path);

        // Read the header to confirm that we have a RIFF file
        char riff[4];
        file.read(riff, 4);

        if (std::strncmp(riff, "RIFF", 4) != 0)
            throw std::runtime_error("Loaded a non-RIFF file at " + path);

        // Read the size of the file
        uint32_t fileSize;
        file.read(reinterpret_cast<char*>(&fileSize), sizeof(fileSize));

        // Read the RIFF subtype to confirm we have a .wav file
        char wave[4];
        file.read(wave, 4);

        if (std::strncmp(wave, "WAVE", 4) != 0)
            throw std::runtime_error("Loaded a non-WAV RIFF file at " + path);

        uint16_t channels = 0;
        uint32_t sampleRate = 0;
        uint16_t bitsPerSample = 0;
        uint16_t audioFormat = 0;

        std::vector<char> audioData;

        // Read until "fmt" and "data" chunks are found
        bool foundFormat = false;
        bool foundData = false;

        // Search through RIFF chunks to find both the format and audio data chunks
        while (file && (!foundFormat || !foundData))
        {
            char chunkID[4];

            if (!file.read(chunkID, 4))
                break;

            uint32_t chunkSize;
            file.read(reinterpret_cast<char*>(&chunkSize), sizeof(chunkSize));

            // Process format chunk to get audio properties
            if (std::strncmp(chunkID, "fmt ", 4) == 0)
            {
                file.read(reinterpret_cast<char*>(&audioFormat), sizeof(audioFormat));
                file.read(reinterpret_cast<char*>(&channels), sizeof(channels));
                file.read(reinterpret_cast<char*>(&sampleRate), sizeof(sampleRate));

                uint32_t byteRate;
                file.read(reinterpret_cast<char*>(&byteRate), sizeof(byteRate));

                uint16_t blockAlign;
                file.read(reinterpret_cast<char*>(&blockAlign), sizeof(blockAlign));
        
                file.read(reinterpret_cast<char*>(&bitsPerSample), sizeof(bitsPerSample));

                if (chunkSize > 16)
                {
                    file.seekg(chunkSize - 16, std::ios::cur);
                }

                foundFormat = true;
            } 
            // Read the PCM audio samples from the data chunk
            else if (std::strncmp(chunkID, "data", 4) == 0)
            {
                audioData.resize(chunkSize);

                file.read(audioData.data(), chunkSize);

                foundData = true;
            } else
            {
                // Skip unkown chunks
                file.seekg(chunkSize, std::ios::cur);
            }
        }

        if (!foundFormat)
            throw std::runtime_error("WAV file has no fmt chunk at " + path);

        if (!foundData)
            throw std::runtime_error("WAV file has no data chunk at " + path);

        if (audioFormat != 1)
            throw std::runtime_error("Only uncompressed PCM WAV files are currently supported " + path);

        // Determine the OpenAL format from the data found in the fmt chunk
        ALenum format;

        if (channels == 1 && bitsPerSample == 8)
            format = AL_FORMAT_MONO8;
        else if (channels == 1 && bitsPerSample == 16)
            format = AL_FORMAT_MONO16;
        else if (channels == 2 && bitsPerSample == 8)
            format = AL_FORMAT_STEREO8;
        else if (channels == 2 && bitsPerSample == 16)
            format = AL_FORMAT_STEREO16;
        else
            throw std::runtime_error("Unsupported WAV format at " + path);

        return AudioData(
            std::move(audioData),
            format,
            static_cast<ALsizei>(sampleRate),
            channels,
            bitsPerSample
        );
    }
}