#include "PrimitiveGenerator.h"
#include "Vec3.h"
#include <string_view>
#include <vector>

constexpr std::string_view version = "0.0.2";

static void GenerateHeader(std::ofstream& output, const char* primitiveType) {
    output << "# Shard Primitive Generator v" << version << '\n';
    output << "o " << primitiveType << '\n';
}

void PrimitiveGenerator::GenerateQuad(float size) {
    const float offset = size / 2;

    output = std::ofstream("assets\\models\\Quad.obj");

    GenerateHeader(output, "Quad");

    // Generate vertices
    std::vector<Vec3> vertices = {
        {-offset, 0.0, -offset},
        {-offset, 0.0,  offset},
        {offset,  0.0,  offset},
        {offset,  0.0, -offset}
    };

    for (auto& vertex : vertices) {
        output << "v " << vertex.x << ' ' << vertex.y << ' ' << vertex.z << '\n';
    }

    // Generate vertex normal, all vertices use same upwards normal
    output << "vn 0.0 1.0 0.0\n";

    // Generate texture coordinates
    std::vector<Vec3> uvs = {
        {0.0, 0.0, 0.0},
        {0.0, 1.0, 0.0},
        {1.0, 1.0, 0.0},
        {1.0, 0.0, 0.0}
    };

    for (auto& coord : uvs) {
        output << "vt " << coord.x << ' ' << coord.y << '\n';
    }

    // Generate one quad out of all 4 points, asset manager will convert to triangles
    output << "f 1/1/1 2/2/1 3/3/1 4/4/1\n";
}

void PrimitiveGenerator::GenerateCube(float size) {
    output = std::ofstream("assets\\models\\Cube.obj");

    const float offset = size / 2;

    GenerateHeader(output, "Cube");

    // Generate vertices
    std::vector<Vec3> vertices = {
        {-offset, -offset, -offset},
        {-offset, -offset,  offset},
        { offset, -offset,  offset},
        { offset, -offset, -offset},
        {-offset,  offset, -offset},
        {-offset,  offset,  offset},
        { offset,  offset,  offset},
        { offset,  offset, -offset},
    };

    for (auto& vertex : vertices) {
        output << "v " << vertex.x << ' ' << vertex.y << ' ' << vertex.z << '\n';
    }

    // Generate vertex normals
    std::vector<Vec3> normals = {
        { 0.0, -1.0,  0.0},
        { 0.0,  1.0,  0.0},
        { 0.0,  0.0,  1.0},
        { 0.0,  0.0, -1.0},
        {-1.0,  0.0,  0.0},
        { 1.0,  0.0,  0.0}
    };

    for (auto& normal : normals) {
        output << "vn " << normal.x << ' ' << normal.y << ' ' << normal.z << '\n';
    }

    // Generate texture coordinates
    std::vector<Vec3> uvs = {
        {0.0, 0.0, 0.0},
        {1.0, 0.0, 0.0},
        {1.0, 1.0, 0.0},
        {0.0, 1.0, 0.0}
    };

    for (auto& coord : uvs) {
        output << "vt " << coord.x << ' ' << coord.y << '\n';
    }

    output << "f 1/1/1 4/2/1 3/3/1 2/4/1\n";
    output << "f 5/1/2 6/2/2 7/3/2 8/4/2\n";
    output << "f 2/1/3 3/2/3 7/3/3 6/4/3\n";
    output << "f 4/1/4 1/2/4 5/3/4 8/4/4\n";
    output << "f 1/1/5 2/2/5 6/3/5 5/4/5\n";
    output << "f 3/1/6 4/2/6 8/3/6 7/4/6\n";
}

void PrimitiveGenerator::GenerateSphere(float radius, unsigned int resolution) {
    output = std::ofstream("assets\\models\\Sphere.obj");

    GenerateHeader(output, "Sphere");
}

void PrimitiveGenerator::GenerateCylinder(float radius, float height, unsigned int resolution) {
    output = std::ofstream("assets\\models\\Cylinder.obj");

    GenerateHeader(output, "Cylinder");
}