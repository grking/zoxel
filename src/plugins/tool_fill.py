# tool_floodfill.py
# Simple tool for flood fill.
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

class FillTool(Tool):
    
    def __init__(self, api):
        super(FillTool, self).__init__(api)
        # Create our action / icon
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/images/gfx/icons/paint-can.png"), 
            "Fill", None)
        self.action.setStatusTip("Flood fill with colour")
        self.action.setCheckable(True)
        # Register the tool
        self.api.register_tool(self)
    
    # Fill all connected voxels of the same colour with a new colour
    def on_activate(self, target):
        # We need to have a selected voxel
        voxel = target.voxels.get(target.x, target.y, target.z)
        if not voxel:
            return
        # Grab the target colour
        search_colour = voxel
        # Initialise our search list
        search = []
        search.append((target.x, target.y, target.z))
        # Keep iterating over the search list until no more to do
        while len(search):
            x,y,z = search.pop()
            voxel = target.voxels.get(x, y, z)
            if not voxel or voxel != search_colour:
                continue
            # Add all likely neighbours into our search list
            if target.voxels.get(x-1,y,z) == search_colour:
                search.append((x-1,y,z))
            if target.voxels.get(x+1,y,z) == search_colour:
                search.append((x+1,y,z))
            if target.voxels.get(x,y+1,z) == search_colour:
                search.append((x,y+1,z))
            if target.voxels.get(x,y-1,z) == search_colour:
                search.append((x,y-1,z))
            if target.voxels.get(x,y,z+1) == search_colour:
                search.append((x,y,z+1))
            if target.voxels.get(x,y,z-1) == search_colour:
                search.append((x,y,z-1))
            # Set the colour of the current voxel
            target.voxels.set(x, y, z, self.colour)

register_plugin(FillTool, "Fill Tool", "1.0")