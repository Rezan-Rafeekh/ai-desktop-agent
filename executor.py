import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.excel import write_excel
from actions.word import generate_report_doc
from actions.email import send_email
from memory import find_similar_task, save_task
from llm import call_llm

try:
    from actions.pdf import generate_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from actions.vscode import generate_code
except ImportError:
    pass

STEP_MAP = {
    "read_file":           "read_file",
    "extract_data":        "extract_data",
    "validate_data":       "validate_data",
    "write_excel":         "write_excel",
    "open_excel":          "write_excel",
    "excel":               "write_excel",
    "generate_report_doc": "generate_report_doc",
    "open_word":           "generate_report_doc",
    "generate_report":     "generate_report_doc",
    "word":                "generate_report_doc",
    "generate_pdf":        "generate_pdf",
    "send_email":          "send_email",
    "send_outlook_email":  "send_email",
    "open_outlook":        "send_email",
    "email":               "send_email",
    "open_vscode":         "open_vscode"
}

def _resolve(step) -> str:
    if isinstance(step, dict):
        step = step.get("action") or step.get("task") or ""
    return STEP_MAP.get(str(step).strip().lower(), str(step).strip().lower())

def ask_llm_for_retry(step, error):
    # Strictly retry the same step to prevent AI hallway hallucinations (like opening VS Code when Word fails)
    return step


from actions.file_reader import read_desktop_file_for_task

def execute_plan(plan: list, task: str, status_callback=None, check_abort=None) -> dict:
    def notify(step, status, msg, shot=None, preview_data=None):
        print(f"[{status.upper()}] {step}: {msg}")
        if status_callback:
            status_callback(step, status, msg, screenshot_path=shot, preview_data=preview_data)

    if check_abort and check_abort():
        notify("ABORT", "error", "Execution stopped by user.")
        return {}

    context = {
        "task":        task,
        "file_content":"",
        "excel":       None,
        "doc":         None,
        "pdf":         None,
        "data":        [],
        "screenshots": [],
        "errors":      []
    }

    # memory interception - disabled plan override to ensure prompt-based precision
    # similar = find_similar_task(task)
    # if similar:
    #     notify("MEMORY", "done", "Historical context analyzed.")
    #     # plan = similar["plan"]

    # Resolve and deduplicate plan to prevent redundant macro execution
    resolved_plan = []
    for raw_step in plan:
        step = _resolve(raw_step)
        if not resolved_plan or resolved_plan[-1] != step:
            resolved_plan.append(step)

    import pyautogui
    import time
    pyautogui.hotkey('win', 'd')
    time.sleep(1)

    for step in resolved_plan:
        if check_abort and check_abort():
            notify("ABORT", "error", "Halted mid-plan.")
            break
        
        max_retries = 3
        attempts = 0
        success = False
        
        while attempts < max_retries and not success:
            if check_abort and check_abort():
                notify("ABORT", "error", "Halted during retry.")
                break
            notify(step, "running", f"Starting {step} (Attempt {attempts + 1})...")
            try:
                if step == "read_file":
                    found_filename, file_content = read_desktop_file_for_task(task)
                    if found_filename and file_content:
                        context["file_content"] = file_content
                        notify(step, "done", f"Read contents of {found_filename}")
                    else:
                        raise ValueError("No matching file found on Desktop for extraction.")
                        
                elif step == "extract_data":
                    from llm import extract_structured_data
                    data = extract_structured_data(context["file_content"])
                    context["data"] = data
                    notify(step, "done", f"Extracted {len(data)} records successfully.", preview_data=data)

                elif step == "validate_data":
                    if not context.get("data"):
                        raise ValueError("Extracted dataset is completely empty.")
                    notify(step, "done", "Data validation passed successfully.")

                elif step == "write_excel":
                    path = write_excel(task, data=context.get("data", []))
                    context["excel"] = path
                    notify(step, "done", f"Excel saved -> {os.path.basename(path)}")

                elif step == "generate_report_doc":
                    path = generate_report_doc(task, excel_data=context.get("data"))
                    context["doc"] = path
                    notify(step, "done", f"Word doc saved -> {os.path.basename(path)}")

                elif step == "generate_pdf":
                    if PDF_AVAILABLE:
                        path = generate_pdf(task, context)
                        context["pdf"] = path
                        notify(step, "done", f"PDF saved -> {os.path.basename(path)}")
                    else:
                        notify(step, "skipped", "reportlab not installed.")

                elif step == "send_email":
                    from llm import extract_email_recipient
                    ext_em = extract_email_recipient(task)
                    if ext_em: context["to_email"] = ext_em
                    
                    ok = send_email(context=context)
                    if ok:
                        notify(step, "done", "Email dispatched via UI.")
                    else:
                        raise ValueError("Failed to dispatch email mapping.")
                
                elif step == "open_vscode":
                    path = generate_code(task)
                    notify(step, "done", f"VSCode python generation complete -> {os.path.basename(path)}")

                else:
                    notify(step, "skipped", f"Unknown step '{step}'")

                success = True

            except Exception as e:
                attempts += 1
                err_msg = str(e)
                context["errors"].append(err_msg)
                notify(step, "error", f"Execute failed: {err_msg}")
                
                if attempts < max_retries:
                    notify(step, "thoughts", f"Autonomous retry initiated for {step} (Attempt {attempts + 1}).")
                    time.sleep(2) # Cooldown before retry
                    # step = step (strictly retrying existing step)
                else:
                    notify(step, "error", "All execution retries exhausted.")
                    break
        
        if not success:
            break
            
    if not context.get("errors"):
        save_task(task, plan, f"Successfully executed via agent loop ({len(plan)} actions).")
        
    return context