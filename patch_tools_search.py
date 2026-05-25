import sys

content = open("/home/flip/CrewAI-Studio/app/my_tools.py").read()
# Replace the translation call for github_search too
content = content.replace(
    "super().__init__(tool_id, t('tool.github_search'),",
    "super().__init__(tool_id, 'GithubSearchTool',"
)

with open("/home/flip/CrewAI-Studio/app/my_tools.py", "w") as f:
    f.write(content)
