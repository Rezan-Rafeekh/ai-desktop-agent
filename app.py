import sys, os, glob, time
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from planner import detect_goals, create_plan
from executor import execute_plan
from memory import load_memory

st.set_page_config(
    page_title="Visual Desktop Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
  .stApp { background:#0d1117; color:#e2e8f0; }
  .main-title { font-size:2rem; font-weight:800; color:#00d9ff; letter-spacing:-0.02em; }
  .thought-box { background:#1e1e1e; border-left:3px solid #f59e0b; padding:10px; margin:5px 0; font-family:monospace; color:#d4d4d4; font-size:0.85rem;}
  .step-row { border-left: 2px solid #00d9ff; padding-left: 10px; margin: 4px 0; font-size:0.9rem;}
  .step-done { border-color: #00ff88; }
  .step-err { border-color: #ef4444; }
  
  .history-card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 10px;
      margin-bottom: 8px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s ease;
  }
  .history-card:hover { border-color: #00d9ff; background: #1c2128; }
  .history-tag { color: #64748b; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; margin-bottom: 4px; }
  .history-text { color: #e2e8f0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AI Desktop Workflow Agent</div>', unsafe_allow_html=True)
st.divider()

if "run_state" not in st.session_state: st.session_state.run_state = False
if "thread_done" not in st.session_state: st.session_state.thread_done = True
if "thoughts" not in st.session_state: st.session_state.thoughts = []
if "timeline" not in st.session_state: st.session_state.timeline = {}
if "task_input" not in st.session_state: st.session_state.task_input = "Generate a professional task report"
if "context_res" not in st.session_state: st.session_state.context_res = {}
if "stop_requested" not in st.session_state: st.session_state.stop_requested = False

# ── SIDEBAR: PROMPT HISTORY ───────────────────────────────────
with st.sidebar:
    st.markdown("### 📜 Prompt History")
    st.markdown("Recent successful tasks. Click to reuse.")
    
    history_data = load_memory()
    if not history_data:
        st.info("No history yet. Successful runs will appear here.")
    else:
        # Show last 10 successful prompts
        for i, entry in enumerate(reversed(history_data[-10:])):
            prompt_text = entry.get("task", "")
            if st.button(f"Reuse: {prompt_text[:30]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.task_input = prompt_text
                st.rerun()
            
            # Visual card for context (non-interactive, button above triggers)
            st.markdown(f"""
            <div class="history-card">
                <div class="history-tag">Successful Task</div>
                <div class="history-text">{prompt_text}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

col_ctrl, col_log, col_feed = st.columns([1, 1.2, 1.5], gap="medium")

with col_ctrl:
    st.markdown("#### Task Presets")
    p1, p2, p3 = st.columns(3)
    if p1.button("Generate Task Report"): st.session_state.task_input = "Generate Task Report"
    if p2.button("Draft Email in Outlook"): st.session_state.task_input = "Draft Email in Outlook"
    if p3.button("Create Python file in VS Code"): st.session_state.task_input = "Create Python file in VS Code"

    task = st.text_area("Objective", value=st.session_state.task_input, height=100)
    use_llm = st.toggle("Autonomous Mode (LLM plans steps)", value=True)
    
    st.divider()
    if not st.session_state.run_state:
        run_btn = st.button("▶ Execute Real Automation", type="primary", use_container_width=True)
    else:
        if st.button("🛑 STOP AGENT", type="secondary", use_container_width=True):
            st.session_state.stop_requested = True
            st.warning("Stop signal sent! Waiting for current step to finalize...")
        run_btn = False

with col_log:
    st.markdown("#### Agent Thoughts")
    thoughts_ph = st.empty()
    
    st.markdown("#### Step Timeline")
    timeline_ph = st.empty()

with col_feed:
    st.markdown("#### Live Screen Feed")
    feed_ph = st.empty()


def get_latest_screenshot():
    home = os.path.expanduser("~")
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
    sdir = os.path.join(desktop_dir, "screenshots")
    if not os.path.exists(sdir): return None
    files = glob.glob(os.path.join(sdir, "*.png"))
    if not files: return None
    return max(files, key=os.path.getctime)

def render_ui_state():
    # Render thoughts
    with thoughts_ph.container():
        for t in st.session_state.thoughts[-7:]:
            st.markdown(f"<div class='thought-box'>{t}</div>", unsafe_allow_html=True)
            
    # Render timeline
    with timeline_ph.container():
        for step_name, data in st.session_state.timeline.items():
            cls = "step-done" if data['status'] == 'done' else "step-err" if data['status'] == 'error' else "step-row"
            dur = f"{data['duration']:.1f}s" if 'duration' in data else "..."
            st.markdown(f"<div class='{cls}'><b>{step_name}</b> [{data['status'].upper()}] - {dur}</div>", unsafe_allow_html=True)

def agent_thread_worker(plan, task_desc):
    def on_status(step, status, msg, **kwargs):
        if status == "thoughts":
            st.session_state.thoughts.append(msg)
        else:
            if step not in st.session_state.timeline:
                st.session_state.timeline[step] = {"status": status, "start": time.time()}
            
            st.session_state.timeline[step]["status"] = status
            
            if status in ["done", "error"]:
                start = st.session_state.timeline[step]["start"]
                st.session_state.timeline[step]["duration"] = time.time() - start

    # Start executor with abort check
    st.session_state.context_res = execute_plan(
        plan, task_desc, 
        status_callback=on_status,
        check_abort=lambda: st.session_state.get("stop_requested", False)
    )
    st.session_state.thread_done = True


if run_btn:
    st.session_state.run_state = True
    st.session_state.thread_done = False
    st.session_state.stop_requested = False
    st.session_state.thoughts = []
    st.session_state.timeline = {}
    st.session_state.context_res = {}
    
    plan = []
    if use_llm:
        plan = create_plan(detect_goals(task))
    else:
        # Static fallback
        plan = ["write_excel"]
        
    st.session_state.timeline["PLANNING"] = {"status": "done", "start": time.time(), "duration": 0.5}
    
    # Spawn thread for blocking executor
    t = threading.Thread(target=agent_thread_worker, args=(plan, task))
    add_script_run_ctx(t)
    t.start()
    
    # Main UI Event Loop: auto-refresh screen every 2 seconds
    while not st.session_state.thread_done:
        latest_img = get_latest_screenshot()
        if latest_img:
            feed_ph.image(latest_img, caption="Live Robot Vision", use_container_width=True)
            
        render_ui_state()
        time.sleep(2)
        
    st.session_state.run_state = False
    render_ui_state()
    st.success("✅ Automation Run Complete!")