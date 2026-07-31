import os
import time
from pathlib import Path
from .logger import *
from shard.loaders.texture_loader import load_texture, load_cooked_tex, save_cooked_tex, load_env_map, load_cooked_env_map, save_cooked_env_map, generate_irradiance
from .mesh import Mesh

class AssetManager:
    def __init__(self, engine, logger):
        self.render_engine = engine
        self.logger = logger

        self.mesh_handles = {}
        self.mesh_paths = {}
        self.meshes = {}
        self.textures = {}
        self.texture_paths = {}
        self.env_maps = {}
        self.env_paths = {}

        self.env_irr_map = {}

    @staticmethod
    def _normalize_path(path):
        return os.path.realpath(path)

    def get_mesh(self, path):
        start = time.perf_counter()
        path = self._normalize_path(path)

        if path in self.mesh_handles and path in self.meshes:
            return self.mesh_handles[path], self.meshes[path]
        
        cooked_path = path + ".mesh"
        
        mesh = Mesh()
        if os.path.exists(cooked_path):
            last_exported = os.path.getmtime(path)
            last_cooked   = os.path.getmtime(cooked_path)

            if last_exported >= last_cooked:
                self.logger.log_warning(f"Mesh at {path} has been modified since last cook. Recooking.")
                mesh.load_model(path, self.logger)
                mesh.save_cooked(cooked_path)
            else:
                try:
                    mesh.load_cooked(cooked_path)
                except Exception as _:
                    self.logger.log_warning("Outdated/corrupted cooked mesh. Recooking mesh.")
                    mesh.load_model(path, self.logger)
                    mesh.save_cooked(cooked_path)
        else:
            mesh.load_model(path, self.logger)
            mesh.save_cooked(cooked_path)

        mesh_id = self.render_engine.create_mesh(mesh.vertices, mesh.indices)

        self.mesh_handles[path] = mesh_id
        self.mesh_paths[mesh_id] = path
        self.meshes[path] = mesh
        #self.logger.log_info(f"Loaded mesh {os.path.split(path)[-1]} in {(time.perf_counter()-start)*1000:.1f}ms")
        return mesh_id, mesh
    
    @staticmethod
    def _recook_tex(ctx, path, cooked_path, fallback, logger):
        tex, tex_path = load_texture(ctx, path, fallback, logger)
        save_cooked_tex(tex_path, cooked_path)

        return tex, tex_path
    
    def get_texture(self, path, fallback, logger):
        path = self._normalize_path(path)

        if path in self.textures:
            return self.textures[path], path
        
        cooked_path = path + ".texture"

        if os.path.exists(cooked_path):
            last_exported = os.path.getmtime(path)
            last_cooked   = os.path.getmtime(cooked_path)

            if last_exported >= last_cooked:
                self.logger.log_error(f"Texture at {path} has been modified since last cook. Recooking.")
                texture_handle, tex_path = AssetManager._recook_tex(self.render_engine, path, cooked_path, fallback, logger)
            else:
                try:
                    texture_handle, _ = load_cooked_tex(self.render_engine, cooked_path)
                    tex_path = path
                except Exception as _:
                    texture_handle, tex_path = AssetManager._recook_tex(self.render_engine, path, cooked_path, fallback, logger)
        else:
            texture_handle, tex_path = AssetManager._recook_tex(self.render_engine, path, cooked_path, fallback, logger)

        self.textures[path] = texture_handle
        self.texture_paths[texture_handle] = path
        return texture_handle, tex_path

    def load_textures(self, path, logger):
        start = time.perf_counter()
        patterns = [
            "*.png",
            "*.jpg"
        ]

        count = 0
        for pattern in patterns:
            for texture in Path(path).rglob(pattern):
                self.get_texture(texture, "assets/textures/Empty.png", logger)
                count += 1

        logger.log_info(f"Loaded {count} textures in {time.perf_counter() - start:.1f}s.")

    def load_env_maps(self, path, logger):
        start = time.perf_counter()
        patterns = [
            "*.exr"
        ]

        count = 0
        for pattern in patterns:
            for texture in Path(path).rglob(pattern):
                self.get_env_map(texture)
                count += 1

        logger.log_info(f"Loaded {count} environment maps in {time.perf_counter() - start:.1f}s.")

    def load_meshes(self, path, logger):
        start = time.perf_counter()
        patterns = [
            "*.obj"
        ]

        count = 0
        for pattern in patterns:
            for path in Path(path).rglob(pattern):
                self.get_mesh(path)
                count += 1

        logger.log_info(f"Loaded {count} meshes in {time.perf_counter() - start:.1f}s.")
    
    @staticmethod
    def _recook_env_map(render_engine, path, cooked_path):
        env_map, img, width, height, env_map_path = load_env_map(render_engine, path)

        irr = generate_irradiance(img, 64, 32, samples=256)
        save_cooked_env_map(img, width, height, 64, 32, irr, cooked_path)

        irr_tex = render_engine.create_texture_rgb32f(irr)

        return env_map, irr_tex, env_map_path
    
    def get_env_map(self, path):
        path = self._normalize_path(path)

        if path in self.env_maps:
            return self.env_maps[path], path
        
        cooked_path = path + ".envmap"

        if os.path.exists(cooked_path):
            last_exported = os.path.getmtime(path)
            last_cooked   = os.path.getmtime(cooked_path)

            if last_exported >= last_cooked:
                self.logger.log_error(f"Env map at {path} has been modified since last cook. Recooking.")
                env_map, irr_map, env_map_path = AssetManager._recook_env_map(self.render_engine, path, cooked_path)
            else:
                try:
                    env_map, irr_map, _ = load_cooked_env_map(self.render_engine, cooked_path)
                    env_map_path = path
                except Exception as _:
                    env_map, irr_map, env_map_path = AssetManager._recook_env_map(self.render_engine, path, cooked_path)
        else:
            env_map, irr_map, env_map_path = AssetManager._recook_env_map(self.render_engine, path, cooked_path)

        self.env_maps[path] = {"environment": env_map, "irradiance": irr_map}
        self.env_paths[env_map] = path
        self.env_irr_map[env_map] = irr_map
        return self.env_maps[path], env_map_path