cmake_minimum_required(VERSION 3.15)
project(spatial_collision_engine)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(pybind11 REQUIRED)

add_library(spatial_core
    src/SpatialGrid.cpp
    src/Raycast.cpp
    src/CollisionSolver.cpp
)

target_include_directories(spatial_core PUBLIC
    ${CMAKE_SOURCE_DIR}/src
)

pybind11_add_module(spatial_collision_engine
    bindings/CollisionBindings.cpp
)

target_link_libraries(spatial_collision_engine PRIVATE spatial_core)

set_target_properties(spatial_collision_engine PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR}/python
    LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR}/python
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR}/python
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR}/python
)

add_executable(engine_tests
    tests/Tests.cpp
)

target_link_libraries(engine_tests PRIVATE spatial_core)