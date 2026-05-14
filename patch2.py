with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "r") as f:
    content = f.read()

# Fix the broken string
content = content.replace("f\"\\n\\n[System directive: Please start your response exactly with the following \ntext: {prefill.get('content', '')}]\"", "f\"\\n\\n[System directive: Please start your response exactly with the following text: {prefill.get('content', '')}]\"")
content = content.replace("f\"\\n\\n[System directive: Please start your response exactly with the following text: {prefill.get('content', '')}]\"", "f\"\\n\\n[System directive: Please start your response exactly with the following text: {prefill.get('content', '')}]\"")

with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "w") as f:
    f.write(content)
