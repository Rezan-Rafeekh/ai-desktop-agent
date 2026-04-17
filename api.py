import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from executor import execute_plan
from planner import detect_goals, create_plan

# Setup static directories
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
home = os.path.expanduser("~")
onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
desktop_dir = onedrive_desktop if os.path.exists(onedrive_desktop) else os.path.join(home, "Desktop")
SCREENSHOT_DIR = os.path.join(desktop_dir, "screenshots")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

app.mount("/screenshots", StaticFiles(directory=SCREENSHOT_DIR), name="screenshots")

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            task = request.get("task", "")
            use_llm = request.get("use_llm", False)
            override_plan = request.get("plan", [])
            
            if use_llm:
                plan = create_plan(detect_goals(task))
            else:
                # Prepend core data extraction pipeline even to manual plans
                # to satisfy the "Strictly use real data" core requirement.
                base_pipeline = ["read_file", "extract_data", "validate_data"]
                # Only prepend if they aren't already there
                plan = base_pipeline + [s for s in override_plan if s not in base_pipeline]
                
            if not plan:
                await websocket.send_json({"type": "error", "msg": "No steps selected."})
                continue
                
            await websocket.send_json({"type": "plan", "plan": plan})
            
            loop = asyncio.get_running_loop()
            queue = asyncio.Queue()
            
            def status_callback(step, status, message, screenshot_path=None, preview_data=None):
                shot_url = None
                if screenshot_path and os.path.exists(screenshot_path):
                    filename = os.path.basename(screenshot_path)
                    shot_url = f"/screenshots/{filename}"
                
                asyncio.run_coroutine_threadsafe(
                    queue.put({
                        "type": "log",
                        "step": step,
                        "status": status,
                        "msg": message,
                        "screenshot": shot_url,
                        "preview_data": preview_data
                    }),
                    loop
                )
                
            def run_executor():
                try:
                    execute_plan(plan, task, status_callback=status_callback)
                except Exception as e:
                    asyncio.run_coroutine_threadsafe(
                        queue.put({"type": "error", "msg": str(e)}), loop
                    )
                finally:
                    asyncio.run_coroutine_threadsafe(
                        queue.put({"type": "done"}), loop
                    )

            task_handle = loop.run_in_executor(None, run_executor)
            
            while True:
                msg = await queue.get()
                await websocket.send_json(msg)
                if msg["type"] in ["done", "error"]:
                    break
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WS error: {e}")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
