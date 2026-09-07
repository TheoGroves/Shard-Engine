#pragma once

#include <fstream>

class PrimitiveGenerator {
public:
    void GenerateQuad(float size);
    void GenerateCube(float size);
    void GenerateSphere(float radius, unsigned int resolution);
    void GenerateCylinder(float radius, float height, unsigned int resolution);
private:
    std::ofstream output;
};