@echo off
setlocal

rem Always run from the folder this .bat lives in
cd /d "%~dp0"

echo ============================================
echo   Tofu's Paladins Loadout Importer
echo ============================================
echo.

rem --- Step 1: make sure uv is installed ---
where uv >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [1/3] uv is already installed.
) else (
    echo [1/3] uv not found. Installing uv via Git Bash...

    rem Locate a Git Bash executable
    set "BASH_EXE="
    if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles%\Git\bin\bash.exe"
    if not defined BASH_EXE if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles(x86)%\Git\bin\bash.exe"
    if not defined BASH_EXE if exist "%LocalAppData%\Programs\Git\bin\bash.exe" set "BASH_EXE=%LocalAppData%\Programs\Git\bin\bash.exe"

    if not defined BASH_EXE (
        echo.
        echo ERROR: Git Bash was not found. Install Git for Windows from
        echo https://git-scm.com/download/win, or install uv manually from
        echo https://astral.sh/uv
        goto :fail
    )

    "%BASH_EXE%" -lc "curl -LsSf https://astral.sh/uv/install.sh | sh"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install uv. Please install it manually from https://astral.sh/uv
        goto :fail
    )

    rem uv installs to %USERPROFILE%\.local\bin -- add it to PATH for this session
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"

    where uv >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: uv was installed but could not be found on PATH.
        echo Please close and re-run this file, or restart your computer.
        goto :fail
    )
    echo uv installed successfully.
)
echo.

rem --- Step 2: sync dependencies (creates/updates the .venv) ---
echo [2/3] Installing/updating dependencies (uv sync)...
uv sync
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: "uv sync" failed. See the messages above for details.
    goto :fail
)
echo Dependencies are ready.
echo.

rem --- Step 3: launch the app ---
echo [3/3] Launching...
echo.
uv run python main.py
goto :done

:fail
echo.
echo Setup did not complete. See README.md for manual instructions.

:done
echo.
echo Program exited. Press any key to close this window.
pause >nul
endlocal
