import os
import sys
from PIL import Image, ImageDraw
import win32com.client
import winshell

def create_icon():
    # Create a circular purple icon
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw purple circle
    circle_color = (128, 0, 128, 255)  # Purple
    draw.ellipse([10, 10, size-10, size-10], fill=circle_color)
    
    # Draw "A" in white
    from PIL import ImageFont
    try:
        # Try to use Arial font
        font = ImageFont.truetype("arial.ttf", 140)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw text in white
    draw.text((size//2-40, size//2-70), "A", fill="white", font=font)
    
    # Save as ICO file
    icon_path = os.path.join(os.path.dirname(__file__), "awesome_icon.ico")
    image.save(icon_path, format='ICO', sizes=[(256, 256)])
    return icon_path

def create_shortcut():
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    desktop = winshell.desktop()
    icon_path = create_icon()
    python_path = sys.executable
    main_script = os.path.join(current_dir, "main.py")
    shortcut_path = os.path.join(desktop, "Awesome.lnk")
    
    # Create shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = python_path
    shortcut.Arguments = f'"{main_script}"'
    shortcut.WorkingDirectory = current_dir
    shortcut.IconLocation = icon_path
    shortcut.save()
    
    print(f"Created shortcut at: {shortcut_path}")

if __name__ == "__main__":
    create_shortcut()
