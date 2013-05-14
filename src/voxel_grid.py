# voxel_grid.py
# A 3D grid for the voxel widget area.
# Copyright (c) 2013, Graham R King & Bruno F Canella
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

import array
from PySide import QtCore, QtGui
from OpenGL.GL import *
#from OpenGL.GLU import gluUnProject, gluProject

##
# Constants for the planes, to be used with a dictionary.
class GridPlanes(object):
    X = "x"
    Y = "y"
    Z = "z"

##
# Represents a plane to be used in the grid
class GridPlane(object):
    ##
    # @param voxels Reference to the VoxelData
    # @param plane The plane where this grid belongs
    # @param offset The offset of the plane, relative to their negative end ( X = Left, Y = Bottom, Z = Front )
    # @param visible Indicates if the plane is visible or not
    def __init__( self, voxels, plane, offset, visible, color = QtGui.QColor("white")  ):
        self._voxels = voxels
        self._plane = plane
        self._offset = offset
        self._visible = visible
        self._color = color
        self._methods_get_plane_vertices = {
            GridPlanes.X: self._get_grid_vertices_x_plane,
            GridPlanes.Y: self._get_grid_vertices_y_plane,
            GridPlanes.Z: self._get_grid_vertices_z_plane
        }
        self.update_vertices()

    @property
    def plane(self):
        return self._plane
    @plane.setter
    def plane(self, value):
        assert value in ( GridPlanes.X, GridPlanes.Y, GridPlanes.Z )
        if( value != self._plane ):
            self._plane = value
            self.update_vertices()

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, value):
        assert isinstance(value, int)
        if( value != self._offset ):
            self._offset = value
            self.update_vertices()

    @property
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, value):
        assert isinstance(value, bool)
        self._visible = value

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        assert isinstance( value, QtGui.QColor )
        self._color = value

    @property
    def vertices(self):
        return self._vertices

    def update_vertices(self):
        self._vertices = self._methods_get_plane_vertices[self._plane]()
        self._vertices_array = array.array("f", self._vertices).tostring()
        self._num_vertices = len(self._vertices)//3

    def _get_grid_vertices_x_plane(self):
        vertices = []
        height = self._voxels.height
        depth = self._voxels.depth
        for y in xrange(height+1):
            vertices += self._voxels.voxel_to_world( self.offset,      y,     0 )
            vertices += self._voxels.voxel_to_world( self.offset,      y, depth )
        for z in xrange(depth+1):
            vertices += self._voxels.voxel_to_world( self.offset,      0,     z )
            vertices += self._voxels.voxel_to_world( self.offset, height,     z )
        return vertices

    def _get_grid_vertices_y_plane(self):
        vertices = []
        width = self._voxels.width
        depth = self._voxels.depth
        for z in xrange(depth+1):
            vertices += self._voxels.voxel_to_world(     0, self.offset, z )
            vertices += self._voxels.voxel_to_world( width, self.offset, z )
        for x in xrange(width+1):
            vertices += self._voxels.voxel_to_world( x, self.offset, 0     )
            vertices += self._voxels.voxel_to_world( x, self.offset, depth )
        return vertices

    def _get_grid_vertices_z_plane(self):
        vertices = []
        width = self._voxels.width
        height = self._voxels.height
        for x in xrange(width+1):
            vertices += self._voxels.voxel_to_world( x,      0, self.offset )
            vertices += self._voxels.voxel_to_world( x, height, self.offset )
        for y in xrange(height+1):
            vertices += self._voxels.voxel_to_world(     0, y, self.offset )
            vertices += self._voxels.voxel_to_world( width, y, self.offset )
        return vertices

class VoxelGrid(object):

    def __init__(self, widget ):
        self._voxels = widget
        self._planes = {}

    def add_grid_plane(self, plane, offset, visible, color = QtGui.QColor("white") ):
        key = (plane, offset)
        if( key in self._planes.keys() ):
            self._planes[key].visible = visible
        else:
            grid_plane = GridPlane( self._voxels, plane, offset, visible, color )
            self._planes[key] = grid_plane

    def remove_grid_plane(self, plane, offset):
        key = (plane, offset)
        if( key in self._planes.keys() ):
            del self._planes[key]

    # Return vertices for a floor grid
    def get_grid_plane(self, plane, offset):
        key = ( plane, offset )
        if( key in self._planes.keys() ):
            return self._planes[key]
        else:
            return None

    def update_grid_plane(self):
        for plane in self._planes.itervalues():
            plane.update_vertices()

    # Render the grids
    def paint(self):
        # Disable lighting
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)

        for plane in self._planes.itervalues():
            if( not plane.visible ):
                continue

            red = plane.color.redF()
            green = plane.color.greenF()
            blue = plane.color.blueF()
            # Grid colour
            glColor3f(red,green,blue)

            # Enable vertex buffers
            glEnableClientState(GL_VERTEX_ARRAY)

            # Describe our buffers
            glVertexPointer(3, GL_FLOAT, 0, plane._vertices_array)

            # Render the buffers
            glDrawArrays(GL_LINES, 0, plane._num_vertices)

            # Disable vertex buffers
            glDisableClientState(GL_VERTEX_ARRAY)

        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
