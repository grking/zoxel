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
import copy
from undo import Undo, UndoItem

# Default world dimensions (in voxels)
# We are an editor for "small" voxel models. So this needs to be small.
# Dimensions are fundamentally limited by our encoding of face ID's into
# colours (for picking) to 127x127x126.
_WORLD_WIDTH = 16
_WORLD_HEIGHT = 16
_WORLD_DEPTH = 16

# Types of voxel
EMPTY = 0
FULL = 1

# Occlusion factor
OCCLUSION = 0.7

class VoxelData(object):

    # Constants for referring to axis
    X_AXIS = 1
    Y_AXIS = 2
    Z_AXIS = 3
    
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
        # Our undo buffer
        self._undo = Undo()
        # Init data
        self._initialise_data()
        # Callback when our data changes
        self.notify_changed = None
        # Ambient occlusion type effect
        self._occlusion = True

    # Initialise our data
    def _initialise_data(self):
        # Our scene data
        self._data = self.blank_data()
        # Our cache of non-empty voxels (coordinate groups)
        self._cache = []
        # Flag indicating if our data has changed
        self._changed = False
        # Reset undo buffer
        self._undo.clear()
        # Animation
        self._frame_count = 1
        self._current_frame = 0
        self._frames = [self._data]

    # Return an empty voxel space
    def blank_data(self):
        return [[[0 for _ in xrange(self.depth)]
            for _ in xrange(self.height)]
                for _ in xrange(self.width)]

    def is_valid_bounds(self, x, y, z):
        return (
            x >= 0 and x < self.width and
            y >= 0 and y < self.height and
            z >= 0 and z < self.depth
        )

    # Return the number of animation frames
    def get_frame_count(self):
        return self._frame_count

    # Change to the given frame
    # FIXME - support frame specific undo buffers
    def select_frame(self, frame_number):
        # Sanity
        if frame_number < 0 or frame_number >= self._frame_count:
            return
        # Make sure we really have a pointer to the current data
        self._frames[self._current_frame] = self._data
        # Change to new frame
        self._data = self._frames[frame_number]
        self._current_frame = frame_number
        self._undo.frame = self._current_frame
        self._cache_rebuild()
        self.changed = True

    # Add a new frame by copying the current one
    def add_frame(self, copy_current = True):
        if copy_current:
            data = self.get_data()
        else:
            data = self.blank_data()
        self._frames.insert(self._current_frame+1, data)
        self._undo.add_frame(self._current_frame+1)
        self._frame_count += 1
        self.select_frame(self._current_frame+1)

    # Delete the current frame
    def delete_frame(self):
        # Sanity - we can't have no frames at all
        if self._frame_count <= 1:
            return
        # Remember the frame we want to delete
        killframe = self._current_frame
        # Select a different frame
        self.select_previous_frame()
        # Remove the old frame
        del self._frames[killframe]
        self._undo.delete_frame(killframe)
        self._frame_count -= 1
        # If we only have one frame left, must be first frame
        if self._frame_count == 1:
            self._current_frame = 0
        # If we wrapped around, fix the frame pointer
        if self._current_frame > killframe:
            self._current_frame -= 1

    # Change to the next frame (with wrap)
    def select_next_frame(self):
        nextframe = self._current_frame+1
        if nextframe >= self._frame_count:
            nextframe = 0
        self.select_frame(nextframe)

    # Change to the previous frame (with wrap)
    def select_previous_frame(self):
        prevframe = self._current_frame-1
        if prevframe < 0:
            prevframe = self._frame_count-1
        self.select_frame(prevframe)

    # Get current frame number
    def get_frame_number(self):
        return self._current_frame

    # Set a voxel to the given state
    def set(self, x, y, z, state, undo = True):
        # If this looks like a QT Color instance, convert it
        if hasattr(state, "getRgb"):
            c = state.getRgb()
            state = c[0]<<24 | c[1]<<16 | c[2]<<8 | 0xff

        # Check bounds
        if ( not self.is_valid_bounds(x, y, z ) ):
            return False
        # Set the voxel
        if ( self.is_valid_bounds(x, y, z ) ):
            # Add to undo
            if undo:
                self._undo.add(UndoItem(Undo.SET_VOXEL, 
                (x, y, z, self._data[x][y][z]), (x, y, z, state)))
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

    # Return a copy of the voxel data
    def get_data(self):
        return copy.deepcopy(self._data)

    # Set all of our data at once
    def set_data(self, data):
        self._data = copy.deepcopy(data)
        self._cache_rebuild()
        self.changed = True

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
    # Consider all animation frames
    def get_bounding_box(self):
        minx = 999
        miny = 999
        minz = 999
        maxx = -999
        maxy = -999
        maxz = -999
        for data in self._frames:
            for x in range(self.width):
                for z in range(self.depth):
                    for y in range(self.height):
                        if data[x][y][z] != EMPTY:
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
    # Resize all animation frames
    def resize(self, width = None, height = None, depth = None, shift = 0):
        # Reset undo buffer
        self._undo.clear()
        # No dimensions, use bounding box
        mx, my, mz, cwidth, cheight, cdepth = self.get_bounding_box()
        if not width:
            width, height, depth = cwidth, cheight, cdepth
        for i, frame in enumerate(self._frames):
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
                        data[x+dx][y+dy][z+dz] = frame[x][y][z]
            self._frames[i] = data
        self._data = self._frames[self._current_frame]
        # Set new dimensions
        self._width = width
        self._height = height
        self._depth = depth
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True

    # Rotate voxels in voxel space 90 degrees
    def rotate_about_axis(self, axis):
        # Reset undo buffer
        self._undo.clear()

        if axis == self.Y_AXIS:
            width = self.depth # note swap
            height = self.height
            depth = self.width
        elif axis == self.X_AXIS:
            width = self.width
            height = self.depth
            depth = self.height
        elif axis == self.Z_AXIS:
            width = self.height
            height = self.width
            depth = self.depth

        for i, frame in enumerate(self._frames):
                    
            # Create new temporary data structure
            data = [[[0 for _ in xrange(depth)]
                for _ in xrange(height)]
                    for _ in xrange(width)]
            
            # Copy data over at new location
            for tx in xrange(0, self.width):
                for ty in xrange(0, self.height):
                    for tz in xrange(0, self.depth):
                        if axis == self.Y_AXIS:
                            dx = (-tz)-1
                            dy = ty
                            dz = tx
                        elif axis == self.X_AXIS:
                            dx = tx
                            dy = (-tz)-1
                            dz = ty
                        elif axis == self.Z_AXIS:
                            dx = ty
                            dy = (-tx)-1
                            dz = tz
                        data[dx][dy][dz] = frame[tx][ty][tz]
            self._frames[i] = data
        
        self._width = width
        self._height = height
        self._depth = depth
        
        self._data = self._frames[self._current_frame]
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True
    
    # Translate the voxel data.
    def translate(self, x, y, z, undo = True):
        # Sanity
        if x == 0 and y == 0 and z == 0:
            return
        
        # Add to undo
        if undo:
            self._undo.add(UndoItem(Undo.TRANSLATE, 
            (-x, -y, -z), (x, y, z)))
        
        # Create new temporary data structure
        data = [[[0 for _ in xrange(self.depth)]
            for _ in xrange(self.height)]
                for _ in xrange(self.width)]
        # Copy data over at new location
        for tx in xrange(0, self.width):
            for ty in xrange(0, self.height):
                for tz in xrange(0, self.depth):
                    dx = (tx+x) % self.width
                    dy = (ty+y) % self.height
                    dz = (tz+z) % self.depth
                    data[dx][dy][dz] = self._data[tx][ty][tz]
        self._data = data
        self._frames[self._current_frame] = self._data
        # Rebuild our cache
        self._cache_rebuild()
        self.changed = True

    # Undo previous operation
    def undo(self):
        op = self._undo.undo()
        # Voxel edit
        if op and op.operation == Undo.SET_VOXEL:
            data = op.olddata
            self.set(data[0], data[1], data[2], data[3], False)
        # Translation
        elif op and op.operation == Undo.TRANSLATE:
            data = op.olddata
            self.translate(data[0], data[1], data[2], False)
            
    # Redo an undone operation
    def redo(self):
        op = self._undo.redo()
        # Voxel edit
        if op and op.operation == Undo.SET_VOXEL:
            data = op.newdata
            self.set(data[0], data[1], data[2], data[3], False)
        # Translation
        elif op and op.operation == Undo.TRANSLATE:
            data = op.newdata
            self.translate(data[0], data[1], data[2], False)

    # Enable/Disable undo buffer
    def disable_undo(self):
        self._undo.enabled = False
    def enable_undo(self):
        self._undo.enabled = True
