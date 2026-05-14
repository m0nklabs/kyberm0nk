with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "r") as f:
    text = f.read()

import re
fixed_text = re.sub(r'body = json\.dumps\(json_body\)\.encode\("utf-8"\)', 
                    'body = json.dumps(json_body).encode("utf-8")\n                        logger.info("MESSAGES AFTER PATCH: " + str([(m.get("role")) for m in msgs]))', text, flags=re.DOTALL)

with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "w") as f:
    f.write(fixed_text)
