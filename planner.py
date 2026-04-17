from llm import parse_task_to_steps

VALID_STEPS = {
    "write_excel", "generate_report_doc", "generate_pdf", "send_email", "open_vscode"
}

def detect_goals(command: str) -> list[str]:
    """Wrap command in a list (one goal = full command)."""
    return [command.strip()]

def create_plan(goals: list[str]) -> list[str]:
    """
    Convert goals into an ordered list of executable step names.
    Directly relies on the comprehensive agentic vocabulary.
    """
    task = " ".join(goals)
    
    try:
        raw_plan = parse_task_to_steps(task)
        print(f"🤖 LLM RAW PLAN: {raw_plan}")
        # Filter to only valid known generation/GUI steps
        plan = [s for s in raw_plan if s in VALID_STEPS]
        print(f"✅ FILTERED PLAN: {plan}")
        if plan:
            return plan
    except Exception as e:
        print(f"⚠️  Planner LLM failed: {e} — using fallback plan")

    # Fallback: No action taken if LLM fails or task is unrelated
    return []