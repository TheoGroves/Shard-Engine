#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include "Vec3.h"
#include "Mat4.h"

namespace py = pybind11;

PYBIND11_MODULE(shard_maths, m)
{
    py::class_<Vec3>(m, "Vec3", py::module_local(false))
        .def(py::init<float, float, float>())
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * float())
        .def_readwrite("x", &Vec3::x)
        .def_readwrite("y", &Vec3::y)
        .def_readwrite("z", &Vec3::z);

    py::class_<Mat4>(m, "Mat4", py::module_local(false))
        .def(py::init([] {
            return Mat4::Identity();
        }))
        .def_readwrite("m", &Mat4::m)
        .def_static("identity", &Mat4::Identity);

    m.def("translate", &Translate);
    m.def("perspective", &Perspective);
    m.def("look_at", &LookAt);
    m.def("model_matrix", &ModelMatrix);
    m.def("length", &Length);
    m.def("normalize", &Normalize);
    m.def("round_to", &Round);
}