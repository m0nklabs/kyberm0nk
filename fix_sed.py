with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "r") as f:
    text = f.read()

import re
fixed_text = re.sub(r'f"\n\n\[System directive.*?\]"', 'f"\\\\n\\\\n[System directive: Please start your response exactly with the following text: {prefill.get(\'content\', \'\')}]"', text, flags=re.DOTALL)

with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "w") as f:
    f.write(fixed_text)
