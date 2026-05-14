import sys

content = open("/home/flip/kyberm0nk/.agent-projects/CrewAI-Studio/app/my_tools.py").read()
# Replace the translation call with explicit string matching TOOL_CLASSES key
content = content.replace(
    "super().__init__(tool_id, t('tool.github_push', default='GitHub Push Tool')",
    "super().__init__(tool_id, 'GithubPushTool'"
)

with open("/home/flip/kyberm0nk/.agent-projects/CrewAI-Studio/app/my_tools.py", "w") as f:
    f.write(content)
