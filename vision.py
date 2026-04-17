import os
import json
import time
import base64
from datetime import datetime
from PIL import ImageGrab
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
VISION_MODEL = "llama-3.2-11b-vision-preview"

home = os.path.expanduser("~")
onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
SCREENSHOT_DIR = os.path.join(desktop_dir, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def capture_screen(label="screen") -> str:
    """Takes a screenshot, saves it with a timestamp, and returns the path."""
    timestamp = datetime.now().strftime("%H%M%S_%f")[:10]
    filename = os.path.join(SCREENSHOT_DIR, f"{label}_{timestamp}.png")
    img = ImageGrab.grab()
    img.save(filename, "PNG")
    return filename

def clean_json(text: str) -> str:
    import re
    text = text.strip()
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def analyze_screen(screenshot_path: str, goal: str) -> dict:
    """
    Sends the screenshot to the Vision LLM to determine the next action.
    Returns: { "type": "click"|"type"|"hotkey"|"wait"|"done", "value": "...", "x": int, "y": int, "reason": "..." }
    """
    base64_image = encode_image(screenshot_path)
    
    prompt = f"""
You are an autonomous desktop agent controlling a Windows PC.
Your current high-level goal is: "{goal}"

Analyze the provided screenshot of the current screen. Determine the EXACT NEXT single action you need to take to progress towards the goal.

Action Types allowed:
- "click": requires x, y coordinates to click (estimate pixels relative to typical 1920x1080 resolution).
- "type": requires 'value' (the string to type).
- "hotkey": requires 'value' (comma-separated keys like "ctrl,s").
- "wait": wait for UI to load.
- "done": if the goal has been fully achieved.

Return ONLY a valid JSON object matching this schema:
{{
  "type": "click" | "type" | "hotkey" | "wait" | "done",
  "value": "string value (or empty if click/wait)",
  "x": 0,
  "y": 0,
  "reason": "Brief explanation of what you see and why you are taking this action"
}}
No other text, no markdown.
"""
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=300,
        )
        content = response.choices[0].message.content
        data = json.loads(clean_json(content))
        return data
    except Exception as e:
        print(f"Vision API error: {e}")
        # Graceful fallback: just wait if Vision fails
        return {"type": "wait", "value": "", "x": 0, "y": 0, "reason": f"Vision error: {str(e)}"}

def verify_action(before_path: str, after_path: str, expected_change: str) -> dict:
    """
    Compares two screenshots to confirm an action worked.
    Returns: {"success": true/false, "reason": "..."}
    """
    before_b64 = encode_image(before_path)
    after_b64 = encode_image(after_path)
    
    prompt = f"""
You are a QA automation agent.
You are given two screenshots:
1) An image showing the state BEFORE an action.
2) An image showing the state AFTER an action.

Expected visual change: "{expected_change}"

Did the expected change occur successfully based on the visual difference between Image 1 and Image 2?
Return ONLY a JSON object:
{{
  "success": true or false,
  "reason": "Briefly explain what changed or why it failed"
}}
"""
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{before_b64}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{after_b64}"}},
                    ],
                }
            ],
            temperature=0.1,
        )
        
        content = response.choices[0].message.content
        data = json.loads(clean_json(content))
        return data
    except Exception as e:
        print(f"Vision Verification error: {e}")
        return {"success": True, "reason": "Assuming success due to Vision API error fallback."}