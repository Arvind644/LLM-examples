#!/usr/bin/env python3
"""
Document and Email Analyzer

Functions:
1. Analyzes documents in Google Docs
2. Processes recent emails and stores summaries in Google Docs
3. Sends email summaries via Gmail

Requirements:
    pip install python-dotenv openai composio-openai

Usage:
    1. Set up environment variables in a .env file:
       OPENAI_API_KEY=your_openai_api_key
       COMPOSIO_API_KEY=your_composio_api_key
    2. Run: python document_analyzer.py
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from composio_openai import ComposioToolSet, Action, App

# Load environment variables
load_dotenv()

# Initialize clients
openai_api_key = os.getenv("OPENAI_API_KEY")
composio_api_key = os.getenv("COMPOSIO_API_KEY")

if not openai_api_key or not composio_api_key:
    print("Error: Missing API keys. Please set OPENAI_API_KEY and COMPOSIO_API_KEY in .env file")
    exit(1)

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["COMPOSIO_API_KEY"] = composio_api_key

# Initialize clients
openai_client = OpenAI()
composio_toolset = ComposioToolSet()

# Configure search keywords for different document types
DOCUMENT_TYPES = {
    "contracts": ["agreement", "contract", "terms", "party", "obligation"],
    "reports": ["analysis", "findings", "results", "data", "conclusion"],
    "presentations": ["slide", "deck", "presentation", "overview", "summary"]
}

def email_to_doc():
    """Process the most recent email and save its summary to a Google Doc"""
    print("\n=== Email to Google Doc Processor ===")
    
    # Check Gmail connection
    print("Checking Gmail connection...")
    gmail_tools = composio_toolset.get_tools(apps=[App.GMAIL])
    
    if not gmail_tools:
        print("Gmail tools not found. Please make sure Gmail integration is set up.")
        print("You can connect your Gmail account with:")
        print("  composio login")
        print("  composio add gmail")
        return False
    
    # Check Google Docs connection
    print("Checking Google Docs connection...")
    gdocs_tools = composio_toolset.get_tools(apps=[App.GOOGLEDOCS])
    
    if not gdocs_tools:
        print("Google Docs tools not found. Please make sure Google Docs integration is set up.")
        print("You can connect your Google account with:")
        print("  composio login")
        print("  composio add googledocs")
        return False
    
    # Step 1: Create an assistant that can use both Gmail and Google Docs tools
    all_tools = gmail_tools + gdocs_tools
    
    assistant_instructions = """
    You are an assistant that processes emails and creates documents.
    
    First, you should:
    1. Retrieve the most recent email from Gmail
    2. Create a summary of the email with key information:
       - Sender
       - Subject
       - Date/time received
       - Main points of the content
       - Any action items or requests
    
    Then, you should:
    3. Create a new Google Doc to store the email summary
    4. Give the document a title based on the email subject
    5. Format the summary clearly and professionally
    6. Save the document
    7. Return the document ID or link
    
    Be thorough but concise in your summary.
    """
    
    assistant = openai_client.beta.assistants.create(
        name="Email to Document Processor",
        instructions=assistant_instructions,
        model="gpt-4-turbo",
        tools=all_tools
    )
    
    # Create a thread
    thread = openai_client.beta.threads.create()
    
    # Add a message to the thread
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please process my most recent email and create a Google Doc with a summary of it. Use a clear title and format."
    )
    
    print("Processing your most recent email...")
    
    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Handle the assistant's tool calls
    print("Assistant is working...")
    run_result = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread
    )
    
    # Get the results
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    
    # Print the assistant's response
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    print("\nAssistant's response:")
                    print("---------------------")
                    print(content.text.value)
                    return True
    
    return False

def list_recent_docs(days=7, document_type=None):
    """List recent documents from Google Docs"""
    # Get the Google Docs tools
    gdocs_tools = composio_toolset.get_tools(apps=[App.GOOGLEDOCS])
    
    if not gdocs_tools:
        print("Google Docs tools not found. Please make sure Google Docs integration is set up.")
        print("You can connect your Google account with:")
        print("  composio login")
        print("  composio add googledocs")
        return []
    
    # Create a thread with the assistant
    assistant_instructions = f"""
    You are a helpful assistant that can list recent documents from Google Docs.
    Focus on documents modified in the last {days} days.
    """
    
    if document_type:
        assistant_instructions += f" Look specifically for documents that might contain content related to {document_type}."
    
    assistant = openai_client.beta.assistants.create(
        name="Document Scanner",
        instructions=assistant_instructions,
        model="gpt-4-turbo",
        tools=gdocs_tools
    )
    
    thread = openai_client.beta.threads.create()
    
    # Add a message to the thread
    query = f"List my recent Google Docs documents from the last {days} days"
    if document_type:
        query += f" that may contain {document_type} content"
        
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )
    
    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Handle the assistant's tool calls
    print("Assistant is searching for documents...")
    run_result = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread
    )
    
    # Get the results
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    
    # Process documents from the messages
    documents = []
    for message in messages.data:
        if message.role == "assistant":
            # Look for content with document information
            for content in message.content:
                if content.type == "text":
                    # Try to extract document information from text
                    text = content.text.value
                    if "documents found" in text.lower() or "document id" in text.lower():
                        documents = extract_docs_from_text(text)
                        break
    
    return documents

def extract_docs_from_text(text):
    """Extract document information from assistant text response"""
    # Simple extraction - in a real app, this would be more robust
    documents = []
    lines = text.split('\n')
    
    current_doc = {}
    for line in lines:
        if ":" not in line:
            continue
            
        line = line.strip()
        if line.lower().startswith(("title:", "document:", "name:")):
            # If we already have a document, add it to the list
            if current_doc and "id" in current_doc:
                documents.append(current_doc)
            # Start a new document
            current_doc = {"name": line.split(":", 1)[1].strip()}
        elif line.lower().startswith(("id:", "document id:")) and current_doc:
            current_doc["id"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith(("last modified:", "modified:")) and current_doc:
            current_doc["modifiedTime"] = line.split(":", 1)[1].strip()
    
    # Add the last document if exists
    if current_doc and "id" in current_doc:
        documents.append(current_doc)
    
    return documents

def get_document_content(doc_id):
    """Get content from a Google Doc"""
    # Get the Google Docs tools
    gdocs_tools = composio_toolset.get_tools(apps=[App.GOOGLEDOCS])
    
    if not gdocs_tools:
        print("Google Docs tools not found.")
        return ""
    
    # Create a thread with the assistant
    assistant = openai_client.beta.assistants.create(
        name="Document Reader",
        instructions="You are a helpful assistant that can read content from Google Docs.",
        model="gpt-4-turbo",
        tools=gdocs_tools
    )
    
    thread = openai_client.beta.threads.create()
    
    # Add a message to the thread
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please read the content of the Google Doc with ID: {doc_id}"
    )
    
    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Handle the assistant's tool calls
    print(f"Assistant is reading document content...")
    run_result = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread
    )
    
    # Get the results
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    
    # Extract content from the last assistant message
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    # Look for content in the message
                    text = content.text.value
                    if "content" in text.lower() or len(text) > 100:
                        return text
    
    return ""

def analyze_document(content, document_type):
    """Analyze document content using OpenAI"""
    prompt = f"""
    Analyze the following document that appears to be a {document_type}.
    Provide a concise summary (max 3 paragraphs) highlighting:
    - Key information and findings
    - Important dates or deadlines
    - Action items or next steps
    - Any risks or concerns

    Document content:
    {content[:4000]}  # Limit content length to avoid token limits
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a document analysis expert. Extract key information from documents and summarize it professionally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def send_email_summary(recipient, subject, body):
    """Send email summary via Gmail using Composio"""
    # Get the Gmail tools
    gmail_tools = composio_toolset.get_tools(apps=[App.GMAIL])
    
    if not gmail_tools:
        print("Gmail tools not found. Please make sure Gmail integration is set up.")
        print("You can connect your Google account with:")
        print("  composio login")
        print("  composio add gmail")
        return False
    
    # Create a thread with the assistant
    assistant = openai_client.beta.assistants.create(
        name="Email Sender",
        instructions="You are a helpful assistant that can send emails through Gmail.",
        model="gpt-4-turbo",
        tools=gmail_tools
    )
    
    thread = openai_client.beta.threads.create()
    
    # Add a message to the thread
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please send an email to {recipient} with subject '{subject}' and the following body: {body}"
    )
    
    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Handle the assistant's tool calls
    print(f"Assistant is sending email to {recipient}...")
    run_result = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread
    )
    
    # Check if email was sent successfully
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    if "sent" in content.text.value.lower() or "success" in content.text.value.lower():
                        return True
    
    return False

