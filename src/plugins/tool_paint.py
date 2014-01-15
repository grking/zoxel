# tool_paint.py
# Simple painting tool.
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

class PaintingTool(Tool):

    def __init__(self, api):
        super(PaintingTool, self).__init__(api)
        # Create our action / icon
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/images/gfx/icons/paint-brush.png"),
            "Paint", None)
        self.action.setStatusTip("Colour Voxels")
        self.action.setCheckable(True)
        # Register the tool
        self.api.register_tool(self)

    # Colour the targeted voxel
    def on_mouse_click(self, data):
        # If we have a voxel at the target, colour it
        voxel = data.voxels.get(data.world_x, data.world_y, data.world_z)
        if voxel:
            data.voxels.set(data.world_x, data.world_y, data.world_z, self.colour)

    # Colour when dragging also
    def on_drag(self, data):
        self.on_mouse_click(data)

register_plugin(PaintingTool, "Painting Tool", "1.0")