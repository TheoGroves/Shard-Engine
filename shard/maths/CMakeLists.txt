cmake_minimum_required(VERSION 3.15)

project(maths LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(maths INTERFACE)

target_include_directories(maths INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

execute_process(
    COMMAND python -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_AUTO_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)

if(PYBIND11_AUTO_DIR)
    set(pybind11_DIR "${PYBIND11_AUTO_DIR}")
endif()

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

find_program(NASM_EXECUTABLE nasm REQUIRED)

set(VEC4_ASM ${CMAKE_CURRENT_SOURCE_DIR}/src/vec4.asm)
set(VEC4_OBJ ${CMAKE_CURRENT_BINARY_DIR}/vec4.obj)

add_custom_command(
    OUTPUT ${VEC4_OBJ}
    COMMAND ${NASM_EXECUTABLE}
            -f win64
            ${VEC4_ASM}
            -o ${VEC4_OBJ}
    DEPENDS ${VEC4_ASM}
    COMMENT "Assembling vec4.asm"
)

add_custom_target(vec4_asm DEPENDS ${VEC4_OBJ})

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)

    execute_process(
        COMMAND python -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE PYBIND11_AUTO_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )

    if(PYBIND11_AUTO_DIR)
        set(pybind11_DIR "${PYBIND11_AUTO_DIR}")
    endif()

    set(PYBIND11_FINDPYTHON ON)
    find_package(pybind11 REQUIRED)

    pybind11_add_module(shard_maths
        bindings/MathsBindings.cpp
        ${VEC4_OBJ}
    )

    add_dependencies(shard_maths vec4_asm)

    target_link_libraries(shard_maths PRIVATE maths)

    set_target_properties(shard_maths PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/python"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/python"
    )

endif()