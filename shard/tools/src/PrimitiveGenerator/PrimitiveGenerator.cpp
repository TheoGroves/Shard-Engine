#include "PrimitiveGenerator.h"
#include "Vec3.h"
#include <string_view>
#include <vector>

constexpr std::string_view version = "0.0.1";

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
    GenerateHeader(output, "Cube");
}

void PrimitiveGenerator::GenerateSphere(float radius, unsigned int resolution) {
    GenerateHeader(output, "Sphere");
}

void PrimitiveGenerator::GenerateCylinder(float radius, float height, unsigned int resolution) {
    GenerateHeader(output, "Cylinder");
}