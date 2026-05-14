import json

with open('/home/flip/kyberm0nk/configs/crewai/main_quest_studio_import.json', 'r') as f:
    data = json.load(f)

for agent in data.get('agents', []):
    if agent['id'] == 'A_kyber_ecosystem_optimizer':
        if 'TOOL_unreal_msbuild' not in agent['tool_ids']:
            agent['tool_ids'].extend(['TOOL_unreal_msbuild', 'TOOL_unreal_remote'])

# Check if the tools already exist in the tools array
tools_exist = any(t['tool_id'] == 'TOOL_unreal_msbuild' for t in data.get('tools', []))
if not tools_exist:
    data['tools'].append({
      "tool_id": "TOOL_unreal_msbuild",
      "name": "UnrealMSBuildTool",
      "description": "Triggers an MSBuild compilation of an Unreal Engine project over SSH.",
      "parameters": {}
    })
    data['tools'].append({
      "tool_id": "TOOL_unreal_remote",
      "name": "UnrealRemoteTool",
      "description": "Interacts with Unreal Engine 5 via its Web Remote Control API over SSH.",
      "parameters": {}
    })

with open('/home/flip/kyberm0nk/configs/crewai/main_quest_studio_import.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated tools.")
