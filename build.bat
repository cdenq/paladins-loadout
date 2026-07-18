@echo off
setlocal
cd /d "%~dp0"

rem uv installs here; make sure it's on PATH even on a plain double-click.
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

echo ============================================
echo   Building PaladinsLoadout.exe
echo ============================================
echo.

where uv >nul 2>&1
if errorlevel 1 goto :no_uv

echo [1/4] Syncing dependencies...
uv sync
if errorlevel 1 goto :fail

echo.
echo [2/4] Ensuring PyInstaller is available...
uv pip install pyinstaller
if errorlevel 1 goto :fail

echo.
echo [3/4] Generating window icon from assets\tofu.png...
uvx --from pillow python make_icon.py
if errorlevel 1 echo WARNING: icon generation failed; building without a custom icon.

echo.
echo Checking the build environment can bundle Tk...
uv run python -c "import tkinter"
if errorlevel 1 goto :bad_tk

echo.
echo [4/4] Building one-file executable...
uv run pyinstaller --noconfirm --clean paladins_loadout.spec
if errorlevel 1 goto :fail

echo.
echo ============================================
echo   Done: dist\PaladinsLoadout.exe
echo ============================================
echo Ship that single file. On first launch it writes a config.yml next to
echo itself that the user can edit.
goto :done

:no_uv
echo ERROR: uv not found. Install it first (running run.bat once will do it).
goto :fail

:bad_tk
echo.
echo ERROR: this environment's Python can't load tkinter, so the built .exe
echo would crash on launch. This usually means .venv was created from an
echo Anaconda Python. Fix with:
echo     rmdir /s /q .venv
echo     uv venv
echo     uv sync
goto :fail

:fail
echo.
echo Build FAILED. See the messages above.

:done
echo.
echo Press any key to close this window.
pause >nul
endlocal
