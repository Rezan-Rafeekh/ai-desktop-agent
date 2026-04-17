import os
import time
import subprocess
import pyautogui
from datetime import datetime
from vision import capture_screen
from llm import generate_word_summary

def generate_report_doc(task: str, excel_data: list[dict] | None = None) -> str:
    """
    Opens Word graphically via subprocess, types content, and saves via UI.
    """
    timestamp = datetime.now().strftime("%d-%m-%Y_%H%M%S")
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
    filename = os.path.join(desktop_dir, f"Report_{timestamp}.docx")
    
    summary = generate_word_summary(task, excel_data) if excel_data else f"Automated report for {task}."

    print("Opening Microsoft Word natively...")
    os.system("start winword")
    time.sleep(12)  # Doubled wait for Word to load completely on slower machines
    
    # Verify/capture load
    capture_screen("word_loading_check")
    
    # Clears any initial splash screens or popups that might steal focus
    pyautogui.press('esc') 
    time.sleep(1)
    
    # Hit enter to select 'Blank document' template
    pyautogui.press('enter')
    time.sleep(5)
    
    capture_screen("word_ready")
    
    # Type report
    print("Typing document contents...")
    content = f"Automated Task Report\n--------------------\nTask: {task}\nDate: {timestamp}\n\nExecutive Summary:\n{summary}\n"
    pyautogui.typewrite(content, interval=0.01)
    time.sleep(2)
    
    # Save
    print("Saving document...")
    # Hit ESC to exit any active mode which might block F12
    pyautogui.press('esc')
    time.sleep(1)
    
    # F12 reliably opens the "Save As" directly in Office 
    pyautogui.press('f12')  
    time.sleep(4)
    
    pyautogui.typewrite(filename, interval=0.02)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    
    capture_screen("word_saved")
    print(f"✅ Word report saved autonomously at {filename}")
    
    return filename