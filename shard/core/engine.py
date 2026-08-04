
import ctypes

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
from shard.core.logger import Logger
from shard.core.systems import TransformSystem, MeshRendererSystem, CollisionSystem, PhysicsSystem, CameraSystem, FlyControllerSystem, ScriptSystem

ENGINE_VERSION = "0.5.0"

class UI:
    def __init__(self, console: Console, viewport: ViewportUI, hierarchy: Hierarchy, inspector: Inspector, profiler: Profiler, main_menu: MainMenu):
        self.console = console
        self.viewport = viewport
        self.hierarchy = hierarchy
        self.inspector = inspector
        self.profiler = profiler
        self.main_menu = main_menu

class Systems:
    def __init__(self, transform: TransformSystem, mesh_renderer: MeshRendererSystem, collision: CollisionSystem, physics: PhysicsSystem, camera: CameraSystem, fly_controller: FlyControllerSystem, scripting_system: ScriptSystem):
        self.transform = transform
        self.mesh_renderer = mesh_renderer
        self.collision = collision
        self.physics = physics
        self.camera = camera
        self.fly_controller = fly_controller
        self.scripting = scripting_system

class Managers:
    def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager):
        self.entity = entity_manager
        self.asset = asset_manager
        

class Engine:
    def __init__(self, console: Console, logger: Logger, screen_width: int, screen_height: int, render_engine: RenderEngine, viewport: Viewport, entity_manager: EntityManager, asset_manager: AssetManager, transform_system: TransformSystem, mesh_renderer_system: MeshRendererSystem, collision_system: CollisionSystem, physics_system: PhysicsSystem, camera_system: CameraSystem, fly_controller_system: FlyControllerSystem, serializer: Serializer, deserializer: Deserializer, viewport_ui: ViewportUI, hierarchy: Hierarchy, inspector: Inspector, profiler: Profiler, main_menu: MainMenu):
        # Constants
        self.USER_32 = ctypes.windll.user32
        self.PLAY_MODE = True

        # Variables
        self.logger = logger
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_engine = render_engine
        self.viewport = viewport

        self.managers = Managers(entity_manager, asset_manager)

        scripting_system = ScriptSystem(entity_manager, self)

        self.systems = Systems(transform_system, mesh_renderer_system, collision_system, physics_system, camera_system, fly_controller_system, scripting_system)
        self.ui = UI(console, viewport_ui, hierarchy, inspector, profiler, main_menu)

        self.serializer = serializer
        self.deserializer = deserializer
        self.bvh = None
        self.triangles = []

        self.dt = 0.0

    def rebuild_bvh(self):
        self.triangles = self.systems.collision.get_collision_triangles(self.bvh)