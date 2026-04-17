import os
import time
import urllib.parse
import pyautogui
from vision import capture_screen

TO_EMAIL  = "fathimarezan12@gmail.com"
CC_EMAIL  = ""

pyautogui.FAILSAFE  = True

def send_email(context: dict | None = None) -> bool:
    context = context or {}
    doc_path   = context.get("doc",   "")
    excel_path = context.get("excel", "")
    task_desc  = context.get("task",  "Automated Task Report")
    to_email   = context.get("to_email", TO_EMAIL)

    body = f"Hello,\n\nPlease find the automated report for {task_desc} attached.\n\nRegards,\nAI Agent"
    subject = f"📋 Automated Task Report — {task_desc[:40]}"

    try:
        print("Launching traditional Outlook UI via macro...")
        # 1. Open outlook
        result = os.system("start outlook")
        if result != 0:
            raise Exception("Outlook executable not found in PATH.")
        
        time.sleep(8)
        capture_screen("outlook_loading")
        
        # 2. New Email
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(4)
        
        # 3. Fill Fields
        # Starts in 'To' field
        pyautogui.typewrite(to_email, interval=0.01)
        pyautogui.press('tab') # CC
        pyautogui.press('tab') # Subject
        
        pyautogui.typewrite(subject, interval=0.01)
        pyautogui.press('tab') # Body
        
        pyautogui.typewrite(body, interval=0.01)
        time.sleep(1)
        
        # 4. Attach Files (Insert > Attach File > Browse this PC)
        for filepath in filter(None, [doc_path, excel_path]):
            if os.path.exists(filepath):
                pyautogui.hotkey('alt', 'n') # Insert tab
                time.sleep(1)
                pyautogui.press('a')         # Attach File
                time.sleep(0.5)
                pyautogui.press('f')         # Browse this PC
                time.sleep(2)
                
                # Type filepath in dialog
                pyautogui.typewrite(filepath, interval=0.01)
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)
        
        # 5. Send
        pyautogui.hotkey('alt', 's')
        time.sleep(2)
        print("✅ Email sent via Outlook UI")
        
        capture_screen("outlook_sent")
        return True

    except Exception as e:
        print(f"Classic Outlook macro failed ({e}), falling back to mailto...")
        try:
            # Fallback mailto code
            mailto_url = f"mailto:{to_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            os.startfile(mailto_url)
            time.sleep(4)
            pyautogui.hotkey("ctrl", "enter")
            time.sleep(1)
            print("✅ Email sent via mailto fallback")
            return True
        except Exception as e2:
            print(f"Fallback mailto also failed: {e2}")
            return False
