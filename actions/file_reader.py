import os

def read_desktop_file_for_task(task_prompt: str) -> tuple[str | None, str | None]:
    """
    Scans the user's desktop files. If a filename from the desktop is 
    found within the task_prompt string (exact match, case-insensitive), 
    it reads and returns the filename and its text content.
    Returns (filename, content) or (None, None).
    """
    # Check for common Windows OneDrive Desktop path first, then standard Desktop
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    standard_desktop = os.path.join(home, "Desktop")
    
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else standard_desktop
    if not os.path.exists(desktop_dir):
        return None, None
        
    best_match = None
    best_content = None
    max_len = 0
    
    # Pre-filter files to those actually mentioned in the prompt
    for item in os.listdir(desktop_dir):
        item_path = os.path.join(desktop_dir, item)
        if os.path.isfile(item_path):
            lower_item = item.lower()
            if lower_item in task_prompt.lower():
                # Prefer the logest filename to avoid partial matches 
                # (e.g. matching 'data.txt' when 'project_data.txt' is prompt)
                if len(lower_item) > max_len:
                    try:
                        with open(item_path, "r", encoding="utf-8") as f:
                            best_match = item
                            best_content = f.read()
                            max_len = len(lower_item)
                    except Exception as e:
                        print(f"Failed to read {item}: {e}")
                    
    return best_match, best_content
