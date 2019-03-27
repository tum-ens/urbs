@echo off
cls

echo Clean folders
RD /s /q build
RD /s /q dist
RD /s /q Output
echo Collect libs
pyinstaller --clean urbs_gui.spec 
::--log-level ERROR
echo Copy images
mkdir dist\urbs_gui\imgs
XCOPY ..\gui\imgs\*.png /S /Y dist\urbs_gui\imgs
echo Copy help
mkdir dist\urbs_gui\help
XCOPY ..\gui\help\*.* /S /Y dist\urbs_gui\help
echo Copy samples
mkdir dist\urbs_gui\samples
XCOPY ..\*.json /Y dist\urbs_gui\samples
echo Copy solvers
XCOPY solvers\glpk\*.* /S /Y dist\urbs_gui
echo Copy extra dlls
mkdir dist\urbs_gui\platforms
XCOPY %APPDATA%\..\Local\Continuum\Anaconda3\Library\plugins\platforms\*.dll /S /Y dist\urbs_gui\platforms
echo Make installer...
cd InnoSetup5
ISCC.exe "../setup_script.iss"
cd..