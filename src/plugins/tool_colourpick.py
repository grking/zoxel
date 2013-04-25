# tool_colourpick.py
# Simple colour picking tool.
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

class ColourPickTool(Tool):
    
    def __init__(self, api):
        super(ColourPickTool, self).__init__(api)
        # Create our action / icon
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/images/gfx/icons/pipette.png"), 
            "Colour Pick", None)
        self.action.setStatusTip("Choose a colour from an existing voxel.")
        self.action.setCheckable(True)
        # Register the tool
        self.api.register_tool(self)
    
    # Grab the colour of the selected voxel
    def on_activate(self, target):
        # If we have a voxel at the target, colour it
        voxel = target.voxels.get(target.x, target.y, target.z)
        if voxel:    
            self.api.set_palette(voxel)

register_plugin(ColourPickTool, "Colour Picking Tool", "1.0")