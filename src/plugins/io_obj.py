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

        # Export vertices
        i = 0
        while i < len(vertices):
            f.write("v %f %f %f\r\n" % 
                (vertices[i], vertices[i+1], vertices[i+2]))
            i += 3
            
        # Export faces
        faces = (len(vertices)//(3*3))//2
        for i in xrange(faces):
            n = 1+(i * 6)
            f.write("f %i %i %i\r\n" % (n, n+2, n+1))
            f.write("f %i %i %i\r\n" % (n+5, n+4, n+3))

        # Tidy up
        f.close()


register_plugin(ObjFile, "OBJ exporter", "1.0")
