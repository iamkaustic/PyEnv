from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a new image with a transparent background
    img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for the base
    draw.rounded_rectangle([(40, 40), (216, 216)], radius=30, fill=(65, 105, 225))
    
    # Draw Python logo-like snake
    # First snake part
    draw.rounded_rectangle([(80, 100), (180, 120)], radius=10, fill=(255, 255, 255))
    # Second snake part
    draw.rounded_rectangle([(160, 120), (180, 170)], radius=10, fill=(255, 255, 255))
    # Third snake part
    draw.rounded_rectangle([(80, 150), (160, 170)], radius=10, fill=(255, 255, 255))
    # Fourth snake part
    draw.rounded_rectangle([(80, 150), (100, 200)], radius=10, fill=(255, 255, 255))
    # Fifth snake part
    draw.rounded_rectangle([(80, 180), (160, 200)], radius=10, fill=(255, 255, 255))
    
    # Save as PNG
    img.save('icon.png')
    
    # Convert to ICO for Windows
    try:
        img.save('icon.ico', format='ICO')
        print("Icon created successfully!")
    except Exception as e:
        print(f"Could not create ICO file: {e}")
        print("PNG icon was created successfully.")

if __name__ == "__main__":
    create_icon()
