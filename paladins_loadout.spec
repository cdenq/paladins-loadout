# PyInstaller build spec -- produces a single-file windowed PaladinsLoadout.exe.
# Build via build.bat (which also generates the .ico), or directly with:
#   uv run pyinstaller paladins_loadout.spec
import os

# tofu.ico is generated from assets/tofu.png by build.bat; fall back to no icon.
_icon = "assets/tofu.ico" if os.path.exists("assets/tofu.ico") else None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    # Read-only assets baked into the bundle. config.yml is included as a seed:
    # on first launch the app copies it out next to the .exe as an editable copy
    # (see src/config.py), so the bundled one is only the default template.
    datas=[
        ("assets", "assets"),
        ("config.yml", "."),
    ],
    hiddenimports=["win32gui", "win32process", "win32api", "win32con"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["jupyter", "ipykernel", "IPython", "notebook"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PaladinsLoadout",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,          # windowed app -- no console window pops up
    disable_windowed_traceback=False,
    icon=_icon,
)
