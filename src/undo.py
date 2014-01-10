# undo.py
# An undo buffer.
# Copyright (c) 2014, Graham R King & Bruno F Canella
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

class UndoItem(object):
    
    @property
    def operation(self):
        return self._operation
    
    @property
    def olddata(self):
        return self._olddata
    
    @property
    def newdata(self):
        return self._newdata

    def __init__(self, operation, olddata, newdata):
        self._operation = operation
        self._olddata = olddata
        self._newdata = newdata

class Undo(object):
    
    # Types of operation
    SET_VOXEL = 1
    TRANSLATE = 2
    
    @property 
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property 
    def frame(self):
        return self._frame
    @frame.setter
    def frame(self, value):
        self._frame = value
    
    def __init__(self):
        self._enabled = True
        self.clear()
    
    def add_frame(self, pos):
        self._buffer.insert(pos, [])
        self._ptr.insert(pos, -1) 

    def delete_frame(self, pos):
        del self._buffer[pos]
        del self._ptr[pos] 

    def add(self, item):
        if not self._enabled:
            return
        # Clear future if we're somewhere in the middle of the undo history
        if self._ptr[self._frame] < len(self._buffer[self._frame])-1:
            self._buffer = self._buffer[self._frame][:self._ptr[self._frame]+1]
        self._buffer[self._frame].append(item)
        self._ptr[self._frame] = len(self._buffer[self._frame])-1
    
    def _valid_buffer(self):
        return len(self._buffer[self._frame]) > 0
      
    def undo(self):
        if not self._valid_buffer():
            return
        item = self._buffer[self._frame][self._ptr[self._frame]]
        self._ptr[self._frame] -= 1
        if self._ptr[self._frame] < -1:
            self._ptr[self._frame] = -1
        return item

    def redo(self):
        if not self._valid_buffer():
            return
        self._ptr[self._frame] += 1
        item = None
        if self._ptr[self._frame] > len(self._buffer[self._frame])-1:
            self._ptr[self._frame] = len(self._buffer[self._frame])-1
        else:
            item = self._buffer[self._frame][self._ptr[self._frame]]
        return item

    def clear(self):
        self._buffer = [[]]
        self._ptr = [-1]
        self._frame = 0
