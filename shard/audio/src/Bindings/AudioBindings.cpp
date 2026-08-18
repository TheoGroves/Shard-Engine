#include <pybind11/pybind11.h>
#include <Core/AudioEngine.h>

namespace py = pybind11;

PYBIND11_MODULE(shard_audio, m)
{
    py::module_ maths = py::module_::import("shard_maths");

    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())

        .def("initialize", &AudioEngine::Initialize)
        .def("load_audio", &AudioEngine::LoadAudio)
        .def("set_listener", &AudioEngine::SetListener)
        .def("play", &AudioEngine::Play)
        .def("cleanup", &AudioEngine::Cleanup)
        .def("shutdown", &AudioEngine::Shutdown);
}