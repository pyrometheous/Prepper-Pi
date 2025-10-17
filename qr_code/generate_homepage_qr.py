#!/usr/bin/env python3
"""
Generate SVG QR code for Prepper-Pi homepage with professional styling
URL: http://10.20.30.1:3000
"""

import os
import qrcode

# Configuration
HOMEPAGE_URL = "http://10.20.30.1:3000"
OUTPUT_DIR = "."  # Output to current directory (qr_code)
SVG_FILE = "homepage.svg"

def generate_svg_qr():
    """Generate SVG QR code with text labels"""
    
    print("Generating SVG QR code with labels...")
    
    # Generate QR code matrix
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=16,  # 60% larger to fill white space much better
        border=2,     # Minimal border to maximize QR space
    )
    qr.add_data(HOMEPAGE_URL)
    qr.make(fit=True)
    
    # Get the QR code matrix
    matrix = qr.get_matrix()
    module_count = len(matrix)
    box_size = 16  # 60% larger
    border = 2     # Minimal border
    
    qr_width = (module_count + border * 2) * box_size
    qr_height = qr_width
    
    # Calculate final dimensions with padding and text
    padding = 40
    text_space = 180
    final_width = qr_width + (padding * 2)
    final_height = qr_height + text_space + (padding * 2)
    
    # Create SVG
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {final_width} {final_height}" width="{final_width}" height="{final_height}">')
    lines.append(f'  <rect width="{final_width}" height="{final_height}" fill="#000000" rx="50" ry="50"/>')
    lines.append(f'  <rect x="{padding}" y="{padding}" width="{qr_width}" height="{qr_height}" fill="#ffffff"/>')
    lines.append(f'  <g transform="translate({padding + border * box_size}, {padding + border * box_size})">')
    
    # Draw QR code modules
    for row in range(module_count):
        for col in range(module_count):
            if matrix[row][col]:
                x = col * box_size
                y = row * box_size
                lines.append(f'    <rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="#000000"/>')
    
    # Add text
    text_y_start = qr_width + padding + 70
    lines.append('  </g>')
    lines.append(f'  <text x="{final_width/2}" y="{text_y_start}" font-family="Arial, Helvetica, sans-serif" font-size="70" font-weight="bold" fill="#FFFFFF" text-anchor="middle">Prepper Pi</text>')
    lines.append(f'  <text x="{final_width/2}" y="{text_y_start + 85}" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif" font-size="80" fill="#FFFFFF" text-anchor="middle">&#127957;</text>')
    lines.append('</svg>')
    
    # Save SVG
    svg_path = os.path.join(OUTPUT_DIR, SVG_FILE)
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"   Saved: {svg_path}")
    print(f"   ViewBox: 0 0 {final_width} {final_height}")
    
    return svg_path

def main():
    print("=" * 70)
    print("Prepper-Pi Homepage QR Code Generator")
    print("=" * 70)
    print()
    print(f"Target URL: {HOMEPAGE_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        svg_path = generate_svg_qr()
        print()
        
        print("=" * 70)
        print("SVG QR Code Generation Complete!")
        print()
        print(f"Generated File: {svg_path}")
        print()
        print("Features:")
        print("   - High error correction (Level H)")
        print("   - Black rounded rectangle background")
        print("   - White QR code area")
        print("   - Prepper Pi title in white")
        print("   - Camping emoji (off-grid symbol)")
        print("   - QR code 60% larger (box_size=16, border=2)")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
