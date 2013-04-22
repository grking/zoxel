# mainwindow.py
# The Zoxel main window.
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

from PySide import QtCore
from PySide import QtGui
from dialog_about import AboutDialog
from ui_mainwindow import Ui_MainWindow
from voxel_widget import GLWidget
import json
    
class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        # Initialise the UI
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Our global state
        self.settings = QtCore.QSettings("Zoxel", "Zoxel")
        self.state = {}
        # Load our state if possible
        self.load_state()
        # Restore UI
        self.ui.splitter.restoreState(self.settings.value('gui/splitter'))
        # Create our GL Widget
        try:
            widget = GLWidget(self.ui.glparent)
            self.ui.glparent.layout().addWidget(widget)
            self.display = widget
        except Exception as E:
            QtGui.QMessageBox.warning(self, "Initialisation Failed",
                str(E))
            exit(1)
        # More UI state
        value = self.get_setting("display_floor_grid")
        if value is not None:
            self.ui.action_floor_grid.setChecked(value)
            self.display.floor_grid = value
        
    @QtCore.Slot()
    def on_action_about_triggered(self):
        dialog = AboutDialog(self)
        if dialog.exec_():
            pass

    @QtCore.Slot()
    def on_action_floor_grid_triggered(self):
        self.display.floor_grid = self.ui.action_floor_grid.isChecked()
        self.set_setting("display_floor_grid", self.display.floor_grid)
    
    @QtCore.Slot()
    def on_action_wireframe_triggered(self):
        self.display.wireframe = self.ui.action_wireframe.isChecked()
        self.set_setting("display_wireframe", self.display.wireframe)

    @QtCore.Slot()
    def on_action_save_triggered(self):
        # Bail if current focus doesn't support saving
        if not self.window_supports_save():
            return
        # Send a save request
        self.window_supports_save(True)

    # Return a section of our internal config
    def get_setting(self, name):
        if name in self.state:
            return self.state[name]
        return None
        
    # Set some config.  Value should be a serialisable type
    def set_setting(self, name, value):
        self.state[name] = value
   
    def closeEvent(self, event):
        # Save splitter state
        self.save_state()
        event.accept()
            
    # Save our state
    def save_state(self):
        try:
            state = json.dumps(self.state)
            self.settings.setValue("system/state", state)
            # Save UI
            self.settings.setValue("gui/splitter", self.ui.splitter.saveState())            
        except Exception as E:
            # XXX Fail. Never displays because we're on our way out
            error = QtGui.QErrorMessage(self)
            error.showMessage(str(E))
            print str(E)
    
    # Load our state
    def load_state(self):
        try:
            state = self.settings.value("system/state")
            if state:
                self.state = json.loads(state)
        except Exception as E:
            error = QtGui.QErrorMessage(self)
            error.showMessage(str(E))


