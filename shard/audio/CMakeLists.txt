cmake_minimum_required(VERSION 3.15)

project(shard_audio LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(
    "${CMAKE_CURRENT_SOURCE_DIR}/../maths"
    "${CMAKE_CURRENT_BINARY_DIR}/maths"
)

set(DEPS_DIR "${CMAKE_SOURCE_DIR}/dependencies")

include_directories(
    "${DEPS_DIR}/include"
)

link_directories(
    "${DEPS_DIR}/lib"
)

add_library(audio_core STATIC
    src/Core/AudioEngine.cpp
    src/Core/AudioLoader.cpp
)

target_include_directories(audio_core PUBLIC
    "${CMAKE_SOURCE_DIR}/src"
)

target_link_libraries(audio_core PUBLIC
    maths
)

if (WIN32)

    if (EXISTS "${DEPS_DIR}/lib/OpenAL32.lib")

        target_link_libraries(audio_core PUBLIC
            OpenAL32
            winmm
            avrt
        )

        target_compile_definitions(audio_core PRIVATE
            AL_LIBTYPE_STATIC
        )

    else()

        message(FATAL_ERROR
            "OpenAL32.lib not found at ${DEPS_DIR}/lib/OpenAL32.lib"
        )

    endif()

endif()

execute_process(
    COMMAND python -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_AUTO_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

if (PYBIND11_AUTO_DIR)
    set(pybind11_DIR "${PYBIND11_AUTO_DIR}")
endif()

set(PYBIND11_FINDPYTHON ON)

find_package(pybind11 REQUIRED)

pybind11_add_module(shard_audio
    src/Bindings/AudioBindings.cpp
)

target_link_libraries(shard_audio PRIVATE
    audio_core
)

set_target_properties(audio_core PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_audio"

    LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_audio"

    RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_audio"
)

set_target_properties(shard_audio PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_audio"

    RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_audio"
)