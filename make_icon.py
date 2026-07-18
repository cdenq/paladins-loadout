"""Generate assets/tofu.ico from assets/tofu.png (run by build.bat).

Kept as a script rather than an inline `python -c` one-liner because the
comma/paren-heavy sizes list breaks cmd.exe's parser inside a .bat file.
"""

from PIL import Image

SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

Image.open("assets/tofu.png").save("assets/tofu.ico", sizes=SIZES)
print("Wrote assets/tofu.ico")
