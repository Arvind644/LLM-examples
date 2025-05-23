import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from composio_openai import ComposioToolSet, App

def main():
    """
    Email Assistant
    Demonstrates integration between OpenAI and Composio using the SDK
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize API clients
    openai_api_key = os.getenv("OPENAI_API_KEY")
    composio_api_key = os.getenv("COMPOSIO_API_KEY")
    
    if not openai_api_key or not composio_api_key:
        print("Error: Missing API keys. Please set OPENAI_API_KEY and COMPOSIO_API_KEY in .env file")
        return
    
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["COMPOSIO_API_KEY"] = composio_api_key
    
    # Initialize clients
    openai_client = OpenAI()
    composio_toolset = ComposioToolSet()
    
    print("OpenAI & Composio Email Assistant")
    print("===============================")
    
    try:
        # First, check if Gmail connection exists
        print("Checking Gmail connection...")
        
        # Get Gmail tools
        gmail_tools = composio_toolset.get_tools(apps=[App.GMAIL])
        
        if not gmail_tools:
            print("Gmail tools not found. Please make sure Gmail integration is set up.")
            print("You can connect your Gmail account with:")
            print("  composio login")
            print("  composio add gmail")
            return
        
        print(f"Found {len(gmail_tools)} Gmail tools")
        
        # Create an assistant that can use Gmail tools
        print("Creating email assistant...")
        
        assistant_instructions = """
        You are an email assistant that can:
        1. Read emails from Gmail
        2. Summarize email content
        3. Determine if emails need a response
        4. Draft replies to emails
        
        When asked to process emails, you'll:
        - Retrieve the most recent email
        - Provide a one-sentence summary
        - Determine if it needs a reply
        - Draft a response if needed
        """
        
        # Create the assistant
        assistant = openai_client.beta.assistants.create(
            name="Email Assistant",
            instructions=assistant_instructions,
            model="gpt-4-turbo-preview",
            tools=gmail_tools
        )
        
        # Create a thread
        thread = openai_client.beta.threads.create()
        
        # Add a message to the thread
        task = "Process my most recent email in my inbox. Provide a summary, determine if it needs a reply, and draft a response if needed."
        message = openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=task
        )
        
        print("Processing your inbox...")
        
        # Run the assistant
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        # Handle the assistant's tool calls
        print("Assistant is analyzing your emails...")
        run_result = composio_toolset.wait_and_handle_assistant_tool_calls(
            client=openai_client,
            run=run,
            thread=thread
        )
        
        # Get all messages from the thread to see the results
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # Print the assistant's response
        for message in messages.data:
            if message.role == "assistant":
                for content in message.content:
                    if content.type == "text":
                        print("\nAssistant's analysis:")
                        print("---------------------")
                        print(content.text.value)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()