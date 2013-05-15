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

import math

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

# Occlusion factor
OCCLUSION = 0.7

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
            if self.notify_changed:
                self.notify_changed()
        self._changed = value

    @property
    def autoresize(self):
        return self._autoresize
    @autoresize.setter
    def autoresize(self, value):
        self._autoresize = value

    @property
    def occlusion(self):
        return self._occlusion
    @occlusion.setter
    def occlusion(self, value):
        self._occlusion = value

    def __init__(self):
        # Default size
        self._width = _WORLD_WIDTH
        self._height = _WORLD_HEIGHT
        self._depth = _WORLD_DEPTH
        self._initialise_data()
        # Callback when our data changes
        self.notify_changed = None
        # Autoresize when setting voxels out of bounds?
        self._autoresize = True
        # Ambient occlusion type effect
        self._occlusion = True

    # Initialise our data
    def _initialise_data(self):
        # Our scene data
        self._data = [[[0 for _ in xrange(self.depth)]
            for _ in xrange(self.height)]
                for _ in xrange(self.width)]
        # Our cache of non-empty voxels (coordinate groups)
        self._cache = []
        # Flag indicating if our data has changed
        self._changed = False

    def is_valid_bounds(self, x, y, z):
        return (
            x >= 0 and x < self.width and
            y >= 0 and y < self.height and
            z >= 0 and z < self.depth
        )

    # Set a voxel to the given state
    def set(self, x, y, z, state):
        # If this looks like a QT Color instance, convert it
        if hasattr(state, "getRgb"):
            c = state.getRgb()
            state = c[0]<<24 | c[1]<<16 | c[2]<<8 | 0xff

        # Check bounds
        if ( not self.is_valid_bounds(x, y, z ) ):
            # If we are auto resizing, handle it
            if not self._autoresize:
                return False
            x, y, z = self._resize_to_include(x,y,z)
        # Set the voxel
        if ( self.is_valid_bounds(x, y, z ) ):
            self._data[x][y][z] = state
            if state != EMPTY:
                if (x,y,z) not in self._cache:
                    self._cache.append((x,y,z))
            else:
                if (x,y,z) in self._cache:
                    self._cache.remove((x,y,z))
        self.changed = True
        return True

    # Get the state of the given voxel
    def get(self, x, y, z):
        if ( not self.is_valid_bounds(x, y, z ) ):
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
        uvs = []
        for x,y,z in self._cache:
            v, c, n, cid, uv = self._get_voxel_vertices(x, y, z)
            vertices += v
            colours += c
            normals += n
            colour_ids += cid
            uvs += uv
        return (vertices, colours, normals, colour_ids, uvs)

    # Called to notify us that our data has been saved. i.e. we can set
    # our "changed" status back to False.
    def saved(self):
        self.changed = False

    # Count the number of non-empty voxels from the list of coordinates
    def _count_voxels(self, coordinates):
        count = 0
        for x,y,z in coordinates:
            if self.get(x, y, z) != EMPTY:
                count += 1
        return count

    # Return the verticies for the given voxel. We center our vertices at the origin
    def _get_voxel_vertices(self, x, y, z):
        vertices = []
        colours = []
        normals = []
        colour_ids = []
        uvs = []

        # Remember voxel coordinates
        vx, vy, vz = x,y,z

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
        # Calculate shades for our 4 occlusion levels
        shades = []
        for c in range(5):
            shades.append((
                int(r*math.pow(OCCLUSION,c)),
                int(g*math.pow(OCCLUSION,c)),
                int(b*math.pow(OCCLUSION,c))))

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
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx,vy+1,vz-1) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx-1,vy,vz-1) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx+1,vy,vz-1) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx,vy-1,vz-1) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx-1,vy-1,vz-1) != EMPTY:
                    occ1 += 1
                if self.get(vx-1,vy+1,vz-1) != EMPTY:
                    occ2 += 1
                if self.get(vx+1,vy-1,vz-1) != EMPTY:
                    occ3 += 1
                if self.get(vx+1,vy+1,vz-1) != EMPTY:
                    occ4 += 1
            vertices += (x,   y,   z)
            colours += shades[occ1]
            vertices += (x,   y+1, z)
            colours += shades[occ2]
            vertices += (x+1, y,   z)
            colours += shades[occ3]
            vertices += (x+1, y,   z)
            colours += shades[occ3]
            vertices += (x,   y+1, z)
            colours += shades[occ2]
            vertices += (x+1, y+1, z)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (0, 0, 1) * 6
            colour_ids += (id_r, id_g, id_b) * 6
        # Top face
        if top:
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx,vy+1,vz+1) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx-1,vy+1,vz) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx+1,vy+1,vz) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx,vy+1,vz-1) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx-1,vy+1,vz-1) != EMPTY:
                    occ1 += 1
                if self.get(vx+1,vy+1,vz-1) != EMPTY:
                    occ3 += 1
                if self.get(vx+1,vy+1,vz+1) != EMPTY:
                    occ4 += 1
                if self.get(vx-1,vy+1,vz+1) != EMPTY:
                    occ2 += 1
            vertices += (x,   y+1, z)
            colours += shades[occ1]
            vertices += (x,   y+1, z-1)
            colours += shades[occ2]
            vertices += (x+1, y+1, z)
            colours += shades[occ3]
            vertices += (x+1, y+1, z)
            colours += shades[occ3]
            vertices += (x,   y+1, z-1)
            colours += shades[occ2]
            vertices += (x+1, y+1, z-1)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (0, 1, 0) * 6
            colour_ids += (id_r, id_g, id_b | 1) * 6
        # Right face
        if right:
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx+1,vy+1,vz) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx+1,vy,vz-1) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx+1,vy,vz+1) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx+1,vy-1,vz) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx+1,vy-1,vz-1) != EMPTY:
                    occ1 += 1
                if self.get(vx+1,vy+1,vz-1) != EMPTY:
                    occ2 += 1
                if self.get(vx+1,vy-1,vz+1) != EMPTY:
                    occ3 += 1
                if self.get(vx+1,vy+1,vz+1) != EMPTY:
                    occ4 += 1
            vertices += (x+1, y, z)
            colours += shades[occ1]
            vertices += (x+1, y+1, z)
            colours += shades[occ2]
            vertices += (x+1, y, z-1)
            colours += shades[occ3]
            vertices += (x+1, y, z-1)
            colours += shades[occ3]
            vertices += (x+1, y+1, z)
            colours += shades[occ2]
            vertices += (x+1, y+1, z-1)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (1, 0, 0) * 6
            colour_ids += (id_r, id_g, id_b | 3) * 6
        # Left face
        if left:
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx-1,vy+1,vz) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx-1,vy,vz+1) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx-1,vy,vz-1) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx-1,vy-1,vz) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx-1,vy-1,vz+1) != EMPTY:
                    occ1 += 1
                if self.get(vx-1,vy+1,vz+1) != EMPTY:
                    occ2 += 1
                if self.get(vx-1,vy-1,vz-1) != EMPTY:
                    occ3 += 1
                if self.get(vx-1,vy+1,vz-1) != EMPTY:
                    occ4 += 1
            vertices += (x, y, z-1)
            colours += shades[occ1]
            vertices += (x, y+1, z-1)
            colours += shades[occ2]
            vertices += (x, y, z)
            colours += shades[occ3]
            vertices += (x, y, z)
            colours += shades[occ3]
            vertices += (x, y+1, z-1)
            colours += shades[occ2]
            vertices += (x, y+1, z)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (-1, 0, 0) * 6
            colour_ids += (id_r, id_g, id_b | 2) * 6
        # Back face
        if back:
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx,vy+1,vz+1) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx+1,vy,vz+1) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx-1,vy,vz+1) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx,vy-1,vz+1) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx+1,vy-1,vz+1) != EMPTY:
                    occ1 += 1
                if self.get(vx+1,vy+1,vz+1) != EMPTY:
                    occ2 += 1
                if self.get(vx-1,vy-1,vz+1) != EMPTY:
                    occ3 += 1
                if self.get(vx-1,vy+1,vz+1) != EMPTY:
                    occ4 += 1
            vertices += (x+1, y, z-1)
            colours += shades[occ1]
            vertices += (x+1, y+1, z-1)
            colours += shades[occ2]
            vertices += (x, y, z-1)
            colours += shades[occ3]
            vertices += (x, y, z-1)
            colours += shades[occ3]
            vertices += (x+1, y+1, z-1)
            colours += shades[occ2]
            vertices += (x, y+1, z-1)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (0, 0, -1) * 6
            colour_ids += (id_r, id_g, id_b | 4) * 6
        # Bottom face
        if bottom:
            occ1 = 0
            occ2 = 0
            occ3 = 0
            occ4 = 0
            if self._occlusion:
                if self.get(vx,vy-1,vz-1) != EMPTY:
                    occ2 += 1
                    occ4 += 1
                if self.get(vx-1,vy-1,vz) != EMPTY:
                    occ1 += 1
                    occ2 += 1
                if self.get(vx+1,vy-1,vz) != EMPTY:
                    occ3 += 1
                    occ4 += 1
                if self.get(vx,vy-1,vz+1) != EMPTY:
                    occ1 += 1
                    occ3 += 1
                if self.get(vx-1,vy-1,vz+1) != EMPTY:
                    occ1 += 1
                if self.get(vx-1,vy-1,vz-1) != EMPTY:
                    occ2 += 1
                if self.get(vx+1,vy-1,vz+1) != EMPTY:
                    occ3 += 1
                if self.get(vx+1,vy-1,vz-1) != EMPTY:
                    occ4 += 1
            vertices += (x, y, z-1)
            colours += shades[occ1]
            vertices += (x, y, z)
            colours += shades[occ2]
            vertices += (x+1, y, z-1)
            colours += shades[occ3]
            vertices += (x+1, y, z-1)
            colours += shades[occ3]
            vertices += (x, y, z)
            colours += shades[occ2]
            vertices += (x+1, y, z)
            colours += shades[occ4]
            uvs += (0,0,0,1,1,0,1,0,0,1,1,1)
            normals += (0, -1, 0) * 6
            colour_ids += (id_r, id_g, id_b | 5) * 6

        return (vertices, colours, normals, colour_ids, uvs)


    # Return vertices for a floor grid
    def get_grid_vertices(self):
        grid = []
        #builds the Y_plane
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
        #builds the Z_plane
        for x in xrange(self.width+1):
            gx, gy, gz = self.voxel_to_world(x, 0, self.depth)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(x, self.height, self.depth)
            grid += (gx, gy, gz)
        for y in xrange(self.height+1):
            gx, gy, gz = self.voxel_to_world(0, y, self.depth)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(self.width, y, self.depth)
            grid += (gx, gy, gz)
        #builds the X_plane
        for y in xrange(self.height+1):
            gx, gy, gz = self.voxel_to_world(0, y, 0)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(0, y, self.depth)
            grid += (gx, gy, gz)
        for z in xrange(self.depth+1):
            gx, gy, gz = self.voxel_to_world(0, 0, z)
            grid += (gx, gy, gz)
            gx, gy, gz = self.voxel_to_world(0, self.height, z)
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
    def get_bounding_box(self):
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

    # Resize the voxel space. If no dimensions given, adjust to bounding box.
    # We offset all voxels on all axis by the given amount.
    def resize(self, width = None, height = None, depth = None, shift = 0):
        # No dimensions, use bounding box
        mx, my, mz, cwidth, cheight, cdepth = self.get_bounding_box()
        if not width:
            width, height, depth = cwidth, cheight, cdepth
        # Create new data structure of the required size
        data = [[[0 for _ in xrange(depth)]
            for _ in xrange(height)]
                for _ in xrange(width)]
        # Adjust ranges
        movewidth = min(width, cwidth)
        moveheight = min(height, cheight)
        movedepth = min(depth, cdepth)
        # Calculate translation
        dx = (0-mx)+shift
        dy = (0-my)+shift
        dz = (0-mz)+shift
        # Copy data over at new location
        for x in xrange(mx, mx+movewidth):
            for y in xrange(my, my+moveheight):
                for z in xrange(mz, mz+movedepth):
                    data[x+dx][y+dy][z+dz] = self._data[x][y][z]
        # Set new dimensions
        self._width = width
        self._height = height
        self._depth = depth
        self._data = data
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True

    # Resize our voxel space so that the out-of-bounds coordinate given
    # becomes in-bounds.  We return adjusted coordinates which take into
    # account that our voxel data will be relocated in voxel space.
    def _resize_to_include(self, x, y, z):
        # One axis must be out of bounds, which is it, and in which direction?
        dx = 0
        dy = 0
        dz = 0
        if x < 0:
            dx = -1
        if y < 0:
            dy = -1
        if z < 0:
            dz = -1
        if x >= self.width:
            dx = 1
        if y >= self.height:
            dy = 1
        if z >= self.depth:
            dz = 1
        # Resize by one voxel along the expanding axis
        dx, dy, dz = self.expand(dx, dy, dz)
        return x+dx, y+dy, z+dz

    # Expand the voxel space along a single axis.
    # Returns the amounts by which existing voxels were shifted
    def expand(self, dx, dy, dz):
        # Work out our new dimensions
        new_width = self.width+abs(dx)
        new_height = self.height+abs(dy)
        new_depth = self.depth+abs(dz)
        # Create new data structure of the required size
        data = [[[0 for _ in xrange(new_depth)]
            for _ in xrange(new_height)]
                for _ in xrange(new_width)]
        # Negative axis expansion requires shifting voxel data
        if dx < 0:
            dx = -dx
        else:
            dx = 0
        if dy < 0:
            dy = -dy
        else:
            dy = 0
        if dz < 0:
            dz = -dz
        else:
            dz = 0
        # Copy data over at new location
        for x in xrange(0, self.width):
            for y in xrange(0, self.height):
                for z in xrange(0, self.depth):
                    data[x+dx][y+dy][z+dz] = self._data[x][y][z]
        # Set new dimensions
        self._width = new_width
        self._height = new_height
        self._depth = new_depth
        self._data = data
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True
        return dx, dy, dz
