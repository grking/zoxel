# io_zoxel.py
# Zoxel native file format import/exporter
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
from constants import ZOXEL_VERSION

class ZoxelFile(object):

    # Description of file type
    description = "Zoxel Files"

    # File type filter
    filetype = "*.zox"

    def __init__(self, api):
        self.api = api
        # Register our exporter
        self.api.register_file_handler(self)
        # File version format we support
        self._file_version = 1

    # Called when we need to save. Should raise an exception if there is a
    # problem saving.
    def save(self, filename):
        # grab the voxel data
        voxels = self.api.get_voxel_data()

        # File version
        version = self._file_version

        # Build data structure
        data = {'version': version, 'frames': 1,
                "creator": "Zoxel Version "+ZOXEL_VERSION}
        frame = []
        for y in range(voxels.height):
            for z in range(voxels.depth):
                for x in range(voxels.width):
                    v = voxels.get(x, y, z)
                    if v:
                        frame.append((x,y,z,v))

        data['frame1'] = frame
        data['width'] = voxels.width
        data['height'] = voxels.height
        data['depth'] = voxels.depth

        # Open our file
        f = open(filename,"wt")

        f.write(json.dumps(data))

        # Tidy up
        f.close()

    # Called when we need to load a file. Should raise an exception if there
    # is a problem.
    def load(self, filename):        
        # grab the voxel data
        voxels = self.api.get_voxel_data()

        # Load the file data
        f = open(filename, "rt")
        try:
            data = json.loads(f.read())
        except Exception as Ex:
            raise Exception("Doesn't look like a valid Zoxel file (%s)" % Ex)
        f.close()

        # Check we understand it
        if data['version'] > self._file_version:
            raise Exception("More recent version of Zoxel needed to open file.")

        # Load the data
        frame = data['frame1']
        
        # Do we have model dimensions
        if 'width' in data:
            # Yes, so resize to them
            voxels.resize(data['width'], data['height'], data['depth'])
        else:
            # Zoxel file with no dimension data, determine size
            maxX = -127
            maxY = -127
            maxZ = -127
            for x, y, z, v in frame:
                if x > maxX:
                    maxX = x
                if y > maxY:
                    maxY = y
                if z > maxZ:
                    maxZ = z
            # Resize
            voxels.resize(maxX+1, maxY+1, maxZ+1)
        
        # Write the voxel data
        for x, y, z, v in frame:
            voxels.set(x, y, z, v)
            

register_plugin(ZoxelFile, "Zoxel file format IO", "1.0")
