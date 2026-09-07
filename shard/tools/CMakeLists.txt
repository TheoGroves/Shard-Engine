cmake_minimum_required(VERSION 3.15)

project(tools LANGUAGES CXX)

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

add_library(tools STATIC
    src/PrimitiveGenerator/PrimitiveGenerator.cpp
)

target_include_directories(tools PUBLIC
    "${CMAKE_SOURCE_DIR}/src"
)

target_link_libraries(tools PUBLIC
    maths
)

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

pybind11_add_module(shard_tools
    src/Bindings/ToolsBindings.cpp
)

target_link_libraries(shard_tools PRIVATE
    tools
)

set_target_properties(shard_tools PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_tools"

    LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_tools"

    RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_tools"
)

set_target_properties(shard_tools PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_tools"

    RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_SOURCE_DIR}/shard_tools"
)