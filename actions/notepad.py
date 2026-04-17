import subprocess
import pyautogui
import time

def open_notepad():
    subprocess.Popen(["notepad"])
    time.sleep(2)

def write_notes():
    pyautogui.write("Meeting Notes:", interval=0.05)
    pyautogui.press("enter")
    pyautogui.write("- Task 1", interval=0.05)

def write_report():
    pyautogui.write("Daily Report:", interval=0.05)
    pyautogui.press("enter")
    pyautogui.write("- Completed tasks", interval=0.05)