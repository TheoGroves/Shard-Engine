from shard.rendering import RenderEngine, TreeNodeFlags
from shard.core import EntityManager
from shard.core.logger import *
from shard.core.systems import TransformSystem
from shard.core.components import Name, Transform
from shard.maths.python import Vec3

class Hierarchy:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager, transform_system: TransformSystem):
        self.render_engine = render_engine
        self.entity_manager = entity_manager
        self.transform_system = transform_system
        self.selected = None
        self.to_delete = None

    def is_descendant(self, eid, possible_parent):
        t = self.entity_manager.entities[eid].components["Transform"]

        for child in t.children:
            if child.entity == possible_parent:
                return True
            
            if self.is_descendant(child.entity, possible_parent):
                return True
            
        return False

    def reparent(self, child, parent):
        parent_transform = self.entity_manager.entities[parent].components["Transform"]

        if self.is_descendant(parent, child):
            return

        self.transform_system.set_parent(child, parent_transform)

    def unparent(self, eid):
        transform = self.entity_manager.entities[eid].components["Transform"]

        if transform.parent is None:
            return

        if transform is not None:
            old_world_pos = transform.world_pos

            transform.parent.children.remove(transform)
            transform.parent = None

            transform.pos = old_world_pos

    def delete_entity(self, eid):
        transform = self.entity_manager.entities[eid].components["Transform"]

        if transform.parent is not None:
            transform.parent.children.remove(transform)
            transform.parent = None

        self.entity_manager.remove_entity(eid)

    def update(self):
        self.render_engine.begin_window("Hierarchy")
        
        for eid in self.entity_manager.query("Name", "Transform"):
            transform = self.entity_manager.entities[eid].components["Transform"]

            if transform.parent is None:
                self.draw_entity(eid)

        available = self.render_engine.get_available_region()
        self.render_engine.dummy(available.x, available.y)

        if self.render_engine.begin_drag_drop_target():
            dropped = self.render_engine.accept_drag_drop_payload("entity")

            if dropped != -1:
                self.unparent(dropped)

            self.render_engine.end_drag_drop_target()

        if self.render_engine.begin_popup_context_window():
            if self.render_engine.menu_item("Create Empty"):
                new_eid, _ = self.entity_manager.create_entity()
                self.entity_manager.add_component(new_eid, Name("Empty"))
                self.entity_manager.add_component(new_eid, Transform(Vec3(0,0,0),Vec3(0,0,0),Vec3(1,1,1)))


            self.render_engine.end_popup()

        self.render_engine.end_window()

        if self.to_delete is not None:
            self.delete_entity(self.to_delete)

            if self.selected == self.to_delete:
                self.selected = None

            self.to_delete = None

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

        # Selection
        if self.render_engine.is_item_clicked():
            self.selected = eid

        if self.render_engine.begin_popup_context_item():
            if self.render_engine.menu_item("Create Child"):
                child, _ = self.entity_manager.create_entity()
                self.entity_manager.add_component(child, Name("Empty"))
                self.entity_manager.add_component(child, Transform(Vec3(0,0,0),Vec3(0,0,0),Vec3(1,1,1)))
                self.reparent(child, eid)

            if self.render_engine.menu_item("Delete"):
                self.to_delete = self.selected

            self.render_engine.end_popup()

        # Drag source
        if self.render_engine.begin_drag_drop_source():
            self.render_engine.set_drag_drop_payload("entity", eid)

            self.render_engine.text(name)
            self.render_engine.end_drag_drop_source()

        # Drop target
        if self.render_engine.begin_drag_drop_target():
            dropped = self.render_engine.accept_drag_drop_payload("entity")

            if dropped != -1:
                self.reparent(dropped, eid)

            self.render_engine.end_drag_drop_target()

        if self.render_engine.is_window_clicked() and not self.render_engine.is_item_clicked():
            self.selected = None

        if opened and has_children:
            for t in transform.children:
                self.draw_entity(t.entity)

            self.render_engine.tree_pop()