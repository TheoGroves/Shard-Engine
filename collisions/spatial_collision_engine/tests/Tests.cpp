#include <cassert>
#include <iostream>
#include <cmath>
#include <vector>
#include "Vec3.h"
#include "CollisionSolver.h"
#include "Geometry.h"
#include "SpatialGrid.h"
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

void TestSphereCollision()
{
    Triangle floor{
        {-10.0f, 0.0f, -10.0f},
        { 10.0f, 0.0f, -10.0f},
        {  0.0f, 0.0f,  10.0f}
    };

    auto hit = SphereTriangleCollision(
        Vec3(0, 0.5f, 0),
        1.0f,
        floor.a,
        floor.b,
        floor.c
    );

    assert(hit.collision);
}

void TestEmptyGrid()
{
    SpatialGrid grid(1.0f);

    auto result = grid.Query(Vec3(0,0,0), Vec3(1,1,1));

    assert(result.empty());
}

void TestSingleTriangleGrid()
{
    SpatialGrid grid(1.0f);

    grid.InsertTriangle(
        42,
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,1,0)
    );

    auto result = grid.Query(Vec3(0,0,0), Vec3(1,1,1));

    assert(result.count(42) > 0);
}

void TestGridMiss()
{
    SpatialGrid grid(1.0f);

    grid.InsertTriangle(
        42,
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,1,0)
    );

    auto result = grid.Query(Vec3(100,100,100), Vec3(101,101,101));

    assert(result.empty());
}

void TestGridClear()
{
    SpatialGrid grid(1.0f);

    grid.InsertTriangle(
        42,
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,1,0)
    );

    grid.Clear();

    auto result = grid.Query(Vec3(100,100,100), Vec3(101,101,101));

    assert(result.empty());
}

void TestRayHitTri() 
{
    std::vector<Triangle> triangles;

    triangles.push_back({
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,0,1)
    });

    SpatialGrid grid(1.0f);
    grid.InsertTriangle(0, triangles[0].a, triangles[0].b, triangles[0].c);

    RayHit hit = Raycast(
        Vec3(0.2f, 1.0f, 0.2f),
        Vec3(0, -1, 0),
        triangles,
        grid
    );

    assert(hit.triIndex == 0);
    assert(std::abs(hit.point.y) < EPS);
}

void TestRayMissTri()
{
    std::vector<Triangle> triangles;

    triangles.push_back({
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,0,1)
    });

    SpatialGrid grid(1.0f);
    grid.InsertTriangle(0, triangles[0].a, triangles[0].b, triangles[0].c);

    RayHit hit = Raycast(
        Vec3(2.0f, 1.0f, 2.0f),
        Vec3(0, -1, 0),
        triangles,
        grid
    );

    assert(hit.triIndex == -1);
}

void TestRaySelectsClosest()
{
    std::vector<Triangle> triangles;

    triangles.push_back({
        Vec3(0,0,0),
        Vec3(1,0,0),
        Vec3(0,0,1)
    });

    triangles.push_back({
        Vec3(0,5,0),
        Vec3(1,5,0),
        Vec3(0,5,1)
    });

    SpatialGrid grid(1.0f);
    grid.InsertTriangle(0, triangles[0].a, triangles[0].b, triangles[0].c);
    grid.InsertTriangle(1, triangles[1].a, triangles[1].b, triangles[1].c);

    RayHit hit = Raycast(
        Vec3(0.2f, 10.0f, 0.2f),
        Vec3(0, -1, 0),
        triangles,
        grid
    );

    assert(hit.triIndex == 1);
}

int main()
{
    TestMagnitude();
    TestCrossProduct();
    TestDotProduct();

    TestEmptyGrid();
    TestGridClear();
    TestGridMiss();
    TestSingleTriangleGrid();
    
    TestRayHitTri();
    TestRayMissTri();
    TestRaySelectsClosest();
    
    TestSphereCollision();

    std::cout << "All Tests Passed" << std::endl;
    std::cin.get();
}