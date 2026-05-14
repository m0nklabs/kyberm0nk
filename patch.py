import re

with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "r") as f:
    content = f.read()

# Locate the json.loads(body) and is_stream extraction
search = """        if path == "chat/completions":
            try:
                json_body = json.loads(body)
                is_stream = json_body.get("stream", False)
            except (json.JSONDecodeError, Exception):
                pass"""

replacement = """        if path == "chat/completions":
            try:
                json_body = json.loads(body)
                is_stream = json_body.get("stream", False)
                # WORKAROUND: llama.cpp "Assistant response prefill is incompatible with enable_thinking"
                msgs = json_body.get("messages", [])
                if msgs and msgs[-1].get("role") == "assistant" and len(msgs) >= 2:
                    prefill = msgs.pop()
                    # Append it to the preceding user message instead
                    if msgs[-1].get("role") == "user":
                        msgs[-1]["content"] = str(msgs[-1].get("content", "")) + f"\n\n[System directive: Please start your response exactly with the following text: {prefill.get('content', '')}]"
                        json_body["messages"] = msgs
                        body = json.dumps(json_body).encode("utf-8")
            except (json.JSONDecodeError, Exception):
                pass"""

if search in content:
    content = content.replace(search, replacement)
    with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "w") as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("Could not find the target block.")
