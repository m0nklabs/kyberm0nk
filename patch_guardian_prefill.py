with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "r") as f:
    text = f.read()

import re

# Find the block from WORKAROUND to json.JSONDecodeError
old_block = r'''                # WORKAROUND: llama\.cpp "Assistant response prefill is incompatible with enable_thinking"
                msgs = json_body\.get\("messages", \[\]\)
                if msgs and msgs\[-1\]\.get\("role"\) == "assistant" and len\(msgs\) >= 2:
                    prefill = msgs\.pop\(\)
                    # Append it to the preceding user message instead
                    if msgs\[-1\]\.get\("role"\) == "user":
                        msgs\[-1\]\["content"\] = str\(msgs\[-1\]\.get\("content", ""\)\) \+ f"\\n\\n\[System directive: Please start your response exactly with the following text: \{prefill\.get\('content', ''\)\}\]"
                        json_body\["messages"\] = msgs
                        body = json\.dumps\(json_body\)\.encode\("utf-8"\)
                        logger\.info\("MESSAGES AFTER PATCH: " \+ str\(\[\(m\.get\("role"\)\) for m in msgs\]\)\)'''

new_block = '''                # WORKAROUND: llama.cpp "Assistant response prefill is incompatible with enable_thinking"
                msgs = json_body.get("messages", [])
                
                # Consolidate ALL trailing assistant messages
                trailing_assistant_contents = []
                while len(msgs) > 0 and msgs[-1].get("role") == "assistant":
                    popped = msgs.pop()
                    # Prepend because we are popping from the end
                    content = popped.get("content", "")
                    if content:
                        trailing_assistant_contents.insert(0, str(content))
                        
                if trailing_assistant_contents and len(msgs) >= 1:
                    combined_prefill = "\\n".join(trailing_assistant_contents)
                    
                    # Find the last user message and append the prefill instruction
                    # Usually it's msgs[-1], but loop just in case
                    last_user_idx = -1
                    for i in range(len(msgs)-1, -1, -1):
                        if msgs[i].get("role") == "user":
                            last_user_idx = i
                            break
                            
                    if last_user_idx != -1:
                        msgs[last_user_idx]["content"] = str(msgs[last_user_idx].get("content", "")) + f"\\n\\n[System directive: Please start your response exactly with the following text: {combined_prefill}]"
                        json_body["messages"] = msgs
                        body = json.dumps(json_body).encode("utf-8")
                        logger.info("MESSAGES AFTER PREFILL CONSOLIDATION: " + str([(m.get("role")) for m in msgs]))
                    else:
                        # If no user message found, just put them back as one assistant message?
                        # No, if there's no user message it's weird. We'll just leave it and hope for the best.
                        logger.warning("Found trailing assistant messages but no user message to attach to.")
                elif trailing_assistant_contents:
                    # Put them back if there's less than 1 message left (edge case)
                    pass'''

fixed_text = re.sub(old_block, new_block, text, flags=re.MULTILINE)

with open("/home/flip/llama_cpp_guardian/app/proxy/server.py", "w") as f:
    f.write(fixed_text)
