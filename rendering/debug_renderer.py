from core.systems import MeshColliderSystem
from ecs import EntityManager

class ColliderDebugger:
    def __init__(self, ctx, em: EntityManager, mcs: MeshColliderSystem):
        self.ctx = ctx

        with open("assets/shaders/debug.vert") as f:
            debug_vert = f.read()

        with open("assets/shaders/debug.frag") as f:
            debug_frag = f.read()

        self.program = self.ctx.program(
            vertex_shader=debug_vert,
            fragment_shader=debug_frag
        )

        self.em = em
        self.mcs = mcs

    def draw(self, renderer):
        if not self.program:
            return

        self.program["view"].write(renderer.view.astype("f4").T.tobytes())
        self.program["proj"].write(renderer.proj.astype("f4").T.tobytes())

        self.ctx.wireframe = True

        for eid in self.em.query("MeshCollider", "Transform"):
            entity = self.em.entities[eid]
            c = entity.components["MeshCollider"]
            t = entity.components["Transform"]

            if not c.debug:
                continue

            self.mcs.build_debug_vao(eid, self.program)    
            
            self.program["model"].write(
                t.model.astype("f4").T.tobytes()
            )

            c.mesh.vao.render()

        self.ctx.wireframe = False