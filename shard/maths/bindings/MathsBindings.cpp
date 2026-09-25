#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include "Vec4.h"
#include "Mat4.h"

namespace py = pybind11;

PYBIND11_MODULE(shard_maths, m)
{
    py::class_<Vec3>(m, "Vec3", py::module_local(false))
        .def(py::init<float, float, float>())
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * float())
        .def_property(
            "x",
            [](const Vec3& v) { return v.x; },
            [](Vec3& v, float value) { v.x = value; }
        )
        .def_property(
            "y",
            [](const Vec3& v) { return v.y; },
            [](Vec3& v, float value) { v.y = value; }
        )
        .def_property(
            "z",
            [](const Vec3& v) { return v.z; },
            [](Vec3& v, float value) { v.z = value; }
        );

    py::class_<Mat4>(m, "Mat4", py::module_local(false))
        .def(py::init([] {
            return Mat4::Identity();
        }))
        .def(py::self * py::self)
        .def_readwrite("m", &Mat4::m)
        .def_static("identity", &Mat4::Identity);

    m.def("translate", &Translate);
    m.def("perspective", &Perspective);
    m.def("look_at", &LookAt);
    m.def("model_matrix", &ModelMatrix);
    m.def("length", static_cast<float (*)(const Vec3&)>(&Length));
    m.def("normalize", static_cast<Vec3 (*)(const Vec3&)>(&Normalize));
    m.def("round_to", static_cast<Vec3 (*)(const Vec3&)>(&Round));
    m.def("cross", static_cast<Vec3 (*)(const Vec3&, const Vec3&)>(&Cross));
    m.def("degrees", static_cast<Vec3 (*)(const Vec3&)>(&Degrees));
    m.def("radians", static_cast<Vec3 (*)(const Vec3&)>(&Radians));
}