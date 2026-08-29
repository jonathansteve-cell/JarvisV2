"""Generate app.ico (multi-size) from packaging/app.png using Pillow.

Pillow is already in requirements.txt, so this runs on the build machine
without extra installs. The .ico is embedded into the JarvisV2.exe by
PyInstaller and used by the Inno Setup installer.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "app.png"
OUT = HERE / "app.ico"


def main() -> int:
    if not SRC.exists():
        print(f"[ERROR] missing source icon: {SRC}")
        return 1
    img = Image.open(SRC).convert("RGBA")
    # Windows icon sizes: 16, 24, 32, 48, 64, 128, 256
    img.save(OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[OK] wrote {OUT} ({img.width}x{img.height} source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())