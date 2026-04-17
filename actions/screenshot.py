import os, time
from datetime import datetime
from PIL import ImageGrab, Image

home = os.path.expanduser("~")
onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
SCREENSHOT_DIR = os.path.join(desktop_dir, "screenshots")

def _ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def _timestamp():
    return datetime.now().strftime("%H%M%S_%f")[:10]

def take_screenshot(label: str = "screen", delay: float = 1.5) -> str:
    """
    Wait `delay` seconds (for window to render), then capture full screen.
    Returns saved file path.
    """
    _ensure_dir()
    time.sleep(delay)
    img      = ImageGrab.grab()
    filename = os.path.join(SCREENSHOT_DIR, f"{label}_{_timestamp()}.png")
    img.save(filename, "PNG")
    print(f"Screenshot saved -> {filename}")
    return filename

def screenshot_excel(delay: float = 2.0) -> str:
    return take_screenshot("excel", delay)

def screenshot_word(delay: float = 2.0) -> str:
    return take_screenshot("word", delay)

def screenshot_pdf(delay: float = 2.0) -> str:
    return take_screenshot("pdf", delay)

def resize_for_display(path: str, max_width: int = 900) -> str:
    """
    Resize screenshot proportionally for Streamlit display.
    Returns path to resized image (overwrites original).
    """
    img = Image.open(path)
    w, h = img.size
    if w > max_width:
        ratio      = max_width / w
        new_size   = (max_width, int(h * ratio))
        img        = img.resize(new_size, Image.LANCZOS)
        img.save(path, "PNG")
    return path