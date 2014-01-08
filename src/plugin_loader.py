# Load these plugins
# This could (should) be replaced by dynamic module loading, but we do it
# this way to support cx-freeze on Windows.
import plugins.tool_draw
import plugins.tool_paint
import plugins.tool_erase
import plugins.tool_drag
import plugins.io_zoxel
import plugins.io_sproxel
import plugins.tool_fill
import plugins.tool_colourpick
import plugins.io_obj
import plugins.io_qubicle
