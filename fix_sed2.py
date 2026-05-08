with open('/home/flip/kyberm0nk/scripts/agent_zero_up.sh', 'r') as f:
    lines = f.readlines()
with open('/home/flip/kyberm0nk/scripts/agent_zero_up.sh', 'w') as f:
    for line in lines:
        if 'except Exception as e' in line or 'self.logger.error' in line: continue
        f.write(line)
