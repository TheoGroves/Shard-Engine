#include <pybind11/pybind11.h>
#include <PrimitiveGenerator/PrimitiveGenerator.h>

namespace py = pybind11;

PYBIND11_MODULE(shard_tools, m)
{
    py::module_ maths = py::module_::import("shard_maths");

    py::class_<PrimitiveGenerator>(m, "PrimitiveGenerator")
        .def(py::init<>())

        .def("generate_quad", &PrimitiveGenerator::GenerateQuad)
        .def("generate_cube", &PrimitiveGenerator::GenerateCube)
        .def("generate_sphere", &PrimitiveGenerator::GenerateSphere)
        .def("generate_cylinder", &PrimitiveGenerator::GenerateCylinder);
}