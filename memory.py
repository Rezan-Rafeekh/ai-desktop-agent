import os
import json
from collections import Counter

def _get_memory_file() -> str:
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
    return os.path.join(desktop_dir, "tasks_memory.json")

def load_memory() -> list:
    mem_file = _get_memory_file()
    if not os.path.exists(mem_file):
        return []
    try:
        with open(mem_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_task(task: str, plan: list, result_summary: str):
    """Saves a successfully completed task and its exact plan to memory."""
    mem_file = _get_memory_file()
    memory = load_memory()
    
    new_entry = {
        "task": task,
        "plan": plan,
        "result": result_summary,
        "success": True if "failed" not in result_summary.lower() else False
    }
    
    memory.append(new_entry)
    with open(mem_file, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)
        
def find_similar_task(new_task: str) -> dict | None:
    """Uses a simple keyword intersection to find similar historical tasks."""
    memory = load_memory()
    if not memory: return None
    
    new_words = set(new_task.lower().split())
    best_match = None
    highest_score = 0
    
    for entry in memory:
        # Only reuse successful plans
        if not entry.get("success", False):
            continue
            
        old_words = set(entry.get("task", "").lower().split())
        if not old_words: continue
        
        score = len(new_words.intersection(old_words)) / len(new_words)
        # Threshold: if >60% word match
        if score > 0.6 and score > highest_score:
            highest_score = score
            best_match = entry
            
    return best_match

def get_memory_stats() -> dict:
    memory = load_memory()
    total = len(memory)
    successes = sum(1 for m in memory if m.get("success", False))
    success_rate = round(successes / total * 100, 2) if total > 0 else 0.0
    
    # Flatten all successful plans to find common steps
    all_steps = []
    for m in memory:
        if m.get("success", False):
            all_steps.extend(m.get("plan", []))
            
    most_common = [step for step, count in Counter(all_steps).most_common(3)]
    
    return {
        "total": total,
        "success_rate": success_rate,
        "most_common_steps": most_common
    }
