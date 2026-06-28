#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Vec3.h"
#include "Mat4.h"
#include "BVH.h"
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

    py::class_<BVH>(m, "BVH")
        .def(py::init<>())
        .def("build", &BVH::Build)
        .def("query", &BVH::Query);

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