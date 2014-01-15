# tool.py
# Base class for tools
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

from PySide import QtGui

# Enumeration type
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Mouse buttons
MouseButtons = enum('LEFT', 'MIDDLE', 'RIGHT')

# Keyboard modifiers
KeyModifiers = enum('CTRL', 'SHIFT', 'ALT')

class Face(object):
    FRONT = 0   # z-
    TOP = 1     # y+
    LEFT = 2    # x+
    RIGHT = 3   # x-
    BACK = 4    # z+
    BOTTOM = 5  # y-
    # Defining the faces for each plane, where "*_PLANE[0] = +" and "*_PLANE[1] = -"
    FACES_PLANE_X = [LEFT, RIGHT]
    FACES_PLANE_Y = [TOP, BOTTOM]
    FACES_PLANE_Z = [BACK, FRONT]
    # Defining the faces for each plane used in the collision detection 
    # algorithm, where the Y plane is collidable (But X and Z are not).
    COLLIDABLE_FACES_PLANE_X = FACES_PLANE_X
    COLLIDABLE_FACES_PLANE_Y = FACES_PLANE_Y + [None]
    COLLIDABLE_FACES_PLANE_Z = FACES_PLANE_Z

class EventData(object):

    @property
    def face(self):
        return self._face
    @face.setter
    def face(self, value):
        self._face = value

    @property
    def world_x(self):
        return self._world_x
    @world_x.setter
    def world_x(self, value):
        self._world_x = value

    @property
    def world_y(self):
        return self._world_y
    @world_y.setter
    def world_y(self, value):
        self._world_y = value

    @property
    def world_z(self):
        return self._world_z
    @world_z.setter
    def world_z(self, value):
        self._world_z = value

    @property
    def voxels(self):
        return self._voxels
    @voxels.setter
    def voxels(self, value):
        self._voxels = value

    @property
    def mouse_x(self):
        return self._mouse_x
    @mouse_x.setter
    def mouse_x(self, value):
        self._mouse_x = value

    @property
    def mouse_y(self):
        return self._mouse_y
    @mouse_y.setter
    def mouse_y(self, value):
        self._mouse_y = value

    @property
    def mouse_button(self):
        return self._mouse_button
    @mouse_button.setter
    def mouse_button(self, value):
        self._mouse_button = value

    @property
    def key_modifiers(self):
        return self._key_modifiers
    @key_modifiers.setter
    def key_modifiers(self, value):
        self._key_modifiers = value

    def __repr__(self):
        return ('EventData(face={0},world_x={1},world_y={2},world_z={3},'
                'mouse_x={4},mouse_y={5},mouse_button={6},key_modifiers={7})'.format( 
                self._face, self._world_x, self._world_y, self._world_z,
                   self._mouse_x, self._mouse_y, self._mouse_button, 
                   self._key_modifiers))

    def __init__(self):
        self._face = None
        self._world_x = 0
        self._world_y = 0
        self._world_z = 0
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_button = None
        self._key_modifiers = None
        self._voxels = None

    def __eq__(self, other):
        return ( (self._x == other._x) and
            (self._y == other._y ) and
            (self._z == other._z ) and
            (self._face == other._face ) and
            (self._voxels == other._voxels ) )

    # Returns the coordinates of the voxel next to the selected face.
    # Or None if there is not one.
    def get_neighbour(self):
        if self.face is None:
            return None
        x = self._world_x
        y = self._world_y
        z = self._world_z
        if self.face == Face.TOP:
            y += 1
        elif self.face == Face.BOTTOM:
            y -=1
        elif self.face == Face.BACK:
            z += 1
        elif self.face == Face.FRONT:
            z -= 1
        elif self.face == Face.LEFT:
            x -= 1
        elif self.face == Face.RIGHT:
            x += 1
        return (x, y, z)

class Tool(object):

    @property
    # Returns the currently selected colour
    def colour(self):
        return self.api.get_palette_colour()

    def __init__(self, api):
        self.api = api
        # Create default action
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/gfx/icons/wrench.png"),
            "A Tool", None)
        self.action.setStatusTip("Unknown Tool")

    # Mouse click - a mouse button has been pressed and released
    def on_mouse_click(self, data):
        pass
    
    # A mouse drag has started
    def on_drag_start(self, data):
        pass
    
    # Mouse is dragging
    def on_drag(self, data):
        pass
    
    # A mouse drag ended
    def on_drag_end(self, data):
        pass

    # Signal to the tool to cancel whatever it's doing and reset it's state
    # back to default
    def on_cancel(self, data):
        pass
    
    # Should return the action for the tool
    def get_action(self):
        return self.action
