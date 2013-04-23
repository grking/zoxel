# io_sproxel.py
# Sproxel import/exporter
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

class SproxelFile(object):

    # We are pasased the mainwindow as a parent on construction
    def __init__(self, parent):
        self.parent = parent
        # Register our exporter
        self.parent.register_save_handler('Sproxel Files','*.csv',self.save)

    # Called when we need to save. Should raise an exception if there is a
    # problem saving.
    def save(self, filename):
        # grab the voxel data
        voxels = self.parent.get_voxel_data()

        # Open our file
        f = open(filename,"wt")

        # First Sproxel line is model dimenstions
        f.write("%i,%i,%i\n" % (voxels.width, voxels.height, voxels.depth))

        # Then we save from the top of the model
        for y in xrange(voxels.height-1, -1, -1):
            for z in xrange(voxels.depth-1, -1, -1):
                line = []
                for x in xrange(voxels.width):
                    voxel = voxels.get(x, y, z)
                    if voxel == 0:
                        line.append("#00000000")
                    else:
                        voxel = (voxel & 0xffffff00) | 0xff
                        line.append("#"+hex(voxel)[2:].upper().rjust(8,"0"))
                f.write(",".join(line)+"\n")
            f.write("\n")

        # Tidy up
        f.close()
