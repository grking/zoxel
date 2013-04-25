cd src

cxfreeze zoxel.py --target-dir ..\dist --base-name Win32GUI --include-modules atexit,PySide.QtNetwork,PySide.QtWebKit,OpenGL,OpenGL.platform.win32,OpenGL.arrays.nones,OpenGL.arrays.lists,OpenGL.arrays.strings,OpenGL.arrays.numbers,OpenGL.arrays.ctypesarrays,OpenGL.arrays.ctypesparameters,OpenGL.arrays.ctypespointers --include-path .
