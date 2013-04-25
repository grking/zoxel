# about_resize.py
# Prompt for resize model dimensions.
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
from ui_dialog_resize import Ui_ResizeDialog

class ResizeDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        # Initialise the UI
        super(ResizeDialog, self).__init__(parent)
        self.ui = Ui_ResizeDialog()
        self.ui.setupUi(self)
        self.ui.button_auto.clicked.connect(self.on_button_auto_clicked)

    def on_button_auto_clicked(self):
        _,_,_,x,y,z = self.parent().display.voxels.get_bounding_box()
        self.ui.width.setValue(x)
        self.ui.height.setValue(y)
        self.ui.depth.setValue(z)
