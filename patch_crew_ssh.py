import sys
content = open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py").read()

ssh_tool_code = """
import subprocess

class WindowsSSHCommandInputSchema(BaseModel):
    \"\"\"Input schema for Windows SSH Command tool.\"\"\"
    command: str = Field(..., description="The command to execute on the Windows PC via SSH (CMD/PowerShell syntax).")

class WindowsSSHCommandTool(BaseTool):
    \"\"\"Tool to execute commands on the Windows PC equipped with Unreal Engine via SSH.\"\"\"
    name: str = "Windows SSH Command execution"
    description: str = "Executes arbitrary commands on the Windows 11 PC (unreal-windows) over SSH. Useful to trigger git pull, UnrealBuildTool, zipping files, and creating GitHub releases using the 'gh' CLI."
    args_schema: Type[BaseModel] = WindowsSSHCommandInputSchema

    def _run(self, command: str) -> str:
        try:
            # We use the unreal-windows SSH alias already configured in the container
            result = subprocess.run(
                ["ssh", "unreal-windows", command],
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + "\\n" + result.stderr
            if result.returncode == 0:
                return f"Success (Exit 0):\\n{output}"
            else:
                return f"Failed (Exit {result.returncode}):\\n{output}"
        except Exception as e:
            return f"Error executing SSH command: {str(e)}"

# Marker replacement
class GitHubRepoPushInputSchema
"""

content = content.replace("class GitHubRepoPushInputSchema", ssh_tool_code)

old_create_tool = """
    elif config["type"] == "github_push":
        return GitHubRepoPushTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
        )
    else:
"""

new_create_tool = """
    elif config["type"] == "github_push":
        return GitHubRepoPushTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
        )
    elif config["type"] == "windows_ssh_command":
        return WindowsSSHCommandTool()
    else:
"""
content = content.replace(old_create_tool, new_create_tool)

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "w") as f:
    f.write(content)
