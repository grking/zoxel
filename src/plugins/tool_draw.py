# tool_draw.py
# Simple drawing tool.
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
from tool import Tool, EventData, MouseButtons, KeyModifiers, Face
from plugin_api import register_plugin

class DrawingTool(Tool):

    def __init__(self, api):
        super(DrawingTool, self).__init__(api)
        # Create our action / icon
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/images/gfx/icons/pencil.png"),
            "Draw", None)
        self.action.setStatusTip("Draw Voxels")
        self.action.setCheckable(True)
        # Register the tool
        self.api.register_tool(self, True)

    # Tries to plot a new voxel at target location.
    # param choosen_target: The place where the new voxel should be inserted.
    # returns A Target object indicating the actual place where the voxel were
    # inserted. Returns None when no insertion was made.
    def _draw_voxel(self, target):
        # Works out where exactly the new voxel goes. It can collide with an existing voxel or with the bottom of the 'y' plane,
        #in which case, pos will be different than None.
        pos = target.get_neighbour()
        if pos:
            target.world_x = pos[0]
            target.world_y = pos[1]
            target.world_z = pos[2]
        # Tries to set the voxel on the matrix and then returns the Target 
        # with it's coordinates, if it exists.
        if( target.voxels.set(target.world_x, target.world_y, target.world_z, 
                              self.colour) ):
            return target
        else:
            return None

    def _get_valid_sequence_faces(self, face):
        if( face in Face.COLLIDABLE_FACES_PLANE_X ):
            return Face.COLLIDABLE_FACES_PLANE_Y + Face.COLLIDABLE_FACES_PLANE_Z
        elif( face in Face.COLLIDABLE_FACES_PLANE_Y ):
            return Face.COLLIDABLE_FACES_PLANE_X + Face.COLLIDABLE_FACES_PLANE_Z
        elif( face in Face.COLLIDABLE_FACES_PLANE_Z ):
            return Face.COLLIDABLE_FACES_PLANE_X + Face.COLLIDABLE_FACES_PLANE_Y
        else:
            return None

    # Draw a new voxel next to the targeted face
    def on_mouse_click(self, data):
        if data.mouse_button == MouseButtons.LEFT:
            self._first_target = self._draw_voxel(data)
        elif data.mouse_button == MouseButtons.RIGHT:
            data.voxels.set(data.world_x, data.world_y, data.world_z, 0)

    # Start a drag
    def on_drag_start(self, data):
        self._first_target = data

    # When dragging, Draw a new voxel next to the targeted face
    def on_drag(self, data):
        # In case the first click has missed a valid target.
        if( self._first_target is None ):
            return
        valid_faces = self._get_valid_sequence_faces(self._first_target.face)
        if( ( not valid_faces ) or ( data.face not in valid_faces ) ):
            return
        self._draw_voxel(data)

register_plugin(DrawingTool, "Drawing Tool", "1.0")