import os
import time
import pyautogui
from datetime import datetime
from vision import capture_screen

def generate_code(task: str) -> str:
    """
    Opens VS Code visually, types python code, and saves file.
    """
    timestamp = datetime.now().strftime("%H%M%S")
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
    filename = os.path.join(desktop_dir, f"script_{timestamp}.py")
    
    print("Launching VS Code natively...")
    # 'code' cli trigger
    os.system("code")
    time.sleep(6)
    capture_screen("vscode_loading")
    
    # Create new file
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(2)
    
    print("Typing Python code...")
    content = f"# Auto-generated scaffold for: {task}\n\nimport sys\nimport os\n\ndef main():\n    print('Hello from GenAI Script!')\n\nif __name__ == '__main__':\n    main()\n"
    pyautogui.typewrite(content, interval=0.02)
    time.sleep(1)
    
    print("Saving python script...")
    # Save As
    pyautogui.hotkey('ctrl', 's')
    time.sleep(2)
    
    pyautogui.typewrite(filename, interval=0.01)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    
    capture_screen("vscode_saved")
    print(f"✅ VS Code file generated at {filename}")
    return filename