# voxel.py
# Simple voxel data structure
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

# The VoxelData class presents a simple interface to a voxel world.  X, Y & Z
# coordinates of voxels run from zero up the positive axis.
#
# Voxel types can be set with a simple call to set(), passing in voxel
# coordinates.
#
# get_vertices() returns a list of vertices, along with normals and colours
# which describes the current state of the voxel world.

# Default world dimensions (in voxels)
# We are an editor for "small" voxel models. So this needs to be small.
# Dimensions are fundamentally limited by our encoding of face ID's into
# colours (for picking) to 127x127x126.
_WORLD_WIDTH = 32
_WORLD_HEIGHT = 32
_WORLD_DEPTH = 32

# Types of voxel
EMPTY = 0
FULL = 1

class VoxelData(object):

    # World dimension properties
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height
    @property
    def depth(self):
        return self._depth
    
    @property
    def changed(self):
        return self._changed
    @changed.setter
    def changed(self, value):
        if value and not self._changed:
            # Let whoever is watching us know about the change
            self._changed = value
            if self.notify:
                self.notify()
        self._changed = value

    def __init__(self):
        # Default size
        self._width = _WORLD_WIDTH
        self._height = _WORLD_HEIGHT
        self._depth = _WORLD_DEPTH
        self._initialise_data()
        # Callback when our data changes 
        self.notify = None

    # Initialise our data
    def _initialise_data(self):
        # Our scene data
        self._data = [[[0 for k in xrange(self.depth)]
            for j in xrange(self.height)]
                for i in xrange(self.width)]
        # Our cache of non-empty voxels (coordinate groups)
        self._cache = []
        # Flag indicating if our data has changed
        self._changed = False

    # Set a voxel to the given state
    def set(self, x, y, z, state):
        # If this looks like a QT Color instance, convert it
        if hasattr(state, "getRgb"):
            c = state.getRgb()
            state = c[0]<<24 | c[1]<<16 | c[2]<<8 | 0xff

        # Check bounds
        if (x < 0 or x >= self.width 
            or y < 0 or y >= self.height 
            or z < 0 or z >= self.depth):
            return
        self._data[x][y][z] = state
        self.changed = True
        if state != EMPTY:
            if (x,y,z) not in self._cache:
                self._cache.append((x,y,z))
        else:
            if (x,y,z) in self._cache:
                self._cache.remove((x,y,z))

    # Get the state of the given voxel
    def get(self, x, y, z):
        if (x < 0 or x >= self.width
            or y < 0 or y >= self.height
            or z < 0 or z >= self.depth):
            return EMPTY
        return self._data[x][y][z]

    # Clear our voxel data
    def clear(self):
        self._initialise_data()

    # Return full vertex list
    def get_vertices(self):
        vertices = []
        colours = []
        colour_ids = []
        normals = []
        for x,y,z in self._cache:
            v, c, n, id = self._get_voxel_vertices(x, y, z)
            vertices += v
            colours += c
            normals += n
            colour_ids += id
        return (vertices, colours, normals, colour_ids)

    # Called to notify us that our data has been saved. i.e. we can set 
    # our "changed" status back to False.
    def saved(self):
        self.changed = False

    # Return the verticies for the given voxel. We center our vertices at the origin
    def _get_voxel_vertices(self, x, y, z):
        vertices = []
        colours = []
        normals = []
        colour_ids = []

        # Determine if we have filled voxels around us
        front = self.get(x, y, z-1) == EMPTY
        left = self.get(x-1, y, z) == EMPTY
        right = self.get(x+1, y, z) == EMPTY
        top = self.get(x, y+1, z) == EMPTY
        back = self.get(x, y, z+1) == EMPTY
        bottom = self.get(x, y-1, z) == EMPTY

        # Get our colour
        c = self.get(x, y, z)
        r = (c & 0xff000000)>>24
        g = (c & 0xff0000)>>16
        b = (c & 0xff00)>>8
        colour = (r, g, b)

        # Encode our voxel space coordinates as colours, used for face selection
        # We use 7 bits per coordinate and the bottom 3 bits for face:
        #   0 - front
        #   1 - top
        #   2 - left
        #   3 - right
        #   4 - back
        #   5 - bottom
        voxel_id = (x & 0x7f)<<17 | (y & 0x7f)<<10 | (z & 0x7f)<<3
        id_r = (voxel_id & 0xff0000)>>16
        id_g = (voxel_id & 0xff00)>>8
        id_b = (voxel_id & 0xff)

        # Adjust coordinates to the origin
        x, y, z = self.voxel_to_world(x, y, z)

        # Front face
        if front:
            vertices += (x,   y,   z)
            vertices += (x,   y+1, z)
            vertices += (x+1, y,   z)
            vertices += (x+1, y,   z)
            vertices += (x,   y+1, z)
            vertices += (x+1, y+1, z)
            colours += colour * 6
            normals += (0, 0, 1) * 6
            colour_ids += (id_r, id_g, id_b) * 6
        # Top face
        if top:
            vertices += (x,   y+1, z)
            vertices += (x,   y+1, z-1)
            vertices += (x+1, y+1, z)
            vertices += (x+1, y+1, z)
            vertices += (x,   y+1, z-1)
            vertices += (x+1, y+1, z-1)
            colours += colour * 6
            normals += (0, 1, 0) * 6
            colour_ids += (id_r, id_g, id_b | 1) * 6
        # Right face
        if right:
            vertices += (x+1, y, z)
            vertices += (x+1, y+1, z)
            vertices += (x+1, y, z-1)
            vertices += (x+1, y, z-1)
            vertices += (x+1, y+1, z)
            vertices += (x+1, y+1, z-1)
            colours += colour * 6
            normals += (1, 0, 0) * 6
            colour_ids += (id_r, id_g, id_b | 3) * 6
        # Left face
        if left:
            vertices += (x, y, z-1)
            vertices += (x, y+1, z-1)
            vertices += (x, y, z)
            vertices += (x, y, z)
            vertices += (x, y+1, z-1)
            vertices += (x, y+1, z)
            colours += colour * 6
            normals += (-1, 0, 0) * 6
            colour_ids += (id_r, id_g, id_b | 2) * 6
        # Back face
        if back:
            vertices += (x+1, y, z-1)
            vertices += (x+1, y+1, z-1)
            vertices += (x, y, z-1)
            vertices += (x, y, z-1)
            vertices += (x+1, y+1, z-1)
            vertices += (x, y+1, z-1)
            colours += colour * 6
            normals += (0, 0, -1) * 6
            colour_ids += (id_r, id_g, id_b | 4) * 6
        # Bottom face
        if bottom:
            vertices += (x, y, z-1)
            vertices += (x, y, z)
            vertices += (x+1, y, z-1)
            vertices += (x+1, y, z-1)
            vertices += (x, y, z)
            vertices += (x+1, y, z)
            colours += colour * 6
            normals += (0, -1, 0) * 6
            colour_ids += (id_r, id_g, id_b | 5) * 6

        return (vertices, colours, normals, colour_ids)

    # Return vertices for a floor grid
    def get_grid_vertices(self):
        grid = []
        for z in xrange(self.depth+1):
            gx, gy, gz = self.voxel_to_world(0, 0, z)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(self.width, 0, z)
            grid += (gx, gy, gz)
        for x in xrange(self.width+1):
            gx, gy, gz = self.voxel_to_world(x, 0, 0)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(x, 0, self.depth)
            grid += (gx, gy, gz)
        return grid

    # Convert voxel space coordinates to world space
    def voxel_to_world(self, x, y, z):
        x = (x - self.width//2)-0.5
        y = (y - self.height//2)-0.5
        z = (z - self.depth//2)-0.5
        z = -z
        return x, y, z

    # Convert world space coordinates to voxel space
    def world_to_voxel(self, x, y, z):
        x = (x + self.width//2)+0.5
        y = (y + self.height//2)+0.5
        z = (z - self.depth//2)-0.5
        z = -z
        return x, y, z

    # Rebuild our cache
    def _cache_rebuild(self):
        self._cache = []
        for x in range(self.width):
            for z in range(self.depth):
                for y in range(self.height):
                    if self._data[x][y][z] != EMPTY:
                        self._cache.append((x, y, z))

    # Calculate the actual bounding box of the model in voxel space
    def calculate_bounding_box(self):
        minx = 999
        miny = 999
        minz = 999
        maxx = -999
        maxy = -999
        maxz = -999
        for x,y,z in self._cache:
            if x < minx:
                minx = x
            if x > maxx:
                maxx = x
            if y < miny:
                miny = y
            if y > maxy:
                maxy = y
            if z < minz:
                minz = z
            if z > maxz:
                maxz = z
        width = (maxx-minx)+1
        height = (maxy-miny)+1
        depth = (maxz-minz)+1
        return minx, miny, minz, width, height, depth

    # Resize the voxel space. If no dimensions given, adjust to bounding box
    def resize(self, width = None, height = None, depth = None):
        # No dimensions, use bounding box
        # FIXME We just adjust to bounding box
        mx, my, mz, width, height, depth = self.calculate_bounding_box()
        # Create new data structure of the required size
        data = [[[0 for k in xrange(depth)]
            for j in xrange(height)]
                for i in xrange(width)]
        # Calculate translation
        dx = 0-mx # XXX
        dy = 0-my
        dz = 0-mz
        # Copy data over at new location
        for x in xrange(mx, mx+width):
            for y in xrange(my, my+height):
                for z in xrange(mz, mz+depth):
                    data[x+dx][y+dy][z+dz] = self._data[x][y][z]
        # Set new dimensions
        self._width = width
        self._height = height
        self._depth = depth
        self._data = data
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True
