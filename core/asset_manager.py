import os
import time
from .logger import *
from loaders.texture_loader import load_texture, load_cooked_tex, save_cooked_tex, load_env_map, load_cooked_env_map, save_cooked_env_map
from .mesh import Mesh

class AssetManager:
    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

        self.mesh_handles = {}
        self.meshes = {}
        self.textures = {}
        self.env_maps = {}

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

        mesh_id = self.engine.create_mesh(mesh.vertices, mesh.indices)

        self.mesh_handles[path] = mesh_id
        self.meshes[path] = mesh
        self.logger.log_info(f"Loaded mesh {os.path.split(path)[-1]} in {(time.perf_counter()-start)*1000:.1f}ms")
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
                texture_handle, tex_path = AssetManager._recook_tex(self.engine, path, cooked_path, fallback, logger)
            else:
                try:
                    texture_handle, _ = load_cooked_tex(self.engine, cooked_path)
                    tex_path = path
                except Exception as _:
                    texture_handle, tex_path = AssetManager._recook_tex(self.engine, path, cooked_path, fallback, logger)
        else:
            texture_handle, tex_path = AssetManager._recook_tex(self.engine, path, cooked_path, fallback, logger)

        self.textures[path] = texture_handle
        return texture_handle, tex_path
    
    @staticmethod
    def _recook_env_map(engine, path, cooked_path):
        env_map, img, width, height, env_map_path = load_env_map(engine, path)
        save_cooked_env_map(img, width, height, cooked_path)

        return env_map, env_map_path
    
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
                env_map, env_map_path = AssetManager._recook_env_map(self.engine, path, cooked_path)
            else:
                try:
                    env_map, _ = load_cooked_env_map(self.engine, cooked_path)
                    env_map_path = path
                except Exception as _:
                    env_map, env_map_path = AssetManager._recook_env_map(self.engine, path, cooked_path)
        else:
            env_map, env_map_path = AssetManager._recook_env_map(self.engine, path, cooked_path)

        self.env_maps[path] = env_map
        return env_map, env_map_path