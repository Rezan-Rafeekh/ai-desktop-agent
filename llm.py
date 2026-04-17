from dotenv import load_dotenv
import os, json, re
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def clean_json(text: str) -> str:
    """Strip markdown fences and extract first JSON array or object."""
    text = text.strip()
    # Remove markdown fences explicitly
    text = re.sub(r"```json|```", "", text).strip()
    # Find the outermost [...] or {...}
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        content = match.group(1)
        # Final pass to remove any trailing junk outside the last brace/bracket
        return content.strip()
    return text.strip()

def call_llm(prompt: str, temperature: float = 0.2) -> str:
    """Raw LLM call, returns string."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

def parse_task_to_steps(task: str) -> list[str]:
    """
    Asks LLM to map user intent strictly to one or more functional modules.
    Ensures that unrelated applications are NEVER opened.
    """
    prompt = f"""
You are a desktop automation classifier.
Map the user's intent to the CORRECT tool(s) from this list:
- write_excel: Use ONLY if the user asks for spreadsheets, tables, sales data, or charts.
- generate_report_doc: Use ONLY if the user asks for a Word document, project report, or summary.
- generate_pdf: Use ONLY if 'PDF' is mentioned.
- send_email: Use ONLY if 'email', 'Outlook', or a recipient address is mentioned.
- open_vscode: Use ONLY if 'VS Code', 'python file', or 'coding' is mentioned.

Task/Intent: "{task}"

Rules:
1. Return ONLY a valid JSON array of strings.
2. If the user asks for "VS Code", DO NOT include "write_excel" or "generate_report_doc" unless they also specifically asked for them.
3. Be EXTREMELY minimal. If you are unsure, return an empty array [].
4. No explanation, no markdown text.
"""
    raw = call_llm(prompt, temperature=0.0) # Maximum precision
    try:
        steps = json.loads(clean_json(raw))
        if isinstance(steps, list):
            return [s for s in steps if s in ["write_excel", "generate_report_doc", "generate_pdf", "send_email", "open_vscode"]]
    except:
        pass
    return []

def extract_structured_data(file_content: str) -> list[dict]:
    """
    Ask LLM to extract realistic row data directly from the text file.
    Returns list of dicts with 9 fields.
    """
    prompt = f"""
You are a precise data extraction bot.
Extract task records directly and ONLY from the provided text below.
DO NOT hallucinate or invent any missing data, values, or tasks.
If a field is missing or unknown, leave it as an empty string "".

Return ONLY a valid JSON array of objects. Each object must have these exact keys:
"task_id", "task_name", "assigned_to", "status", "priority", "start_date", "end_date", "completion_percentage", "notes"

For "completion_percentage", extract the number (0-100) or leave blank if unknown.

Data to extract from:
{file_content}

Return ONLY the valid JSON array string. No explanation, no markdown.
"""
    raw = call_llm(prompt, temperature=0.1)
    try:
        data = json.loads(clean_json(raw))
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception as e:
        print(f"Extraction parsing error: {e}")
    return []

def generate_word_summary(task: str, excel_data: list[dict]) -> str:
    """Ask LLM to write a professional summary paragraph analyzing real data."""
    rows_text = "\n".join(
        f"- {r.get('task_name', 'Unknown')}: Status={r.get('status', '')}, Priority={r.get('priority', '')}, Completion={r.get('completion_percentage', '')}%"
        for r in excel_data
    )
    prompt = f"""
Write a short professional 3-paragraph report summary based ONLY on the data below.
DO NOT invent any tasks or imaginary progress.

Data:
{rows_text}

Format Rules:
- Paragraph 1: General overview and estimated overall completion percentage.
- Paragraph 2: Specifically identify incomplete tasks.
- Paragraph 3: Point out high priority pending/incomplete tasks and recommendations.

Plain text only. No markdown, no headers, no bullet points.
"""
    return call_llm(prompt, temperature=0.3)

def extract_email_recipient(task: str) -> str:
    """Ask LLM to extract the recipient email address from the task prompt."""
    prompt = f"""
You are an email extraction bot. Extract the recipient email address from the text below.
If there are multiple emails, extract the first destination or most logical one.
If there is no email mentioned, return an empty string "".

Text: {task}

Return ONLY the email address string, no quotes, no explanation, no markdown.
"""
    raw = call_llm(prompt, temperature=0.1).strip()
    # Basic validation
    if "@" in raw and "." in raw:
        return raw
    return ""