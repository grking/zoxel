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
    # Defining the faces for each plane used in the collision detection algorithm, where the Y plane is collidable (But X and Z are not).
    COLLIDABLE_FACES_PLANE_X = FACES_PLANE_X
    COLLIDABLE_FACES_PLANE_Y = FACES_PLANE_Y + [None]
    COLLIDABLE_FACES_PLANE_Z = FACES_PLANE_Z


class Target(object):

    @property
    def face(self):
        return self._face

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def voxels(self):
        return self._voxels

    def __repr__(self):
        return 'Target(face=%s,x=%d,y=%d,z=%d)' % (self._face, self._x, self._y, self._z)

    def __init__(self, voxels, x, y, z, face = None):
        self._face = face
        self._x = x
        self._y = y
        self._z = z
        self._voxels = voxels

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
        x = self.x
        y = self.y
        z = self.z
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

    # Called when the left mouse button is pressed
    def on_activate(self, target):
        pass

    # Called when the left mouse button is held down and dragged
    def on_drag(self, target):
        pass

    # Called when the left mouse button is released
    def on_deactivate(self, target):
        pass

    # Should return the action for the tool
    def get_action(self):
        return self.action
