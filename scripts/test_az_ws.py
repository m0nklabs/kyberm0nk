import socketio
import time

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("Connected to Agent Zero")
    sio.emit('message', {'text': 'Hi, what is 2+2? Please reply with just the number.'})

@sio.on('message')
def on_message(data):
    print("Agent Zero replied:", data)

@sio.on('disconnect')
def on_disconnect():
    print("Disconnected from Agent Zero")

try:
    sio.connect('http://127.0.0.1:50001')
    sio.wait()
except Exception as e:
    print("Error:", e)
