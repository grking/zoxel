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

class ZoxelFile(object):
    
    # Description of file type
    description = "Zoxel Files"
    
    # File type filter
    filetype = "*.zox"

    # We are pasased the mainwindow as a parent on construction
    def __init__(self, parent):
        self.parent = parent
        # Register our exporter
        self.parent.register_file_handler(self)
        # File version format we support
        self._file_version = 1

    # Called when we need to save. Should raise an exception if there is a
    # problem saving.
    def save(self, filename):
        # grab the voxel data
        voxels = self.parent.get_voxel_data()

        # File version
        version = self._file_version
        
        # Build data structure
        data = {'version': version, 'frames': 1}
        data['frame1'] = voxels._data
        
        # Open our file
        f = open(filename,"wt")
        
        f.write(json.dumps(data))

        # Tidy up
        f.close()

    # Called when we need to load a file. Should raise an exception if there
    # is a problem.
    def load(self, filename):
        # grab the voxel data
        voxels = self.parent.get_voxel_data()

        # Load the file data
        f = open(filename, "rt")
        try:
            data = json.loads(f.read())
        except Exception as Ex:
            raise Exception("Doesn't look like a valid Zoxel file (%s)" % Ex)
        f.close()
        
        # Check we understand it
        if int(data['version']) > self._file_version:
            raise Exception("More recent version of Zoxel needed to open file.")
        
        # Load the data
        voxels._data = data['frame1']
