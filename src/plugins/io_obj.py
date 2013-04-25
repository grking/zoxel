# io_obj.py
# Export mesh to OBJ format
# Copyright (c) 2013, Graham R King
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import os
from plugin_api import register_plugin

class ObjFile(object):
    
    # Description of file type
    description = "OBJ Files"
    
    # File type filter
    filetype = "*.obj"

    def __init__(self, api):
        self.api = api
        # Register our exporter
        self.api.register_file_handler(self)

    # Called when we need to save. Should raise an exception if there is a
    # problem saving.
    def save(self, filename):
        # grab the voxel data
        vertices, colours, normals = self.api.get_voxel_mesh()

        # Open our file
        f = open(filename,"wt")

        # Use materials
        name, _ = os.path.splitext(filename)
        mat_filename = os.path.basename(name)+".mtl"
        f.write("mtllib %s\r\n" % mat_filename)

        # Export vertices
        i = 0
        while i < len(vertices):
            f.write("v %f %f %f\r\n" % 
                (vertices[i], vertices[i+1], vertices[i+2]))
            i += 3
        
        # Build a list of unique colours we use so we can assign materials
        mats = {}
        i = 0
        while i < len(colours):
            r = colours[i]
            g = colours[i+1]
            b = colours[i+2]
            colour = r<<24 | g<<16 | b<<8
            if colour not in mats:
                mats[colour] = "material_%i" % len(mats)
            i += 3
            
        # Export faces
        faces = (len(vertices)//(3*3))//2
        for i in xrange(faces):
            n = 1+(i * 6)
            r = colours[(i*18)]
            g = colours[(i*18)+1]
            b = colours[(i*18)+2]
            colour = r<<24 | g<<16 | b<<8
            f.write("usemtl %s\r\n" % mats[colour])
            f.write("f %i %i %i\r\n" % (n, n+2, n+1))
            f.write("f %i %i %i\r\n" % (n+5, n+4, n+3))

        # Tidy up
        f.close()
        
        # Create our material file
        f = open(mat_filename,"wt")
        for colour, material in mats.items():
            f.write("newmtl %s\r\n" % material)
            r = (colour & 0xff000000) >> 24
            g = (colour & 0xff0000) >> 16
            b = (colour & 0xff00) >> 8
            r = r / 255.0
            g = g / 255.0
            b = b / 255.0
            f.write("Ka %f %f %f\r\n" % (r, g, b))
            f.write("Kd %f %f %f\r\n" % (r, g, b))
        f.close()


register_plugin(ObjFile, "OBJ exporter", "1.0")
