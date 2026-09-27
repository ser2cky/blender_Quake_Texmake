#
#   This is a direct translation of Quake's
#   uv-map generator code, into something that
#   can be used as a Blender plugin.
#
#   I have added a few comments to the code, to
#   hopefully better explain how the UV Mapper
#   works. (serecky)
#
#   Files referenced:
#       * MODELGEN.C
#       * TEXMAKE.C
#   These files can be found at:
#   https://github.com/id-Software/Quake-Tools/
#

import bpy
import bmesh

from mathutils import Vector
from math import floor, ceil

axis_info = {
    'XY_AXIS' : {"Name": "X/Y Axis", "Axis": (0, 1)},
    'YX_AXIS' : {"Name": "Y/X Axis", "Axis": (1, 0)},
}

def q_round(num): return int(floor(num+0.5))

def rangefl(start, stop, step):
    while start <= stop:
        yield start
        start += step

class TexmakeMain:
    def __init__(self):
        self.maxs = Vector((0.0, 0.0, 0.0))
        self.mins = Vector((0.0, 0.0, 0.0))

        self.pad_model_size = (0, 0)
        self.skin_size = (0, 0)
        self.scale = (0.0, 0.0)

        self.image = None
        self.properties = bpy.context.window_manager.texmake_properties
        
        self.forward_axis = axis_info[self.properties.projection_axis]["Axis"][0]
        self.side_axis = axis_info[self.properties.projection_axis]["Axis"][1]

    #
    #   bound_faces
    #   gets model dimensions (self.pad_model_size, self.mins, self.maxs)
    #   and calculates skin size.
    #
    def bound_faces(self, vert_list):
        for vert in vert_list:
            for x in range(0, 3):
                if vert.co[x] < self.mins[x]: self.mins[x] = vert.co[x]
                if vert.co[x] > self.maxs[x]: self.maxs[x] = vert.co[x]

        for x in range(0, 3):
            self.mins[x] = floor(self.mins[x])
            self.maxs[x] = ceil(self.maxs[x])

        model_size = (int(self.maxs[self.forward_axis] - self.mins[self.forward_axis]), int(self.maxs.z - self.mins.z))
        scale = 8.0

        if self.properties.fixed_size is False:
            if (model_size[0] * scale) >= 150:
                scale = 150.0 / model_size[0]
                
            if (model_size[1] * scale) >= 190:
                scale = 190.0 / model_size[1]
                
            self.pad_model_size = (
                ceil(model_size[0] * scale) + 4,
                ceil(model_size[1] * scale) + 4
            )
            
            self.scale = (scale, scale)
        else:
            self.pad_model_size = (
                self.properties.skin_dimensions[0] // 2,
                self.properties.skin_dimensions[1]
            )
            
            self.scale = (
                (self.pad_model_size[0] - 4.0) / model_size[0],
                (self.pad_model_size[1] - 4.0) / model_size[1]
            )

        # make the width a multiple of 4; some hardware requires this, and it ensures
        # dword alignment for each scan
        width = self.pad_model_size[0] * 2
        self.skin_size = (width + (4 - (width % 4)), self.pad_model_size[1])
        
        print(
            f"width: {model_size[0]} height: {model_size[1]}\n"
            f"scale: {self.scale[0]} {self.scale[1]}\n"
            f"iwidth: {self.pad_model_size[0]} iheight: {self.pad_model_size[1]}\n"
            f"skin width: {self.skin_size[0]} (unpadded width: {width}) skin height: {self.skin_size[1]}"
            )

        # create new image for drawing
        if self.properties.generate_skin is True:
            image = bpy.data.images.get('_texmake_skin_')
            if image is not None: bpy.data.images.remove(image)
            self.image = bpy.data.images.new(name='_texmake_skin_', width=self.skin_size[0], height=self.skin_size[1])
            
    #
    #   plot_pixel_safe
    #
    def plot_pixel_safe(self, xy, color):
        if self.image is None: return
        pixel = (int(xy[0]) + self.skin_size[0] * int(xy[1])) * 4
        
        if pixel < len(self.image.pixels):
            self.image.pixels[pixel] = color[0]
            self.image.pixels[pixel + 1] = color[1]
            self.image.pixels[pixel + 2] = color[2]
            self.image.pixels[pixel + 3] = 1.0
            
    #
    #   plot_pixel
    #   wrapper for plot_pixel_safe
    #  
    def plot_pixel(self, xy, color):
        if self.image is None: return

        if self.properties.line_style == 'FAT_LINES':
            # tried speeding this up with a lookup table, but on average a lookup table for
            # this runs about 2x slower...
            for u in rangefl(-0.1, 0.9, 0.999):
                for v in rangefl(-0.1, 0.9, 0.999):
                    self.plot_pixel_safe((xy[0] + u, xy[1] + v), color)
        else:
            self.plot_pixel_safe(xy, color)

    #
    #   draw_line
    #   draw uv lines.
    #
    def draw_line(self, xy1, xy2):
        delta = (xy2[0] - xy1[0], xy2[1] - xy1[1])
        count = max((abs(delta[0]), abs(delta[1])))
        
        if count <= 0: return
        
        start = [float(xy1[0]), float(xy1[1])]
        step = (float(delta[0]) / count, float(delta[1]) / count)

        for x in range(0, count):
            self.plot_pixel(start, self.properties.line_color) 
            start[0] += step[0]
            start[1] += step[1]

    #
    #   write_uv
    #   write uv map and generate texture (if so desired by the user) for
    #   their mesh.
    #
    def write_uv(self, mesh):
        for face in mesh.faces:
            uv_coords = [ (0, 0) ] * len(face.verts)
            base_ofs = [2, 2]

            # determine which side to map the teture to
            v1 = face.verts[0].co - face.verts[1].co
            v2 = face.verts[2].co - face.verts[1].co
            normal = Vector.cross(v1, v2)

            if normal[self.side_axis] > 0.0: base_ofs[0] = self.pad_model_size[0] + 2
            uv_layer = mesh.loops.layers.uv.verify()

            # write uv
            for x, loop in enumerate(face.loops):
                uv = loop[uv_layer].uv
                
                uv.x = q_round((loop.vert.co[self.forward_axis] - self.maxs[self.forward_axis]) * self.scale[0] + base_ofs[0]) + self.pad_model_size[0]
                uv.y = (q_round((self.maxs.z - loop.vert.co.z) * self.scale[0] + base_ofs[1]) * -1) + self.pad_model_size[1]

                # copy uv stuff to another list for drawing lines
                uv_coords[x] = (int(uv.x), int(uv.y))

                # scale down UV coords for Blender
                uv.x /= float(self.skin_size[0])
                uv.y /= float(self.skin_size[1])
            
            # draw lines
            if self.properties.generate_skin is True and self.properties.line_style != 'NO_LINE':
                for x in range(0, len(face.verts)): self.draw_line(uv_coords[x], uv_coords[(x + 1) % len(face.verts)])
                
        # show image when done.
        if self.image is not None:
            self.image.update()
            for area in bpy.context.screen.areas:
                if area.type == "IMAGE_EDITOR":
                    for space in area.spaces:
                        if space.type == "IMAGE_EDITOR":
                            space.image = self.image
            
