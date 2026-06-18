import os
from core.mesh import Mesh
from loaders.texture_loader import load_texture, load_cooked_tex, save_cooked_tex, load_env_map, load_cooked_env_map, save_cooked_env_map

class AssetManager:
    def __init__(self, ctx):
        self.ctx = ctx

        self.meshes = {}
        self.textures = {}
        self.env_maps = {}

    @staticmethod
    def _normalize_path(path):
        return os.path.realpath(path)

    def get_mesh(self, path):
        path = self._normalize_path(path)

        if path in self.meshes:
            return self.meshes[path]
        
        cooked_path = path + ".mesh"
        
        mesh = Mesh()
        if os.path.exists(cooked_path):
            last_exported = os.path.getmtime(path)
            last_cooked   = os.path.getmtime(cooked_path)

            if last_exported >= last_cooked:
                print(f"WARNING: Mesh at {path} has been modified since last cook. Recooking.")
                mesh.load_model(path)
                mesh.save_cooked(cooked_path)
            else:
                try:
                    mesh.load_cooked(cooked_path)
                except Exception as _:
                    print("WARNING: Outdated/corrupted cooked mesh. Recooking mesh.")
                    mesh.load_model(path)
                    mesh.save_cooked(cooked_path)
        else:
            mesh.load_model(path)
            mesh.save_cooked(cooked_path)

        self.meshes[path] = mesh
        return mesh
    
    @staticmethod
    def _recook_tex(ctx, path, cooked_path, fallback):
        tex, tex_path = load_texture(ctx, path, fallback)
        save_cooked_tex(tex_path, cooked_path)

        return tex, tex_path
    
    def get_texture(self, path, fallback):
        path = self._normalize_path(path)

        if path in self.textures:
            return self.textures[path], path
        
        cooked_path = path + ".texture"

        if os.path.exists(cooked_path):
            last_exported = os.path.getmtime(path)
            last_cooked   = os.path.getmtime(cooked_path)

            if last_exported >= last_cooked:
                print(f"WARNING: Texture at {path} has been modified since last cook. Recooking.")
                texture, tex_path = AssetManager._recook_tex(self.ctx, path, cooked_path, fallback)
            else:
                try:
                    texture, _ = load_cooked_tex(self.ctx, cooked_path)
                    tex_path = path
                except Exception as _:
                    texture, tex_path = AssetManager._recook_tex(self.ctx, path, cooked_path, fallback)
        else:
            texture, tex_path = AssetManager._recook_tex(self.ctx, path, cooked_path, fallback)

        self.textures[path] = texture
        return texture, tex_path
    
    @staticmethod
    def _recook_env_map(ctx, path, cooked_path):
        env_map, img, width, height, env_map_path = load_env_map(ctx, path)
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
                print(f"WARNING: Env map at {path} has been modified since last cook. Recooking.")
                env_map, env_map_path = AssetManager._recook_env_map(self.ctx, path, cooked_path)
            else:
                try:
                    env_map, _ = load_cooked_env_map(self.ctx, cooked_path)
                    env_map_path = path
                except Exception as _:
                    env_map, env_map_path = AssetManager._recook_env_map(self.ctx, path, cooked_path)
        else:
            env_map, env_map_path = AssetManager._recook_env_map(self.ctx, path, cooked_path)

        self.env_maps[path] = env_map
        return env_map, env_map_path