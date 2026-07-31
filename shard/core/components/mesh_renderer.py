from ..component import component
from shard.rendering import PBRMaterial, SkyboxMaterial


@component
class MeshRenderer:
    __inspect__ = {
        "mesh_handle": "mesh",
        "material": "material"
    }

    def __init__(self, mesh_handle=1, material=None):
        self.entity = None

        self.mesh_handle = mesh_handle
        self.material = material

    def serialize(self):
        return {
            "mesh_handle": self.mesh_handle,
            "material": self.material.serialize()
        }

    @classmethod
    def deserialize(cls, data, engine):
        # Header has material type (PBR/Skybox)
        mat_type = data["material"].split("#")[0]

        render_engine = engine.render_engine
        asset_manager = engine.managers.asset
        logger = engine.logger

        if mat_type == "PBR":
            material = PBRMaterial.deserialize(render_engine, asset_manager, logger, data)
        elif mat_type == "Skybox":
            material = SkyboxMaterial.deserialize(render_engine, asset_manager, logger, data)
        else:
            logger.log_warning(f"Unsupported material of type {mat_type} found in scene. Scene may be corrupt.")

        return cls(data["mesh_handle"], material)