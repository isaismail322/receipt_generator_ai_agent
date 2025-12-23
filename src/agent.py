import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
import httpx
from io import BytesIO
from pdf_generator import pdf_receipt_generator
# from airbyte_agent_github import GithubConnector
# from airbyte_agent_github.models import GithubGithubPersonalAccessTokenAuthConfig
load_dotenv()

# connector = GithubConnector(
#     auth_config=GithubGithubPersonalAccessTokenAuthConfig(
#         token=os.environ["GITHUB_ACCESS_TOKEN"]
#         )
#         )


# Environment Variables
AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
BASE_ID = os.environ["BASE_ID"] # Please replace with your actual Airtable Base ID (starts with 'app')
TABLE_NAME = os.environ["TABLE_NAME"]
PRIMARY_KEY_FIELD = os.environ["PRIMARY_KEY_FIELD"]


agent = Agent(
    "openai:gpt-5-nano",
    system_prompt=(
        "You are a helpful assistant that can access Data table to "
        "query the results and generate the receipts. Use the available tools to answer questions about "
        "Receipts data. Be concise and accurate in your responses."
    ),
)

# Tool to list issues in a repository
# @agent.tool_plain
# async def list_issues(owner: str, repo: str, limit: int = 10) -> str:
#     """List open issues in a GitHub repository."""
#     result = await connector.issues.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
#     return str(result.data)


# Tool to list pull requests in a repository
# @agent.tool_plain
# async def list_pull_requests(owner: str, repo: str, limit: int = 10) -> str:
#     """List open pull requests in a GitHub repository."""
#     result = await connector.pull_requests.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
#     return str(result.data)

# 1️⃣ DEFINE INPUT MODEL FIRST
class AirtableFetchInput(BaseModel):
    # name: str = Field(..., description="Primary key (Name) to search")
    reservation : int = Field(..., description="Primary key (Reservation number) to search")
    # max_records: int = Field(1, description="Number of records to fetch")
    view: str = Field("Grid view", description="Airtable view name")


 # Tool to get the available receipt data from the connected database
@agent.tool
async def fetch_airtable_records(
    ctx: RunContext,
    args: AirtableFetchInput
    ) -> list[dict]:
    """
    Fetch records from Airtable by Name (primary key).
    """

    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    # formula = f"{{Name}}='{args.name.lower()}'"
    formula = f"{{Reservation}}='{int(args.reservation)}'"

    params = {
        "filterByFormula": formula,
        # "maxRecords": args.max_records,
        "maxRecords": 5,
        "view": args.view
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()

    # records = response.json().get("records", [])


    data = response.json().get("records", [])
    # pdf_file = pdf_receipt_generator(data)
    return data
    
    
    # return [
    #     AirtableRecord(
    #         id=r["id"],
    #         fields=r["fields"]
    #     )
    #     for r in response.json()["records"]
    # ]