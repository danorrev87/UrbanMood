#!/usr/bin/env python3
"""
Create properly sized favicon from icon.png
"""
from PIL import Image
import os

def create_favicon_sizes():
    # Open the original icon
    original = Image.open('static/icon.png')
    
    # Convert to RGBA if not already
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Create a square canvas (use the larger dimension)
    max_size = max(original.size)
    square_image = Image.new('RGBA', (max_size, max_size), (0, 0, 0, 0))
    
    # Center the original image on the square canvas
    offset_x = (max_size - original.size[0]) // 2
    offset_y = (max_size - original.size[1]) // 2
    square_image.paste(original, (offset_x, offset_y))
    
    # Create different sizes
    sizes = [16, 32, 48, 64, 96, 128, 180, 192, 256, 512]
    
    for size in sizes:
        resized = square_image.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save to both static and static-site directories
        resized.save(f'static/favicon-{size}x{size}.png')
        resized.save(f'static-site/favicon-{size}x{size}.png')
    
    # Create a 64x64 as the main favicon.ico (larger for better visibility)
    favicon_64 = square_image.resize((64, 64), Image.Resampling.LANCZOS)
    favicon_64.save('static/favicon.ico')
    favicon_64.save('static-site/favicon.ico')
    
    # Create apple-touch-icon (180x180)
    apple_icon = square_image.resize((180, 180), Image.Resampling.LANCZOS)
    apple_icon.save('static/apple-touch-icon.png')
    apple_icon.save('static-site/apple-touch-icon.png')
    
    print("✅ Favicon sizes created successfully!")
    print("Created sizes:", sizes)
    print("Created favicon.ico and apple-touch-icon.png")

if __name__ == "__main__":
    create_favicon_sizes()
