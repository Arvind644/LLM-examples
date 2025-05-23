import os
from dotenv import load_dotenv
from openai import OpenAI
from composio_openai import ComposioToolSet, Action

def main():
    """
    Google Docs Creator
    Creates documents in Google Docs with AI-generated content
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
    
    print("OpenAI & Composio Google Docs Creator")
    print("====================================")
    
    try:
        # Check if Google Docs connection exists
        print("Checking Google Docs connection...")
        
        # Get only the document creation action
        gdocs_actions = ['GOOGLEDOCS_CREATE_DOCUMENT']
        
        gdocs_tools = composio_toolset.get_tools(actions=gdocs_actions)
        
        if not gdocs_tools:
            print("Google Docs tools not found. Please make sure Google Docs integration is set up.")
            print("You can connect your Google account with:")
            print("  composio login")
            print("  composio add googledocs")
            return
        
        print(f"Found document creation tool")
        
        # Create an assistant that can use Google Docs creation tool
        print("Creating Google Docs assistant...")
        
        assistant_instructions = """
        You are a document creation assistant that specializes in creating Google Docs with rich content.
        
        When creating a new document:
        1. Use the GOOGLEDOCS_CREATE_DOCUMENT action
        2. Give the document a descriptive title based on the topic
        3. Generate comprehensive, well-structured content on the requested topic
        4. Include an introduction, multiple sections with detailed information, and a conclusion
        5. Confirm to the user when the document has been created successfully
        6. If possible, provide a link or ID to access the document
        """
        
        # Create the assistant
        assistant = openai_client.beta.assistants.create(
            name="Google Docs Creator",
            instructions=assistant_instructions,
            model="gpt-4-turbo-preview",
            tools=gdocs_tools
        )
        
        # Create a thread
        thread = openai_client.beta.threads.create()
        
        # Ask about document topic
        topic = input("\nWhat would you like to create a document about? ")
        
        user_message = f"""Create a new Google Doc titled '{topic.title()} Overview' with comprehensive content about {topic}.
        
        The document should include:
        1. An introduction to {topic}
        2. Multiple sections covering important aspects of {topic} with detailed information
        3. A conclusion summarizing the key points
        
        Please use the GOOGLEDOCS_CREATE_DOCUMENT action to create this document with complete content.
        """
        
        # Add the user's message to the thread
        message = openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        print(f"\nCreating document about '{topic}'...")
        print("This may take a minute as content is being generated...")
        
        # Run the assistant
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        # Handle the assistant's tool calls
        print("Assistant is creating your Google Doc...")
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
                        print("\nAssistant's response:")
                        print("====================")
                        print(content.text.value)
        
        # Ask for document link
        print("\nWould you like to get the link to your document?")
        get_link = input("Enter 'y' for yes: ").strip().lower()
        
        if get_link == 'y':
            follow_up_message = openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Can you provide the document link or ID so I can access it?"
            )
            
            follow_up_run = openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            print("Getting document link...")
            follow_up_result = composio_toolset.wait_and_handle_assistant_tool_calls(
                client=openai_client,
                run=follow_up_run,
                thread=thread
            )
            
            # Get updated messages
            updated_messages = openai_client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Print only the newest message
            for message in updated_messages.data[:1]:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            print("\nDocument access information:")
                            print("===========================")
                            print(content.text.value)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 