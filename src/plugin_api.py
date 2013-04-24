# plugin_api.py
# API for system plugins.
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

class PluginManager(object):
    plugins = []

class PluginAPI(object):
    
    def __init__(self):
        # All plugins get a reference to our application
        self.application = QtGui.QApplication.instance()
        # And our main window
        self.mainwindow = self.application.mainwindow

    # Register a drawing tool with the system
    def register_tool(self, tool):
        # Create an instance
        self.mainwindow.register_tool(tool)
        
    # Register an importer/exporter with the system
    def register_file_handler(self, handler):
        self.mainwindow.register_file_handler(handler)

    # Get the currently selected colour from the palette
    def get_palette_colour(self):
        return self.mainwindow.display.voxel_colour

    # Returns the current voxel data
    def get_voxel_data(self):
        return self.mainwindow.display.voxels

    # Get and set persistent config values. value can be any serialisable type.
    # name should be a hashable type, like a simple string.
    def set_config(self, name, value):
        self.api.mainwindow.set_setting(name, value)
    def get_config(self, name):
        return self.api.mainwindow.get_setting(name)

    # Changee the GUI palette to the given colour.
    # Accepts QColors and 32bit integer RGBA
    def set_palette(self, colour):
        self.mainwindow.colour_palette.colour = colour        

# Plugin registration
# Plugins call this function to register with the system.  A plugin
# should pass the class which will be instaniated by the application, 
# this constructor is passed an instance of the system plugin API.
def register_plugin(plugin_class, name, version):
    # Create an instance of the API to send to the plugin
    # Plugins access the main app via this API instance
    api = PluginAPI()
    plugin = plugin_class(api)
    PluginManager.plugins.append(plugin)
    return api
