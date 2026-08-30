#!/usr/bin/env python3
"""
Jarvis V2 - Installer Image Generator
======================================
Generates BMP images for Inno Setup installer wizard.

Creates:
- app.bmp (164x314) - Left side wizard image
- app_small.bmp (55x55) - Small wizard image

Usage:
    python packaging/create_installer_images.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow is required. Install with: pip install pillow")
    sys.exit(1)

HERE = Path(__file__).resolve().parent


def create_wizard_image(output_path: Path, width: int = 164, height: int = 314):
    """Create the main wizard sidebar image."""
    # Create gradient background (dark to orange)
    img = Image.new('RGB', (width, height), color='#050505')
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for y in range(height):
        # Dark at top, orange at bottom
        r = int(5 + (255 - 5) * (y / height) * 0.3)
        g = int(5 + (140 - 5) * (y / height) * 0.2)
        b = int(5 + (26 - 5) * (y / height) * 0.1)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw decorative circles (solar core style)
    center_x = width // 2
    center_y = height // 3

    # Outer glow
    for radius in range(60, 20, -5):
        alpha = int(255 * (1 - radius / 60))
        color = (255, 140, 26, alpha)
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            outline=(255, 140, 26, 100),
            width=1
        )

    # Inner core
    draw.ellipse(
        [center_x - 20, center_y - 20,
         center_x + 20, center_y + 20],
        fill=(255, 140, 26)
    )

    # Draw text
    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # App name
    text = "JARVIS"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, center_y + 70),
        text,
        fill=(255, 140, 26),
        font=font_large
    )

    # Version
    text = "V2"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, center_y + 100),
        text,
        fill=(255, 200, 100),
        font=font_large
    )

    # Tagline
    text = "AI Assistant"
    bbox = draw.textbbox((0, 0), text, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, center_y + 140),
        text,
        fill=(200, 200, 200),
        font=font_small
    )

    # Save as BMP
    img.save(output_path, 'BMP')
    print(f"[OK] Created: {output_path} ({width}x{height})")


def create_small_image(output_path: Path, size: int = 55):
    """Create the small wizard image."""
    img = Image.new('RGB', (size, size), color='#050505')
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for y in range(size):
        r = int(5 + (255 - 5) * (y / size) * 0.3)
        g = int(5 + (140 - 5) * (y / size) * 0.2)
        b = int(5 + (26 - 5) * (y / size) * 0.1)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Draw core
    center = size // 2
    draw.ellipse(
        [center - 15, center - 15, center + 15, center + 15],
        fill=(255, 140, 26)
    )

    # Draw outer ring
    draw.ellipse(
        [center - 20, center - 20, center + 20, center + 20],
        outline=(255, 140, 26, 150),
        width=2
    )

    # Save as BMP
    img.save(output_path, 'BMP')
    print(f"[OK] Created: {output_path} ({size}x{size})")


def main():
    """Main function."""
    print("\n" + "=" * 50)
    print("  Jarvis V2 - Installer Image Generator")
    print("=" * 50 + "\n")

    # Create main wizard image
    wizard_bmp = HERE / "app.bmp"
    create_wizard_image(wizard_bmp)

    # Create small wizard image
    small_bmp = HERE / "app_small.bmp"
    create_small_image(small_bmp)

    print("\n" + "=" * 50)
    print("  Done! Images created for installer.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
