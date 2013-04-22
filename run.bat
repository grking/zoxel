@echo off
c:\Python27\lib\site-packages\PySide\pyside-rcc.exe src\resources.qrc -o src\resources_rc.py
call :iter
cd src
python zoxel.py
cd ..
goto :eof

:iter
for %%f in (*.ui) do pyside-uic %%~dpnxf -o %%~dpf\ui_%%~nf.py
  for /D %%d in (*) do (
    cd %%d
    call :iter
    cd ..
  )
exit /b
