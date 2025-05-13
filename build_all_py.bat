@echo off
setlocal enabledelayedexpansion

set UPXPATH=G:\python-路径插件\upx-5.0.1-win64\upx.exe

echo Scanning all .py files in current folder...

for %%F in (*.py) do (
    set PYFILE=%%F
    set EXENAME=%%~nF

    echo ---------------------------------------------
    echo Building !PYFILE!...

    pyinstaller "!PYFILE!" ^
     --onefile ^
     --clean ^
     --strip ^
     --noconfirm ^
     --name "!EXENAME!" ^
     --exclude-module=tkinter ^
     --exclude-module=unittest ^
     --hidden-import=fitz ^
     --hidden-import=PIL.ImageFilter ^
     --upx-dir "%UPXPATH%"

    echo Finished: dist\!EXENAME!.exe
    echo.
)

echo All done.
pause
