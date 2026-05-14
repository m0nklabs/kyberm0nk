import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import pystray
from PIL import Image, ImageDraw

class HookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/run-grass':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Starting Unreal Engine Grass Generation...")
            
            # Open a log file to capture the output of Unreal
            log_file = open(r"J:\UnrealProjects\NewNexus\Webhook_Unreal.log", "w")
            
            # WINERROR 87 FIX: Cannot combine DETACHED_PROCESS and CREATE_NEW_CONSOLE.
            subprocess.Popen([
                r"C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
                r"J:\UnrealProjects\NewNexus\NewNexus.uproject",
                r"-ExecutePythonScript=J:\UnrealProjects\NewNexus\SpawnGrass.py", 
                "-NoUI",
                "-NullRHI"
            ], 
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.DETACHED_PROCESS)
        else:
            self.send_response(404)
            self.end_headers()

server = None

def run_server():
    global server
    server = HTTPServer(('0.0.0.0', 9005), HookHandler)
    server.serve_forever()

def create_image():
    # Genereer on the fly een simpel groen vierkantje als icoon (Gras!)
    image = Image.new('RGB', (64, 64), color=(34, 139, 34)) # Forest Green
    d = ImageDraw.Draw(image)
    d.rectangle([0, 0, 63, 63], outline=(0, 0, 0), width=3)
    return image

def on_quit(icon, item):
    icon.stop()
    if server:
        server.shutdown()

if __name__ == '__main__':
    # Start de Webhook server parallel in de achtergrond
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Zet het icoontje in de System Tray, dit blokkeert de main thread (zoals Windows wil)
    icon = pystray.Icon("UE_Webhook", create_image(), "Unreal Webhook", menu=pystray.Menu(
        pystray.MenuItem("Afsluiten", on_quit)
    ))
    icon.run()
