from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

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

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9005), HookHandler)
    print("Listening on port 9005...")
    server.serve_forever()
