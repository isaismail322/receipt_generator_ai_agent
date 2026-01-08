import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
import httpx
# from io import BytesIO
# from pdf_generator import pdf_receipt_generator
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
RECEIPT_TABLE_NAME = os.environ["RECEIPT_TABLE_NAME"]
PRIMARY_KEY_FIELD = os.environ["PRIMARY_KEY_FIELD"]
RESERVATION_TABLE_NAME = os.environ["RESERVATION_TABLE_NAME"]



agent = Agent(
    "openai:gpt-5-nano",
    system_prompt=(
        "You are a helpful assistant that can access Data table to "
        "query the results, generate the receipts, create and cancel the reservations. "
        "Use the available tools to answer questions about "
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


# 2️⃣ DEFINE INPUT MODEL FOR CREATING RESERVATION
class AirtableCreateReservationInput(BaseModel):
    passenger_name: str = Field(..., description="Name of the passenger")
    car_type: str = Field(..., description="Type of car requested")
    pickup_time: str = Field(..., description="Pickup date and time")
    dropoff_time: str = Field(..., description="Drop-off date and time")
    contact_number: str = Field(..., description="Customer contact number")
    pickup_address: str = Field(..., description="Pickup location address")
    dropoff_address: str = Field(..., description="Drop-off location address")

# 3️⃣ DEFINE INPUT MODEL FOR CANCELLING RESERVATION
class AirtableCancelReservationInput(BaseModel):
    reservation_number: int = Field(..., description="Reservation number (primary key) to cancel")



 # Tool to get the available receipt data from the connected database
@agent.tool
async def fetch_records(
    ctx: RunContext,
    args: AirtableFetchInput
    ) -> list[dict]:
    """
    Fetch records from Airtable by Name (primary key).
    """

    url = f"https://api.airtable.com/v0/{BASE_ID}/{RECEIPT_TABLE_NAME}"

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

    async with httpx.AsyncClient(timeout=30) as client:
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


@agent.tool
async def create_reservation(
    ctx: RunContext,
    args: AirtableCreateReservationInput
) -> dict:
    """
    Create a new reservation record in with customer details.
    """
    
    url = f"https://api.airtable.com/v0/{BASE_ID}/{RESERVATION_TABLE_NAME}"
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare the record data - adjust field names to match your Airtable schema
    record_data = {
        "records": [
            {
                "fields": {
                    "Name": args.passenger_name,
                    "Car_Type": args.car_type,
                    "Pickup_Time": args.pickup_time,
                    "Dropoff_Time": args.dropoff_time,
                    "Contact_Number": args.contact_number,
                    "Pickup_Address": args.pickup_address,
                    "Dropoff_Address": args.dropoff_address,
                    "Reservation_Type": "New_Reservation"
                    # "Reservation": will be auto-generated if it's an auto-number field
                }
            }
        ]
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=record_data)
        response.raise_for_status()
    
    created_record = response.json().get("records", [])[0]
    
    return {
        "success": True,
        "record_id": created_record.get("id"),
        "reservation_number": created_record.get("fields").get("Reservation_Number",{}), # .get("fields").get("Reservation_Number"),
        "fields": created_record.get("records", {}),
        "message": f"Reservation created successfully for {args.passenger_name}"
    }



# Tool to cancel a reservation in Airtable
@agent.tool
async def cancel_reservation(
    ctx: RunContext,
    args: AirtableCancelReservationInput
) -> dict:
    """
    Cancel a reservation by updating the reservation type field to 'cancelled reservation'.
    """
    
    # Step 1: First, find the record by reservation number to get its record ID
    fetch_url = f"https://api.airtable.com/v0/{BASE_ID}/{RESERVATION_TABLE_NAME}"
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Find the record using filterByFormula
    formula = f"{{Reservation_Number}}={int(args.reservation_number)}"
    params = {
        "filterByFormula": formula,
        "maxRecords": 1
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch the record
        response = await client.get(fetch_url, headers=headers, params=params)
        response.raise_for_status()
        
        records = response.json().get("records", [])
        
        if not records:
            return {
                "success": False,
                "message": f"Reservation {args.reservation_number} not found"
            }
        
        # Get the Airtable record ID
        record_id = records[0]["id"]
        
        # Step 2: Update the record
        update_url = f"https://api.airtable.com/v0/{BASE_ID}/{RESERVATION_TABLE_NAME}/{record_id}"
        
        update_data = {
            "fields": {
                "Reservation_Type": "Cancelled_Reservation"  # Adjust field name to match your Airtable
            }
        }
        
        # Update the record using PATCH
        update_response = await client.patch(update_url, headers=headers, json=update_data)
        update_response.raise_for_status()
        
        updated_record = update_response.json()
        
        return {
            "success": True,
            "reservation_number": args.reservation_number,
            "message": f"Reservation {args.reservation_number} has been cancelled successfully",
            "updated_fields": updated_record.get("fields", {})
        }