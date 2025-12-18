import asyncio
import nest_asyncio
from agent import agent
nest_asyncio.apply()

# async def main():
#     print("GitHub Agent Ready! Ask questions about GitHub repositories.")
#     print("Type 'quit' to exit.\n")

#     history = None

#     while True:
#         prompt = input("You: ")
#         if prompt.lower() in ('quit', 'exit', 'q'):
#             break
#         result = await agent.run(prompt, message_history=history)
#         history = result.all_messages()  # Call the method
#         print(f"\nAgent: {result.output}\n")

# if __name__ == "__main__":
#     asyncio.run(main())



async def ask_agent(prompt: str, history=None):
    """
    Run the agent on a single prompt.
    Returns a dict with output and updated history.
    """
    result = await agent.run(prompt, message_history=history)
    return {"output": result.output, "history": result.all_messages()}

# Helper function to call from synchronous code
# def ask_agent_sync(prompt: str, history=None):
#     return asyncio.run(ask_agent(prompt, history))

def ask_agent_sync(prompt: str, history=None):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(ask_agent(prompt, history))