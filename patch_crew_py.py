import sys
content = open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py").read()

push_tool_code = """
class GitHubRepoPushInputSchema(BaseModel):
    \"\"\"Input schema for GitHub repository push file.\"\"\"
    file_path: str = Field(..., description="The path to the file in the repository (e.g. 'src/main.py').")
    content: str = Field(..., description="The text content to commit.")
    commit_message: str = Field(..., description="The commit message.")
    branch: str = Field("main", description="The branch to commit to. Defaults to main.")

class GitHubRepoPushTool(BaseTool):
    \"\"\"Small GitHub REST tool to create or update a file in a repository without a local git clone.\"\"\"

    name: str = "GitHub repository push file"
    description: str = "Commit and push a single file's content to a GitHub repository using the GitHub REST API."
    args_schema: Type[BaseModel] = GitHubRepoPushInputSchema
    github_repo: str
    gh_token: str = Field(exclude=True)
    api_base: str = "https://api.github.com"

    def __init__(self, github_repo: str, gh_token: str, **kwargs: Any) -> None:
        super().__init__(github_repo=github_repo, gh_token=gh_token, **kwargs)
        self._generate_description()

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.gh_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _run(self, file_path: str, content: str, commit_message: str, branch: str = "main") -> str:
        file_url = f"{self.api_base}/repos/{self.github_repo}/contents/{file_path}"
        get_response = requests.get(f"{file_url}?ref={branch}", headers=self._headers(), timeout=REQUEST_TIMEOUT_SECONDS)
        
        sha = None
        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
            
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch
        }
        if sha:
            data["sha"] = sha
            
        put_response = requests.put(file_url, headers=self._headers(), json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if put_response.status_code in [200, 201]:
            return f"Success! File '{file_path}' committed and pushed to {branch}."
        else:
            return f"Failed to commit file. Code: {put_response.status_code}, Resp: {put_response.text}"

def load_yaml"""

content = content.replace("def load_yaml", push_tool_code)

old_create_tool = """def create_tool(tool_name: str, tools_config: dict[str, Any]) -> Any:
    \"\"\"Create a CrewAI tool from YAML config.\"\"\"
    config = tools_config["tools"][tool_name]
    if config["type"] != "github_search":
        raise ValueError(f"Unsupported tool type: {config['type']}")

    gh_token = os.getenv(config.get("token_env", "GITHUB_TOKEN")) or os.getenv(config.get("fallback_token_env", "GH_TOKEN"))
    if not gh_token:
        raise ValueError("Missing GitHub token env var: GITHUB_TOKEN or GH_TOKEN")

    return GitHubRepoSearchTool(
        github_repo=config["github_repo"],
        gh_token=gh_token,
        content_types=config.get("content_types") or ["code", "repo", "pr", "issue"],
    )"""

new_create_tool = """def create_tool(tool_name: str, tools_config: dict[str, Any]) -> Any:
    \"\"\"Create a CrewAI tool from YAML config.\"\"\"
    config = tools_config["tools"][tool_name]
    
    gh_token = os.getenv(config.get("token_env", "GITHUB_TOKEN")) or os.getenv(config.get("fallback_token_env", "GH_TOKEN"))
    if not gh_token:
        raise ValueError("Missing GitHub token env var: GITHUB_TOKEN or GH_TOKEN")

    if config["type"] == "github_search":
        return GitHubRepoSearchTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
            content_types=config.get("content_types") or ["code", "repo", "pr", "issue"],
        )
    elif config["type"] == "github_push":
        return GitHubRepoPushTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
        )
    else:
        raise ValueError(f"Unsupported tool type: {config['type']}")"""

content = content.replace(old_create_tool, new_create_tool)

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "w") as f:
    f.write(content)
