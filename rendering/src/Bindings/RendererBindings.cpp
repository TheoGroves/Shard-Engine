#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "Core/Engine.h"
#include "Core/Camera.h"
#include "Gameplay/PlayerController.h"
#include "Rendering/Viewport.h"

namespace py = pybind11;

PYBIND11_MODULE(shard_render_engine, m)
{
    py::module_ maths = py::module_::import("shard_maths");

    py::class_<Engine>(m, "Engine")
        .def(py::init<>())
        .def("initialize", &Engine::Initialize)

        .def("create_mesh", 
            [](Engine& engine,
                py::array_t<float, py::array::c_style | py::array::forcecast> vertices,
                py::array_t<uint32_t, py::array::c_style | py::array::forcecast> indices)
            {
                auto v = vertices.request();
                auto i = indices.request();

                return engine.CreateMesh(
                    static_cast<float*>(v.ptr),
                    static_cast<size_t>(v.size),
                    static_cast<uint32_t*>(i.ptr),
                    static_cast<size_t>(i.size)
                );
            })

        .def("update_int", &Engine::UpdateInt)
        .def("update_float", &Engine::UpdateFloat)
        .def("update_vec3", &Engine::UpdateVec3)
        .def("update_mat4", &Engine::UpdateMat4)

        .def("create_texture_rgba",
        [](Engine& engine, py::array_t<uint8_t, py::array::c_style | py::array::forcecast> image)
        {
            auto buf = image.request();

            if (buf.ndim != 3 || buf.shape[2] != 4)
                engine.LogError("Expected HxWx4 image");

            int height = static_cast<int>(buf.shape[0]);
            int width  = static_cast<int>(buf.shape[1]);

            auto* ptr = static_cast<uint8_t*>(buf.ptr);

            std::vector<uint8_t> pixels(
                ptr,
                ptr + width * height * 4
            );

            return engine.CreateTextureRGBA(width, height, pixels);
        })

        .def("create_texture_rgb32f",
        [](Engine& engine, py::array_t<float, py::array::c_style | py::array::forcecast> image)
        {
            auto buf = image.request();

            if (buf.ndim != 3 || buf.shape[2] != 3)
                engine.LogError("Expected HxWx4 image");

            int height = static_cast<int>(buf.shape[0]);
            int width  = static_cast<int>(buf.shape[1]);

            auto* ptr = static_cast<float*>(buf.ptr);

            std::vector<float> pixels(
                ptr,
                ptr + width * height * 3
            );

            return engine.CreateTextureRGB32F(width, height, pixels);
        })

        .def("consume_logs", &Engine::ConsumeLogs)
        .def("bind_texture", &Engine::BindTexture)
        .def("get_input", &Engine::GetInput)
        .def("should_close", &Engine::ShouldClose)
        .def("begin_frame", &Engine::BeginFrame)
        .def("create_material", &Engine::CreateMaterial)
        .def("draw_mesh", &Engine::DrawMesh)
        .def("get_shadow_depth", &Engine::GetShadowDepth)
        .def("get_light_space", &Engine::GetLightSpaceMatrix)
        .def("begin_shadows", &Engine::BeginShadows)
        .def("end_shadows", &Engine::EndShadows)
        .def("draw_shadow", &Engine::DrawShadow)
        .def("begin_window", &Engine::Begin)
        .def("end_window", &Engine::End)
        .def("text", &Engine::Text)
        .def("text_coloured", &Engine::TextColoured)
        .def("button", &Engine::Button)
        .def("slider_float", &Engine::SliderFloat)
        .def("slider_int", &Engine::SliderInt)
        .def("checkbox", &Engine::Checkbox)
        .def("same_line", &Engine::SameLine)
        .def("separator", &Engine::Separator)
        .def("image", &Engine::Image)
        .def("begin_child", &Engine::BeginChild)
        .def("end_child", &Engine::EndChild)
        .def("tree_node", &Engine::TreeNode)
        .def("tree_node_ex", &Engine::TreeNodeEx)
        .def("tree_pop", &Engine::TreePop)
        .def("is_item_clicked", &Engine::IsItemClicked)
        .def("selectable", &Engine::Selectable)
        .def("collapsing_header", &Engine::CollapsingHeader)
        .def("input_text", &Engine::InputText)
        .def("begin_popup_context_item", &Engine::BeginPopupContextItem)
        .def("end_popup", &Engine::EndPopup)
        .def("menu_item", &Engine::MenuItem)
        .def("get_available_region", &Engine::GetAvailableRegion)
        .def("get_width", &Engine::GetWidth)
        .def("get_height", &Engine::GetHeight)
        .def("disable_depth_mask", &Engine::DisableDepthMask)
        .def("enable_depth_mask", &Engine::EnableDepthMask)
        .def("disable_cull_face", &Engine::DisableCullFace)
        .def("enable_cull_face", &Engine::EnableCullFace)
        .def("disable_depth_test", &Engine::DisableDepthTest)
        .def("enable_depth_test", &Engine::EnableDepthTest)
        .def("hide_mouse", &Engine::HideMouse)
        .def("show_mouse", &Engine::ShowMouse)
        .def("end_frame", &Engine::EndFrame)
        .def("shutdown", &Engine::Shutdown);

    py::class_<Camera>(m, "Camera")
        .def(py::init<>())

        .def_readwrite("position", &Camera::position)
        .def_readwrite("forward", &Camera::forward)
        .def_readwrite("up", &Camera::up)
        .def_readwrite("right", &Camera::right)
        .def_readwrite("world_up", &Camera::worldUp)
        .def_readwrite("rotation", &Camera::rotation)

        .def_readwrite("fov", &Camera::fov)
        .def_readwrite("aspect", &Camera::aspect)
        .def_readwrite("near_plane", &Camera::nearPlane)
        .def_readwrite("far_plane", &Camera::farPlane)

        .def("get_view", &Camera::GetView)
        .def("get_projection", &Camera::GetProjection);
        
    m.def("forward_from_euler", &ForwardFromEuler);
    m.def("update_camera_vectors", &UpdateCameraVectors);

    py::class_<Input>(m, "Input")
        .def(py::init<>())
        .def_readwrite("forward", &Input::forward)
        .def_readwrite("backward", &Input::backward)
        .def_readwrite("left", &Input::left)
        .def_readwrite("right", &Input::right)
        .def_readwrite("up", &Input::up)
        .def_readwrite("down", &Input::down)
        .def_readwrite("jump", &Input::jump)
        .def_readwrite("sprint", &Input::sprint)
        .def_readwrite("escape", &Input::escape)
        .def_readwrite("mouse_dx", &Input::mouseDeltaX)
        .def_readwrite("mouse_dy", &Input::mouseDeltaY);

    py::class_<PlayerController>(m, "PlayerController")
        .def(py::init<>())
        .def_readwrite("move_speed", &PlayerController::moveSpeed)
        .def_readwrite("mouse_sensitivity", &PlayerController::mouseSensitivity)
        .def("update", &PlayerController::Update);

    py::class_<LogEntry>(m, "LogEntry")
        .def_readonly("text", &LogEntry::text)
        .def_readonly("level", &LogEntry::level);

    py::enum_<LogEntry::Level>(m, "LogLevel")
        .value("Trace", LogEntry::Level::Trace)
        .value("Debug", LogEntry::Level::Debug)
        .value("Info", LogEntry::Level::Info)
        .value("Warning", LogEntry::Level::Warning)
        .value("Error", LogEntry::Level::Error)
        .value("Fatal", LogEntry::Level::Fatal)
        .export_values();

    py::class_<Viewport>(m, "Viewport")
        .def(py::init<>())
        .def("create", &Viewport::Create)
        .def("destroy", &Viewport::Destroy)
        .def("resize", &Viewport::Resize)
        .def("bind", &Viewport::Bind)
        .def("unbind", &Viewport::Unbind)

        .def_readonly("fbo", &Viewport::fbo)
        .def_readonly("colour", &Viewport::colour)
        .def_readonly("depth", &Viewport::depth)
        .def_readonly("width", &Viewport::width)
        .def_readonly("height", &Viewport::height);
}