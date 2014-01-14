# io_qubicle.py
# Qubicle Constructor Binary File IO
# Copyright (c) 2014, Graham R King
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
from plugin_api import register_plugin

class QubicleFile(object):

    # Description of file type
    description = "Qubicle Files"

    # File type filter
    filetype = "*.qb"

    def __init__(self, api):
        self.api = api
        # Register our exporter
        self.api.register_file_handler(self)

    # Helper function to read/write uint32
    def uint32(self, f, value = None):
        if value is not None:
            # Write
            data = bytearray()
            data.append((value & 0xff));
            data.append((value & 0xff00)>>8);
            data.append((value & 0xff0000)>>16);
            data.append((value & 0xff000000)>>24);
            f.write(data)
        else:
            # Read
            x = bytearray(f.read(4))
            if len(x) == 4:
                return x[0] | x[1]<<8 | x[2]<<16 | x[3]<<24
            return 0

    # Called when we need to save. Should raise an exception if there is a
    # problem saving.
    def save(self, filename):
        # grab the voxel data
        voxels = self.api.get_voxel_data()

        # Open our file
        f = open(filename,"wb")

        # Version 
        self.uint32(f, 0x00000101)
        # Colour format RGBA
        self.uint32(f, 0)
        # Left handed coords
        self.uint32(f, 0)
        # Uncompressed
        self.uint32(f, 0)
        # Visability mask 
        self.uint32(f, 0)
        # Matrix count
        self.uint32(f, 1)
        
        # Model name length
        name = "Model"
        f.write(str(chr(len(name))))
        # Model name
        f.write(name)
        
        # X, Y, Z dimensions
        self.uint32(f, voxels.width)
        self.uint32(f, voxels.height)
        self.uint32(f, voxels.depth)

        # Matrix position
        self.uint32(f, 0)
        self.uint32(f, 0)
        self.uint32(f, 0)

        # Data
        for z in xrange(voxels.depth):
            for y in xrange(voxels.height):
                for x in xrange(voxels.width):
                    vox = voxels.get(x, y, z)
                    alpha = 0xff
                    if not vox:
                        alpha = 0x00
                    r = (vox & 0xff000000)>>24
                    g = (vox & 0xff0000)>>16
                    b = (vox & 0xff00)>>8
                    vox = r | g<<8 | b<<16 | alpha<<24
                    self.uint32(f, vox)

        # Tidy up
        f.close()

    # Load a Qubicle Constructor binary file
    def load(self, filename):
        # grab the voxel data
        voxels = self.api.get_voxel_data()

        # Open our file
        f = open(filename,"rb")

        # Version 
        version = self.uint32(f)
        # Colour format RGBA
        format =self.uint32(f)
        if format:
            raise Exception("Unsupported colour format")
        # Left handed coords
        coords = self.uint32(f)
        # Uncompressed
        compression = self.uint32(f)
        if compression:
            raise Exception("Compressed .qb files not yet supported")
        # Visability mask 
        mask = self.uint32(f)
        # Matrix count
        matrix_count = self.uint32(f)
        
        # Warn about multiple matrices
        if matrix_count > 1:
            self.api.warning("Qubicle files with more than 1 matrix"
                             " are not yet properly supported. All "
                             " matrices will be (badly) merged.")
        
        max_width = 0
        max_height = 0
        max_depth = 0
        
        for i in xrange(matrix_count):
        
            # Name length
            namelen = int(ord(f.read(1)))
            name = f.read(namelen)
        
            # X, Y, Z dimensions
            width = self.uint32(f)
            height = self.uint32(f)
            depth = self.uint32(f)
            
            # Don't allow huge models
            if width > 127 or height > 127 or depth > 127:
                raise Exception("Model to large - max 127x127x127")
    
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height
            if depth > max_depth:
                max_depth = depth
    
            voxels.resize(max_width, max_height, max_depth)
    
            # Matrix position - FIXME not yet supported
            dx = self.uint32(f)
            dy = self.uint32(f)
            dz = self.uint32(f)
    
            # Data
            for z in xrange(depth):
                for y in xrange(height):
                    for x in xrange(width):
                        vox = self.uint32(f)
                        vox = (vox & 0x00ffffff)
                        if vox:
                            r = (vox & 0x000000ff)>>0
                            g = (vox & 0x0000ff00)>>8
                            b = (vox & 0x00ff0000)>>16
                            vox = (r<<24) | (g<<16) | (b<<8) | 0xff
                            voxels.set(x, y, z, vox)

        f.close()


register_plugin(QubicleFile, "Qubicle Constructor file format IO", "1.0")
