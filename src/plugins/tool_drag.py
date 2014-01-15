# tool_drag.py
# Model moving tool.
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

class DragTool(Tool):

    def __init__(self, api):
        super(DragTool, self).__init__(api)
        # Create our action / icon
        self.action = QtGui.QAction(
            QtGui.QPixmap(":/images/gfx/icons/arrow-in-out.png"),
            "Move Model", None)
        self.action.setStatusTip("Move Model")
        self.action.setCheckable(True)
        # Register the tool
        self.api.register_tool(self)

    # Colour the targeted voxel
    def on_drag_start(self, target):
        self._mouse = (target.mouse_x, target.mouse_y)

    # Drag the model in voxel space
    def on_drag(self, target):
            dx = target.mouse_x - self._mouse[0]
            dy = target.mouse_y - self._mouse[1]
            # Work out some sort of vague translation between screen and voxels
            sx = self.api.mainwindow.width() / target.voxels.width
            sy = self.api.mainwindow.height() / target.voxels.height
            dx = int(round(dx / float(sx)))
            dy = int(round(dy / float(sy)))
            # Work out translation for x,y
            ax, ay = self.api.mainwindow.display.view_axis()
            tx = 0
            ty = 0
            tz = 0
            if ax == self.api.mainwindow.display.X_AXIS:
                if dx > 0:
                    tx = 1
                elif dx < 0:
                    tx = -1
            if ax == self.api.mainwindow.display.Y_AXIS:
                if dx > 0:
                    ty = 1
                elif dx < 0:
                    ty = -1
            if ax == self.api.mainwindow.display.Z_AXIS:
                if dx > 0:
                    tz = 1
                elif dx < 0:
                    tz = -1
            if ay == self.api.mainwindow.display.X_AXIS:
                if dy > 0:
                    tx = 1
                elif dy < 0:
                    tx = -1
            if ay == self.api.mainwindow.display.Y_AXIS:
                if dy > 0:
                    ty = -1
                elif dy < 0:
                    ty = 1
            if ay == self.api.mainwindow.display.Z_AXIS:
                if dy > 0:
                    tz = 1
                elif dy < 0:
                    tz = -1
            
            if ty != 0 or tx != 0 or tz != 0:
                self._mouse = (target.mouse_x, target.mouse_y)
            
            target.voxels.translate(tx, ty, tz)
            
register_plugin(DragTool, "Drag Tool", "1.0")