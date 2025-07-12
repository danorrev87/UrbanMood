#!/usr/bin/env python3
"""
Create a larger-appearing favicon with less padding
"""
from PIL import Image
import os

def create_larger_favicon():
    # Open the original icon
    original = Image.open('static/icon.png')
    
    # Convert to RGBA if not already
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Create a square canvas with minimal padding (just 10% on each side)
    padding_ratio = 0.05  # 5% padding instead of centering
    max_size = max(original.size)
    canvas_size = int(max_size * (1 + padding_ratio * 2))
    
    square_image = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    
    # Position the original image with minimal padding
    offset_x = int(padding_ratio * max_size)
    offset_y = int(padding_ratio * max_size)
    
    # Resize original to fit with padding
    target_size = (canvas_size - offset_x * 2, int((canvas_size - offset_x * 2) * original.size[1] / original.size[0]))
    if target_size[1] > canvas_size - offset_y * 2:
        target_size = (int((canvas_size - offset_y * 2) * original.size[0] / original.size[1]), canvas_size - offset_y * 2)
        offset_x = (canvas_size - target_size[0]) // 2
    
    resized_original = original.resize(target_size, Image.Resampling.LANCZOS)
    square_image.paste(resized_original, (offset_x, offset_y))
    
    # Create a prominent 64x64 favicon
    favicon_64 = square_image.resize((64, 64), Image.Resampling.LANCZOS)
    favicon_64.save('static/favicon-large.ico')
    favicon_64.save('static-site/favicon-large.ico')
    
    # Also create 96x96 version
    favicon_96 = square_image.resize((96, 96), Image.Resampling.LANCZOS)
    favicon_96.save('static/favicon-96x96-large.png')
    favicon_96.save('static-site/favicon-96x96-large.png')
    
    print("✅ Larger favicon created as favicon-large.ico!")

if __name__ == "__main__":
    create_larger_favicon()
