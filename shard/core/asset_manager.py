import os
import time
from pathlib import Path
import json
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
                self.logger.log_warning(f"Texture at {path} has been modified since last cook. Recooking.")
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

    def load_textures(self, path, assets, database):
        start = time.perf_counter()

        existing = database["resources"]

        # Discover any new textures
        for texture in Path(path).rglob("*"):
            if texture.suffix.lower() not in [".png", ".jpg"]:
                continue

            texture = str(self._normalize_path(texture))

            if texture not in existing:
                self.logger.log_info(f"Discovered new texture: {texture}")

                existing[texture] = {
                    "type": "texture"
                }

        count = 0
        for texture, data in existing.items():
            if data["type"] != "texture":
                continue

            handle, tex_path = self.get_texture(texture, "assets/textures/Empty.png", self.logger)

            data["handle"] = handle

            assets[texture] = data
            count += 1

        self.logger.log_info(f"Loaded {count} textures in {time.perf_counter()-start:.1f}s")

            

    def load_env_maps(self, path, assets, database):
        start = time.perf_counter()

        resources = database["resources"]

        for env in Path(path).rglob("*.exr"):
            env = str(self._normalize_path(env))

            if env not in resources:
                self.logger.log_info(f"Discovered new environment map: {env}")

                resources[env] = {
                    "type": "env"
                }

        count = 0
        for env, data in resources.items():
            if data["type"] != "env":
                continue

            handle, env_path = self.get_env_map(env)

            data["handle"] = handle["environment"]

            assets[env] = data
            count += 1

        self.logger.log_info(f"Loaded {count} environment maps in {time.perf_counter() - start:.1f}s.")

    def load_meshes(self, path, assets, database):
        start = time.perf_counter()

        meshes = database["meshes"]

        for mesh in Path(path).rglob("*.obj"):
            mesh = str(self._normalize_path(mesh))

            if mesh not in meshes:
                self.logger.log_info(f"Discovered new mesh: {mesh}")

                meshes[mesh] = {
                    "type": "mesh"
                }

        count = 0
        for mesh, data in meshes.items():
            handle, _ = self.get_mesh(mesh)
            data["handle"] = handle

            assets[mesh] = data
            count += 1

        self.logger.log_info(f"Loaded {count} meshes in {time.perf_counter() - start:.1f}s.")

    def load_assets(self, texture_path, mesh_path):
        database = self.load_database()

        resources = {}
        meshes = {}

        self.load_textures(texture_path, resources, database)
        self.load_env_maps(texture_path, resources, database)
        self.load_meshes(mesh_path, meshes, database)

        self.save_database(database)

        return {
            "resources": resources,
            "meshes": meshes
        }

    def load_database(self, path="assets/asset_database.json"):
        if not os.path.exists(path):
            return {
                "resources": {},
                "meshes": {}
            }

        with open(path, "r") as f:
            return json.load(f)

    def save_database(self, database, path="assets/asset_database.json"):
        with open(path, "w") as f:
            json.dump(database, f, indent=4)
        
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
                self.logger.log_warning(f"Env map at {path} has been modified since last cook. Recooking.")
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