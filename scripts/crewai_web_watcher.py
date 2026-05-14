import asyncio
import re
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

app = FastAPI()

# Simple regex to strip ANSI escape codes so the output is clean HTML
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
LOG_FILE = "/home/flip/kyberm0nk/logs/crewai_live.log"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>KyberM0nk CrewAI Watcher</title>
    <style>
        body { 
            background-color: #0f172a; 
            color: #10b981; 
            font-family: 'Consolas', 'Courier New', monospace; 
            margin: 0; 
            padding: 20px; 
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #334155;
            padding-bottom: 15px;
        }
        h2 { margin: 0; color: #f8fafc; }
        .badge {
            background-color: #ef4444; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px;
            margin-left: 10px;
            vertical-align: middle;
        }
        .badge.active { background-color: #10b981; }
        #terminal { 
            background-color: #1e293b; 
            padding: 20px; 
            border-radius: 8px; 
            height: 75vh; 
            overflow-y: auto; 
            white-space: pre-wrap; 
            font-size: 14px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            line-height: 1.4;
        }
        .text-gray { color: #94a3b8; }
        .text-blue { color: #3b82f6; }
        .text-yellow { color: #eab308; }
        button { 
            background-color: #3b82f6; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            cursor: pointer; 
            border-radius: 6px; 
            font-weight: bold;
            font-family: inherit;
            transition: background-color 0.2s;
        }
        button:hover { background-color: #2563eb; }
        button:disabled { background-color: #475569; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🚀 KyberM0nk CrewAI Watcher <span id="statusBadge" class="badge">Disconnected</span></h2>
        <button id="startBtn" onclick="startRun()">Live Inhaken (Tail Log)</button>
    </div>
    <div id="terminal"><span class="text-gray">Ready. Start het script in je terminal via:</span><br/><span class="text-yellow">bash scripts/crewai_main_quest_run.sh</span><br/><br/><span class="text-gray">En klik daarna op 'Live Inhaken' om de output mee te kijken...</span><br/><br/></div>

    <script>
        let eventSource = null;

        function startRun() {
            const btn = document.getElementById('startBtn');
            const term = document.getElementById('terminal');
            const badge = document.getElementById('statusBadge');
            
            btn.disabled = true;
            btn.innerText = "Ingehaakt...";
            badge.innerText = "Live";
            badge.className = "badge active";
            term.innerHTML += "<span class='text-blue'>[System] Hooking into live session file (/logs/crewai_live.log)...</span>\\n\\n";
            
            if (eventSource) {
                eventSource.close();
            }
            
            eventSource = new EventSource('/stream');
            
            eventSource.onmessage = function(event) {
                let text = event.data;
                if (text.includes("[INFO]")) {
                    text = "<span class='text-blue'>" + text + "</span>";
                } else if (text.includes("Agent:") || text.includes("Task:")) {
                    text = "<span class='text-yellow'>" + text + "</span>";
                }
                
                term.innerHTML += text + "\\n";
                // Force autoscroll to bottom
                term.scrollTop = term.scrollHeight;
            };
            
            eventSource.onerror = function() {
                // Connection might just reset, don't show error immediately unless it stays broken
            };
        }
    </script>
</body>
</html>
"""

@app.get("/")
def index():
    return HTMLResponse(HTML_PAGE)

async def tail_stream():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

    # Gebruik tail -f om simpel in te haken op het bestand (startend met laatste 100 regels geschiedenis)
    process = await asyncio.create_subprocess_shell(
        f"tail -n 150 -f {LOG_FILE}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            text = line.decode(errors="replace").rstrip()
            
            # Strip crazy ANSI codes from CrewAI output
            clean_text = ANSI_ESCAPE.sub('', text)
            
            # Add timestamp
            import datetime
            now = datetime.datetime.now().strftime('%H:%M:%S')
            clean_text = f"<span class='text-gray'>[{now}]</span> {clean_text}"
            
            # Format for SSE safely
            clean_text = clean_text.replace('\\', '\\\\').replace('"', '\\"')
            yield f"data: {clean_text}\n\n"
    finally:
        process.terminate()

@app.get("/stream")
def stream():
    return StreamingResponse(tail_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8509, log_level="warning")
