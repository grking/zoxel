# mainwindow.py
# Zoxel - A Voxel Editor
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

import sys
from PySide import QtGui
from mainwindow import MainWindow

def main():
    # create application
    app = QtGui.QApplication(sys.argv)

    # create mainWindow
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    
    # Remember our main window
    app.mainwindow = mainWindow
    
    # run main loop
    sys.exit(app.exec_())

# call main function
if __name__ == '__main__':
    main()
