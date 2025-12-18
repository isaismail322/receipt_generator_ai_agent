import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubGithubPersonalAccessTokenAuthConfig
load_dotenv()

connector = GithubConnector(
    auth_config=GithubGithubPersonalAccessTokenAuthConfig(
        token=os.environ["GITHUB_ACCESS_TOKEN"]
        )
        )

agent = Agent(
    "openai:gpt-5-nano",
    system_prompt=(
        "You are a helpful assistant that can access GitHub repositories, issues, "
        "and pull requests. Use the available tools to answer questions about "
        "GitHub data. Be concise and accurate in your responses."
    ),
)

# Tool to list issues in a repository
@agent.tool_plain
async def list_issues(owner: str, repo: str, limit: int = 10) -> str:
    """List open issues in a GitHub repository."""
    result = await connector.issues.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)


# Tool to list pull requests in a repository
@agent.tool_plain
async def list_pull_requests(owner: str, repo: str, limit: int = 10) -> str:
    """List open pull requests in a GitHub repository."""
    result = await connector.pull_requests.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)