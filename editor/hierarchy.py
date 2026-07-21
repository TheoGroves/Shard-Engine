from rendering import RenderEngine
from core import EntityManager
from core.logger import *

class Hierarchy:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager):
        self.render_engine = render_engine
        self.entity_manager = entity_manager
        self.selected = None

    def update(self):
        self.render_engine.begin_window("Hierarchy")
        
        for eid in self.entity_manager.query("Name", "Transform"):
            transform = self.entity_manager.entities[eid].components["Transform"]

            if transform.parent is None:
                self.draw_entity(eid)

        self.render_engine.end_window()

    def draw_entity(self, eid):
        entity = self.entity_manager.entities[eid]
        name = entity.components["Name"].name
        transform = entity.components["Transform"]

        has_children = len(transform.children) > 0

        if has_children:
            opened = self.render_engine.tree_node(name)

            if self.render_engine.is_item_clicked():
                self.selected = eid

            if opened:
                for t in transform.children:
                    self.draw_entity(t.entity)

                self.render_engine.tree_pop()
        else:
            if self.render_engine.selectable(name, self.selected == eid):
                self.selected = eid