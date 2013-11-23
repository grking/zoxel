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
from PySide import QtGui
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
        self._offset = 0
        self._visible = visible
        self._color = color
        self._offset_plane_limit = {
            GridPlanes.X: lambda: self._voxels.width,
            GridPlanes.Y: lambda: self._voxels.height,
            GridPlanes.Z: lambda: self._voxels.depth,
        }
        self._methods_get_plane_vertices = {
            GridPlanes.X: self._get_grid_vertices_x_plane,
            GridPlanes.Y: self._get_grid_vertices_y_plane,
            GridPlanes.Z: self._get_grid_vertices_z_plane
        }
        self.offset = offset
        self.update_vertices()

    @property
    def voxels(self):
        return self._voxels
    @voxels.setter
    def voxels(self, voxels):
        self._voxels = voxels

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
        offset_limit = self._offset_plane_limit[self.plane]()
        if( value > offset_limit ):
            value = offset_limit
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

    def update_grid_plane(self, voxels):
        for plane in self._planes.itervalues():
            plane.voxels = voxels
            if plane.plane == GridPlanes.Z:
                plane.offset = voxels.depth
            plane.update_vertices()

    # Render the grids
    def paint(self):
        # Disable lighting
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)

        for grid in self._planes.itervalues():
            if( not grid.visible ):
                continue

            red = grid.color.redF()
            green = grid.color.greenF()
            blue = grid.color.blueF()
            # Grid colour
            glColor3f(red,green,blue)

            # Enable vertex buffers
            glEnableClientState(GL_VERTEX_ARRAY)

            # Describe our buffers
            glVertexPointer(3, GL_FLOAT, 0, grid._vertices_array)

            # Render the buffers
            glDrawArrays(GL_LINES, 0, grid._num_vertices)

            # Disable vertex buffers
            glDisableClientState(GL_VERTEX_ARRAY)

        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)

    def scale_offsets(self, width_scale = None, height_scale = None, depth_scale = None ):
        for grid in self._planes.itervalues():
            if( grid.plane == GridPlanes.X and width_scale ):
                grid.offset = int(round(grid.offset * width_scale))
            elif( grid.plane == GridPlanes.Y and height_scale ):
                grid.offset = int(round(grid.offset * height_scale))
            elif( grid.plane == GridPlanes.Z and depth_scale ):
                grid.offset = int(round(grid.offset * depth_scale))
