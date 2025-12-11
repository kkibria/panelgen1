bl_info = {
    "name": "My Panel Add-on",
    "author": "You",
    "version": (0, 0, 1),
    "blender": (5, 0, 0),
    "location": "VSE > Sidebar > My Panels",
    "category": "Sequencer",
}

import bpy

from bpy.props import BoolProperty, StringProperty


# ─────────────────────────────────────────
# PROPERTIES REGISTER / UNREGISTER
# ─────────────────────────────────────────

def register_properties():
    bpy.types.Scene.my_main_label = StringProperty(
        name="Main Label",
        description="Main label text for overlays",
        default='Hello from TOML'
    )
    bpy.types.Scene.my_show_debug = BoolProperty(
        name="Show Debug",
        description="Toggle debug mode",
        default=True
    )


def unregister_properties():
    if hasattr(bpy.types.Scene, "my_main_label"):
        del bpy.types.Scene.my_main_label
    if hasattr(bpy.types.Scene, "my_show_debug"):
        del bpy.types.Scene.my_show_debug


# ─────────────────────────────────────────
# OPERATORS
# ─────────────────────────────────────────

class MYADDON_OT_dummy_operator(bpy.types.Operator):
    """Dummy operator generated from TOML"""
    bl_idname = "myaddon.dummy_operator"
    bl_label = "Dummy Operator"
    bl_options = {"REGISTER"}

    def execute(self, context):
        # You can customize operator logic later
        self.report({'INFO'}, "Operator myaddon.dummy_operator executed.")
        return {'FINISHED'}


# ─────────────────────────────────────────
# PANELS
# ─────────────────────────────────────────

class MYADDON_PT_main(bpy.types.Panel):
    """Auto-generated panel"""
    bl_label = "Main Panel"
    bl_idname = "MYADDON_PT_main"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "MyPanel"

    def draw(self, context):
        layout = self.layout
        scene = getattr(context, "scene", None)
        if scene is None:
            layout.label(text="No scene context.")
            return

        layout.label(text="Main Panel")

        # Properties
        layout.prop(context.scene, "my_main_label")
        layout.prop(context.scene, "my_show_debug")

        # Operators
        layout.operator("myaddon.dummy_operator", text="Run Dummy")

class MYADDON_PT_secondary(bpy.types.Panel):
    """Auto-generated panel"""
    bl_label = "Secondary Panel"
    bl_idname = "MYADDON_PT_secondary"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "MyPanel"

    def draw(self, context):
        layout = self.layout
        scene = getattr(context, "scene", None)
        if scene is None:
            layout.label(text="No scene context.")
            return

        layout.label(text="Secondary Panel")

        # Properties
        layout.prop(context.scene, "my_main_label")

        # Operators
        layout.operator("myaddon.dummy_operator", text="Run Dummy (Secondary)")


classes = [
    MYADDON_OT_dummy_operator,
    MYADDON_PT_main,
    MYADDON_PT_secondary,
]


def register():
    register_properties()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()


if __name__ == "__main__":
    register()