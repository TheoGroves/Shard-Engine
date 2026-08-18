import ctypes
import traceback

# Load maths onto path
import shard.maths.python

# Editor
from editor.console import Console
from editor.viewport import ViewportUI
from editor.hierarchy import Hierarchy
from editor.inspector import Inspector
from editor.profiler import Profiler
from editor.main_menu import MainMenu

# Core
from shard.core import AssetManager, EntityManager, Serializer, Deserializer
from shard.rendering import RenderEngine, Viewport
from shard.audio import AudioEngine
from shard.core.logger import Logger
from shard.core.systems import TransformSystem, MeshRendererSystem, CollisionSystem, PhysicsSystem, CameraSystem, FlyControllerSystem, ScriptSystem

from shard.core.engine import Engine, ENGINE_VERSION

def bootstrap():
    try:
        # Setup Console
        console = Console()
        logger = Logger(console)

        logger.log_info(f"SHARD ENGINE v{ENGINE_VERSION}")

        user32 = ctypes.windll.user32

        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # Setup Shard Renderer
        render_engine = RenderEngine()
        render_engine.initialize(screen_width, screen_height, "Shard Engine")
        render_engine.hide_mouse()
        console.set_render_engine(render_engine)

        viewport = Viewport()
        viewport.create(1280, 720)

        # Setup Shard Audio Engine
        audio_engine = AudioEngine()

        # Setup systems
        entity_manager = EntityManager()
        asset_manager = AssetManager(render_engine, logger)
        asset_manager.load_assets("assets/textures", "assets/models")

        transform_system = TransformSystem(entity_manager, logger)
        mesh_renderer_system = MeshRendererSystem(entity_manager, asset_manager, logger)
        collision_system = CollisionSystem(entity_manager, asset_manager)
        physics_system = PhysicsSystem(entity_manager)
        camera_system = CameraSystem(entity_manager)
        fly_controller_system = FlyControllerSystem(entity_manager, render_engine)

        # Serialization
        serializer = Serializer()
        deserializer = Deserializer()

        # Setup UI
        viewport_ui = ViewportUI(render_engine)
        hierarchy = Hierarchy(render_engine, entity_manager, transform_system)
        inspector = Inspector(render_engine, entity_manager, hierarchy, asset_manager)
        profiler = Profiler(render_engine)
        main_menu = MainMenu(render_engine, entity_manager)

        return Engine(console, logger, screen_width, screen_height, render_engine, audio_engine, viewport, entity_manager, asset_manager, transform_system, mesh_renderer_system, collision_system, physics_system, camera_system, fly_controller_system, serializer, deserializer, viewport_ui, hierarchy, inspector, profiler, main_menu)

    except Exception as e:
        logger.log_fatal(f"Core engine initialization failed:\n{traceback.format_exc()}")
