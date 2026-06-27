#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Vec3.h"
#include "Mat4.h"
#include "SpatialGrid.h"
#include "Raycast.h"
#include "CollisionSolver.h"

namespace py = pybind11;

PYBIND11_MODULE(spatial_collision_engine, m)
{
    py::class_<Vec3>(m, "Vec3")
        .def(py::init<float, float, float>())
        .def_readwrite("x", &Vec3::x)
        .def_readwrite("y", &Vec3::y)
        .def_readwrite("z", &Vec3::z);

    py::class_<Mat4>(m, "Mat4")
        .def(py::init<const std::array<float, 16>&>())
        .def_readwrite("m", &Mat4::m);

    py::class_<Cell>(m, "Cell")
        .def(py::init<int, int, int>());

    py::class_<SpatialGrid>(m, "SpatialGrid")
        .def(py::init<int>())
        .def_readwrite("cellSize", &SpatialGrid::cellSize)
        .def("clear", &SpatialGrid::Clear)
        .def("world_to_cell", &SpatialGrid::WorldToCell)
        .def("insert_triangle", &SpatialGrid::InsertTriangle)
        .def("query", &SpatialGrid::Query)
        .def("insert_mesh", &SpatialGrid::InsertMesh);

    py::class_<Triangle>(m, "Triangle")
        .def(py::init<Vec3, Vec3, Vec3>())
        .def_readwrite("a", &Triangle::a)
        .def_readwrite("b", &Triangle::b)
        .def_readwrite("c", &Triangle::c);

    py::class_<Capsule>(m, "Capsule")
        .def(py::init<float, float, float>())
        .def_readwrite("radius", &Capsule::radius)
        .def_readwrite("height", &Capsule::height)
        .def_readwrite("offset", &Capsule::offset);

    py::class_<RayHit>(m, "RayHit")
        .def(py::init<Vec3, int>())
        .def_readwrite("point", &RayHit::point)
        .def_readwrite("tri_index", &RayHit::triIndex);

    m.def("raycast", &Raycast);

    py::class_<CollisionData>(m, "CollisionData")
        .def(py::init<bool, Vec3>())
        .def_readwrite("collision", &CollisionData::collision)
        .def_readwrite("collision_vector", &CollisionData::collisionVector);

    m.def("solve_capsule", &SolveCapsule);

    m.def("get_world_triangles", &GetWorldTriangles);
}