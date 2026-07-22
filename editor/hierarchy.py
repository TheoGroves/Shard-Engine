from rendering import RenderEngine, TreeNodeFlags
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

        flags = TreeNodeFlags.OpenOnArrow | TreeNodeFlags.SpanAvailWidth

        if self.selected == eid:
            flags |= TreeNodeFlags.Selected

        if not has_children:
            flags |= TreeNodeFlags.Leaf
            flags |= TreeNodeFlags.NoTreePushOnOpen

        opened = self.render_engine.tree_node_ex(str(eid), name, flags)

        if self.render_engine.is_item_clicked():
            self.selected = eid

        if self.render_engine.is_window_clicked() and not self.render_engine.is_item_clicked():
            self.selected = None

        if opened and has_children:
            for t in transform.children:
                self.draw_entity(t.entity)

            self.render_engine.tree_pop()