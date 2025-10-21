
import os
import sys
from PIL import Image
import cairosvg

def convert_svg(svg_path):
    base_name = os.path.splitext(svg_path)[0]

    # Convert SVG to PNG
    png_path = base_name + ".png"
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    print(f"Converted {svg_path} to {png_path}")

    # Convert PNG to JPG
    jpg_path = base_name + ".jpg"
    img = Image.open(png_path)
    rgb_img = img.convert('RGB')
    rgb_img.save(jpg_path)
    print(f"Converted {png_path} to {jpg_path}")

    # Convert SVG to PDF
    pdf_path = base_name + ".pdf"
    cairosvg.svg2pdf(url=svg_path, write_to=pdf_path)
    print(f"Converted {svg_path} to {pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_svg.py <path_to_svg_file>")
        sys.exit(1)
    
    svg_file = sys.argv[1]
    if not os.path.exists(svg_file):
        print(f"Error: SVG file not found at {svg_file}")
        sys.exit(1)
    
    convert_svg(svg_file)
