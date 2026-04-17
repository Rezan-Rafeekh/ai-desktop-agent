import time
import pyautogui
from vision import capture_screen, analyze_screen, verify_action

# Safety constraint
pyautogui.FAILSAFE = True

def execute_action(action: dict):
    """Translates the structured JSON action from vision LLM into pyautogui commands."""
    atype = action.get("type", "").lower()
    val = action.get("value", "")
    
    # Explicit constraint: Minimum 1.0s between actions
    time.sleep(1.2)
    
    if atype == "click":
        x, y = action.get("x", 0), action.get("y", 0)
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
    elif atype == "type":
        # Type character by character to mimic human and avoid buffer drops
        pyautogui.typewrite(str(val), interval=0.03)
    elif atype == "hotkey":
        keys = [k.strip().lower() for k in str(val).split(',')]
        pyautogui.hotkey(*keys)
    elif atype == "wait":
        time.sleep(2)
    elif atype == "done":
        pass
    else:
        print(f"Unknown action type: {atype}")

def agent_loop(goal: str, steps: list, status_callback=None) -> dict:
    """
    Real Observe -> Plan -> Act loop.
    Iterates through given steps via Visual LLM perception and GUI control.
    """
    context = {"task": goal, "results": [], "errors": []}
    
    for step in steps:
        if status_callback:
            status_callback("AGENT", "running", f"Initiating autonomous visual loop for step: {step}")
            
        step_goal = f"Main Goal: {goal} | Current Step Objective: {step}"
        attempts = 0
        max_attempts = 10
        step_done = False
        
        while attempts < max_attempts and not step_done:
            # 1. Observe
            if status_callback: 
                status_callback("AGENT", "running", "Observe: Capturing screen state...")
            before_path = capture_screen("obs")
            
            # 2. Decide (Plan)
            if status_callback: 
                status_callback("AGENT", "thoughts", "Decide: Analyzing screen and determining next micro-action...")
            
            action = analyze_screen(before_path, step_goal)
            reason = action.get("reason", "No explicit reason.")
            
            if status_callback:
                status_callback("AGENT", "thoughts", f"Plan: {action.get('type').upper()} -> {reason}")
            
            if action.get("type") == "done":
                if status_callback: 
                    status_callback("AGENT", "done", f"Visual verification confirmed mapping for '{step}' is done.")
                step_done = True
                break
                
            # 3. Act
            if status_callback: 
                status_callback("AGENT", "running", f"Act: Executing {action.get('type')} macro...")
            try:
                execute_action(action)
            except Exception as e:
                err = f"Action execution failed: {e}"
                context["errors"].append(err)
                if status_callback: status_callback("AGENT", "error", err)
            
            # 4. Verify
            if status_callback: 
                status_callback("AGENT", "running", "Verify: Checking visual delta...")
            after_path = capture_screen("verify")
            
            # Use visual LLM to verify if the intended macro succeeded
            verification = verify_action(before_path, after_path, expected_change=action.get("type"))
            if not verification.get("success", True):
                msg = f"Verification failed: {verification.get('reason')}. Will retry or adjust."
                if status_callback: status_callback("AGENT", "running", msg)
                
            # Sleep extra to ensure stability
            time.sleep(1)
            attempts += 1
            
        if not step_done:
            err_msg = f"Failed to complete step '{step}' autonomously after maximum visual actions."
            if status_callback: status_callback("AGENT", "error", err_msg)
            context["errors"].append(err_msg)

    return context