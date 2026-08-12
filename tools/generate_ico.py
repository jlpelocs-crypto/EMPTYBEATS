#!/usr/bin/env python3
"""Generate gaming-hub-icon.ico from gaming-hub-icon.svg using cairosvg + Pillow.

Usage:
  python3 tools/generate_ico.py

This will create `gaming-hub-icon.ico` next to the SVG file.
"""
import os
import sys

SVG = os.path.join(os.path.dirname(__file__), os.pardir, "gaming-hub-icon.svg")
ICO = os.path.join(os.path.dirname(__file__), os.pardir, "gaming-hub-icon.ico")

try:
    import cairosvg
    from PIL import Image
except Exception as e:
    print("Missing dependency:", e)
    print("Install requirements: pip install Pillow cairosvg")
    sys.exit(1)

if not os.path.exists(SVG):
    print("SVG icon not found at:", SVG)
    sys.exit(1)

# Render SVG to PNG bytes at multiple sizes and save as ICO
sizes = [256, 128, 64, 48, 32, 16]
images = []
for s in sizes:
    png_bytes = cairosvg.svg2png(url=SVG, output_width=s, output_height=s)
    from io import BytesIO
    img = Image.open(BytesIO(png_bytes)).convert("RGBA")
    images.append(img)

# Save first image as ICO and include others as sizes
try:
    images[0].save(ICO, format="ICO", sizes=[(s, s) for s in sizes])
    print("Created ICO:", ICO)
except Exception as e:
    print("Failed to write ICO:", e)
    sys.exit(1)
