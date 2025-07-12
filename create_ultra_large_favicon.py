#!/usr/bin/env python3
"""
Create an SVG favicon that will appear larger
"""
from PIL import Image
import os

def create_large_svg_favicon():
    # Open the original icon
    original = Image.open('static/icon.png')
    
    # Convert to RGBA if not already
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Create a much larger favicon (128x128) with minimal padding
    large_favicon = original.resize((128, 128), Image.Resampling.LANCZOS)
    large_favicon.save('static/urbanmood-large-favicon.ico')
    large_favicon.save('static-site/urbanmood-large-favicon.ico')
    
    # Also create PNG versions
    large_favicon.save('static/urbanmood-large-favicon.png')
    large_favicon.save('static-site/urbanmood-large-favicon.png')
    
    print("✅ Large 128x128 favicon created!")

if __name__ == "__main__":
    create_large_svg_favicon()
