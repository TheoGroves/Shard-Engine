#include <cassert>
#include <iostream>
#include <cmath>
#include <vector>
#include "Vec3.h"
#include "CollisionSolver.h"
#include "Geometry.h"
#include "BVH.h"
#include "Raycast.h"

constexpr float EPS = 1e-5f;

void TestDotProduct()
{
    Vec3 a{1,2,3};
    Vec3 b{4,5,6};

    assert(Dot(a,b) == 32.0f);
}

void TestCrossProduct()
{
    Vec3 x{1, 0, 0};
    Vec3 y{0, 1, 0};

    Vec3 z = Cross(x,y);

    assert(z.x == 0);
    assert(z.y == 0);
    assert(z.z == 1);
}

void TestMagnitude()
{
    Vec3 v{3, 0, 4};
    assert(std::abs(Magnitude(v) - 5.0f) < EPS);
}

int main()
{
    TestMagnitude();
    TestCrossProduct();
    TestDotProduct();

    std::cout << "All Tests Passed" << std::endl;
    std::cin.get();
}