# palette_widget.py
# A colour picking widget.
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
from PySide import QtCore, QtGui
from PySide.QtCore import QRect, QPoint

class PaletteWidget(QtGui.QWidget):

    # Colour changed signal
    changed = QtCore.Signal()

    @property
    def colour(self):
        return QtGui.QColor.fromHsvF(self._hue, self._saturation, self._value)
    @colour.setter
    def colour(self, value):
        # If this is an integer, assume is RGBA
        if type(value) is int:
            r = (value & 0xff000000) >> 24
            g = (value & 0xff0000) >> 16
            b = (value & 0xff00) >> 8
            value = QtGui.QColor.fromRgb(r,g,b)
        self._set_colour(value)

    def __init__(self, parent = None):
        super(PaletteWidget, self).__init__(parent)
        self._hue = 1.0
        self._saturation = 1.0
        self._value = 1.0
        self._hue_width = 24
        self._gap = 8
        self._colour = QtGui.QColor.fromHslF(self._hue, 1.0, 1.0)
        self._calculate_bounds()
        self._draw_palette()

    # Calculate the sizes of various bits of our UI
    def _calculate_bounds(self):
        width = self.width()
        height = self.height()
        # Hue palette
        self._hue_rect = QRect(
            width-self._hue_width, 0, self._hue_width, height)
        # Shades palette
        self._shades_rect = QRect(
            0, 0, width-(self._hue_width+self._gap), height)

    # Render our palette to an image
    def _draw_palette(self):

        # Create an image with a white background
        self._image = QtGui.QImage(QtCore.QSize(self.width(), self.height()),
            QtGui.QImage.Format.Format_RGB32)
        self._image.fill(QtGui.QColor.fromRgb(0xff, 0xff, 0xff))

        # Draw on our image with no pen
        qp = QtGui.QPainter()
        qp.begin(self._image)
        qp.setPen(QtCore.Qt.NoPen)

        # Render hues
        rect = self._hue_rect
        for x in xrange(rect.x(), rect.x()+rect.width()):
            for y in xrange(rect.y(), rect.y()+rect.height(), 8):
                h = float(y)/rect.height()
                s = 1.0
                v = 1.0
                c = QtGui.QColor.fromHsvF(h, s, v)
                qp.setBrush(c)
                qp.drawRect(x, y, 8, 8)

        # Render hue selection marker
        qp.setBrush(QtGui.QColor.fromRgb(0xff, 0xff, 0xff))
        qp.drawRect(rect.x(), self._hue * rect.height(),
            rect.width(), 2)

        # Render shades
        rect = self._shades_rect
        width = float(rect.width())
        steps = int(round(width / 8.0))
        step_size = width / steps
        x = rect.x()
        while x < rect.width()+rect.x():
            w = int(round(step_size))
            for y in xrange(rect.y(), rect.y()+rect.height(), 8):
                h = self._hue
                s = 1-float(y)/rect.height()
                v = float(x)/rect.width()
                c = QtGui.QColor.fromHsvF(h, s, v)
                qp.setBrush(c)
                qp.drawRect(x, y, w, 8)
            x += w
            width -= w
            steps -= 1
            if steps > 0:
                step_size = width / steps

        # Render colour selection marker
        qp.setBrush(QtGui.QColor.fromRgb(0xff, 0xff, 0xff))
        qp.drawRect(rect.x(), (1-self._saturation)*rect.height(), rect.width(), 1)
        qp.drawRect(self._value*rect.width(), rect.y(), 1, rect.height())

        qp.end()

    def paintEvent(self, event):
        # Render our palette image to the screen
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(QPoint(0,0), self._image)
        qp.end()

    def mousePressEvent(self, event):
        mouse = QPoint(event.pos())
        if event.buttons() & QtCore.Qt.LeftButton:
            # Click on hues?
            if self._hue_rect.contains(mouse.x(), mouse.y()):
                y = mouse.y()
                c = QtGui.QColor.fromHsvF(
                    float(y)/self.height(), self._saturation, self._value)
                self.colour = c
            # Click on colours?
            elif self._shades_rect.contains(mouse.x(), mouse.y()):
                # calculate saturation and value
                x = mouse.x()
                y = mouse.y()
                c = QtGui.QColor.fromHsvF(
                    self._hue, 1-float(y)/self._shades_rect.height(),
                    float(x)/self._shades_rect.width())
                self.colour = c

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.mousePressEvent(event)

    def resizeEvent(self, event):
        self._calculate_bounds()
        self._draw_palette()

    # Set the current colour
    def _set_colour(self, c):
        h, s, v, _ = c.getHsvF()
        self._hue = h
        self._saturation = s
        self._value = v
        self._draw_palette()
        self.repaint()
        self.changed.emit()
