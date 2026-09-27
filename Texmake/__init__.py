bl_info = {
    "name": "Texmake",
    "author": "ID Software, serecky",
    "version": (0, 0, 1),
    "blender": (2, 83, 0),
    "location": "Edit Mode -> N-Panel -> Texmake",
    "description": "ID Software's Quake 1/2 UV Mapper for Blender",
    "category": "UV"
}

if "bpy" in locals():
    import imp
    if "texmake" in locals():
        imp.reload(texmake)

import bpy
import time

from bpy.props import (
    BoolProperty, 
    IntVectorProperty, 
    FloatVectorProperty,
    EnumProperty,
    PointerProperty
)

from bpy.types import (
    PropertyGroup,
    Operator,
    Panel,
    WindowManager
)

from bmesh import (
    from_edit_mesh, 
    update_edit_mesh
)

from . texmake import (
    axis_info,
    TexmakeMain
)
from mathutils import Vector

class TexmakeProperties(PropertyGroup):
    fixed_size = BoolProperty(
        name = "Fixed Size Skins",
        description = "Generate skins at a fixed width and height",
        default = False
    )

    skin_dimensions = IntVectorProperty(
        name = "Skin Size",
        description = "Fixed Size Skin width and height.",
        default = (256, 128),
        size = 2
    )

    line_style = EnumProperty(
        name = "Line Style",
        description = "How UV lines should be drawn on the texture.\nWarning: Lines make skin generation a lot slower",
        items = (
            ('NO_LINE', "No Lines", "Draw no lines. Best performance."),
            ('THIN_LINES', "Thin Lines", "Draw thin lines. Takes a while to draw onto the skin."),
            ('FAT_LINES', "Fat Lines", "Draw fat lines. Takes very long time to draw onto the skin.")
        ),
        default = 'FAT_LINES'
    )

    line_color = FloatVectorProperty(
        name = "Line Color",
        subtype = "COLOR",
        description = "What color lines will be drawn as",
        default = (159.0 / 255.0, 91.0 / 255.0, 83.0 / 255.0),
        size = 3
    )
    
    fat_lines = BoolProperty(
        name = "Fat Lines",
        description = "Draw really fat lines.\nWarning: Makes skin generation slower",
        default = True
    )

    generate_skin = BoolProperty(
        name = "Generate Skin",
        description = "Create a wireframed skin",
        default = True
    )
    
    projection_axis = EnumProperty(
        name = "Forward/Side Axis",
        description = "Which forward/side axis the projection\nshould start at",
        items = tuple(
            (k, axis_info[k]["Name"], "") for k in axis_info.keys()
        ),
        default = 'YX_AXIS'
    )

class TexmakeOperator(Operator):
    bl_idname = "texmake.operator"
    bl_label = "Generate UV Maps"
    bl_description = (
        "Click this to generate a UV map"
    )

    def execute(self, context):
        main = TexmakeMain()
        start_time = time.time()
        
        edit_mesh = bpy.context.active_object.data
        temp_mesh = from_edit_mesh(edit_mesh)
        
        main.bound_faces(temp_mesh.verts)
        main.write_uv(temp_mesh)

        update_edit_mesh(edit_mesh)
        
        self.report({'INFO'}, "Finished in {:.4f}".format(time.time() - start_time))
        
        return {'FINISHED'}

class VIEW3D_PT_TexmakePanel(Panel):
    bl_label = "Texmake Control Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "mesh_edit"
    bl_category = "Texmake"

    def draw(self, context):
        properties = bpy.context.window_manager.texmake_properties
        
        layout = self.layout

        row = layout.row()
        row.prop(properties, "generate_skin")

        if properties.generate_skin is True:
            box = layout.box()

            row = box.row()
            row.prop(properties, "line_style")

            if properties.line_style != "NO_LINE":
                row = box.row()
                row.prop(properties, "line_color")

            row = box.row()
            row.prop(properties, "fixed_size")

            if properties.fixed_size is True:
                row = box.row()
                row.prop(properties, "skin_dimensions")
        
        row = layout.row()
        row.prop(properties, "projection_axis")
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("texmake.operator")

class_list = (
        TexmakeOperator,
        VIEW3D_PT_TexmakePanel
    )

def register():
    bpy.utils.register_class(TexmakeProperties)
    
    WindowManager.texmake_properties = PointerProperty(type = TexmakeProperties)
    
    for x in class_list: bpy.utils.register_class(x)

def unregister():
    bpy.utils.unregister_class(TexmakeProperties)
    
    for x in class_list: bpy.utils.unregister_class(x)

    del WindowManager.texmake_properties

if __name__ == "__main__":
    register()
    
