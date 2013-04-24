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
from tool import Tool
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
        self.api.register_tool(self)
    
    # Draw a new voxel next to the targeted face
    def on_activate(self, target):
        # Work out where exactly the new voxel goes
        pos = target.get_neighbour()
        if pos:
            target.voxels.set(pos[0], pos[1], pos[2], self.colour)
        else:
            # Just place voxel at this positon
            target.voxels.set(target.x, target.y, target.z, self.colour)

register_plugin(DrawingTool, "Drawing Tool", "1.0")