def create_email_body(document_info, analysis):
    """Create email body with document analysis"""
    today = datetime.now().strftime("%B %d, %Y")
    
    email_body = f"""
    Document Analysis Report - {today}
    
    Document: {document_info.get('name', 'Untitled Document')}
    Last Modified: {document_info.get('modifiedTime', 'Unknown')}
    
    ANALYSIS SUMMARY:
    {analysis}
    
    This analysis was generated automatically using AI. Please review the original document for complete details.
    """
    
    return email_body

def main():
    print("\n===== Document and Email Analyzer =====\n")
    print("Choose an operation:")
    print("1. Analyze Google Docs and send email summaries")
    print("2. Process latest email and save to Google Docs")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        # Analyze documents flow
        document_type = input("Enter document type to analyze (contracts, reports, presentations) or press Enter for all: ").lower() or None
        days = int(input("Enter number of days to look back (default: 7): ") or 7)
        recipient = input("Enter email recipient: ")
        
        # Validate inputs
        if document_type and document_type not in DOCUMENT_TYPES:
            print(f"Invalid document type. Choose from: {', '.join(DOCUMENT_TYPES.keys())}")
            return
        
        print(f"Listing Google Docs documents from the last {days} days...")
        
        # List recent documents
        documents = list_recent_docs(days, document_type)
        
        if not documents or len(documents) == 0:
            print("No documents found matching the criteria.")
            return
        
        print(f"Found {len(documents)} documents. Analyzing...")
        
        # Process each document
        for doc in documents[:5]:  # Limit to 5 documents to avoid hitting rate limits
            print(f"Processing: {doc.get('name', 'Untitled')}")
            
            # Get document content
            content = get_document_content(doc.get('id'))
            
            # Determine document type if not specified
            doc_type = document_type
            if not doc_type:
                # Simple keyword matching to guess document type
                doc_text = content.lower() if content else ""
                scores = {dt: sum(1 for kw in kws if kw.lower() in doc_text) for dt, kws in DOCUMENT_TYPES.items()}
                doc_type = max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else "general"
            
            # Analyze document
            analysis = analyze_document(content, doc_type)
            
            # Create and send email
            subject = f"Document Analysis: {doc.get('name', 'Document')} [{doc_type.capitalize()}]"
            email_body = create_email_body(doc, analysis)
            
            print(f"Sending analysis to {recipient}...")
            send_email_summary(recipient, subject, email_body)
            
            print(f"Analysis sent for document: {doc.get('name', 'Untitled')}")
            
        print("Document analysis and reporting complete!")
    
    elif choice == "2":
        # Process email to Google Doc
        success = email_to_doc()
        if success:
            print("Email processing and document creation complete!")
        else:
            print("Email processing failed.")
    
    elif choice == "3":
        print("Exiting...")
    
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 