import os
import time
import pyautogui
from datetime import datetime
from vision import capture_screen

def write_excel(task: str, data: list[dict]) -> str:
    """
    Opens Excel graphically, types data via Tab/Enter, creates chart, and saves.
    """
    timestamp = datetime.now().strftime("%d-%m-%Y_%H%M%S")
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
    filename = os.path.join(desktop_dir, f"Data_{timestamp}.xlsx")

    print("Opening Microsoft Excel natively...")
    os.system("start excel")
    time.sleep(12) # Doubled wait for Excel startup
    
    capture_screen("excel_loading_check")
    # Hit ESC to clear any initial popups/focus issues
    pyautogui.press('esc')
    time.sleep(1)
    
    # Hit Enter to select "Blank workbook"
    pyautogui.press('enter')
    time.sleep(5)
    
    capture_screen("excel_ready")
    
    print("Typing spreadsheet data...")
    # Type headers
    headers = ["Task", "Assigned To", "Status"]
    for header in headers:
        pyautogui.typewrite(header, interval=0.01)
        pyautogui.press('tab')
    
    pyautogui.press('enter') # Moves to next row's starting column
    time.sleep(0.5)
    
    # Type data
    if not data:
        data = [
            {"task_name": "System Setup", "assigned_to": "Alice", "status": "Done"},
            {"task_name": "UI Design", "assigned_to": "Bob", "status": "In Progress"},
            {"task_name": "API Dev", "assigned_to": "Charlie", "status": "Pending"}
        ]
        
    for i, row in enumerate(data[:10]): # Limit for demo speed
        vals = [str(row.get("task_name", f"Task {i}")), 
                str(row.get("assigned_to", "User")), 
                str(row.get("status", "Pending"))]
        for val in vals:
            pyautogui.typewrite(val[:20], interval=0.01) # truncate super long strings
            pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(0.2)
        
    time.sleep(1)
    
    print("Generating Chart...")
    # Add a chart using Alt+F1 default macro
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'f1')
    time.sleep(2)
    
    print("Saving spreadsheet...")
    # Hit ESC to exit any active cell-edit mode which blocks F12
    pyautogui.press('esc')
    time.sleep(0.5)
    
    # Save As
    pyautogui.press('f12')
    time.sleep(2.5)
    
    pyautogui.typewrite(filename, interval=0.02)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    
    capture_screen("excel_saved")
    print(f"✅ Excel file saved autonomously at {filename}")
    
    return filename