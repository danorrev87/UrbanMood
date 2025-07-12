#!/usr/bin/env python3
"""
Create an extra large favicon for maximum visibility
"""
from PIL import Image, ImageDraw
import os

def create_extra_large_favicon():
    # Open the original icon
    original = Image.open('static/icon.png')
    
    # Convert to RGBA if not already
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Create a square canvas that fills most of the space (no padding)
    # Use the larger dimension and make it square
    size = max(original.size)
    square_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Scale the original to fill the square as much as possible
    if original.size[0] > original.size[1]:
        # Wider than tall - fit width
        new_width = size
        new_height = int(size * original.size[1] / original.size[0])
        offset_x = 0
        offset_y = (size - new_height) // 2
    else:
        # Taller than wide - fit height  
        new_height = size
        new_width = int(size * original.size[0] / original.size[1])
        offset_x = (size - new_width) // 2
        offset_y = 0
    
    resized_original = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
    square_image.paste(resized_original, (offset_x, offset_y))
    
    # Create extra large favicons
    favicon_96 = square_image.resize((96, 96), Image.Resampling.LANCZOS)
    favicon_96.save('static/urbanmood-favicon.ico')
    favicon_96.save('static-site/urbanmood-favicon.ico')
    
    # Also create 128x128
    favicon_128 = square_image.resize((128, 128), Image.Resampling.LANCZOS)
    favicon_128.save('static/urbanmood-favicon-128.png')
    favicon_128.save('static-site/urbanmood-favicon-128.png')
    
    print("✅ Extra large favicon created as urbanmood-favicon.ico (96x96)!")
    print("✅ Also created urbanmood-favicon-128.png (128x128)!")

if __name__ == "__main__":
    create_extra_large_favicon()
