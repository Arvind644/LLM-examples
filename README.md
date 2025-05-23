# OpenAI + Composio Integration

This project demonstrates how to build AI assistants using Composio's integration tools with OpenAI's API. It includes two applications:

1. **Email Assistant**: Processes Gmail messages, summarizes content, and determines priorities
2. **Google Docs Assistant**: Works with Google Docs to list, read, summarize, and generate content

## Prerequisites

- Python 3.8+
- Composio API key ([get yours here](https://app.composio.dev/))
- OpenAI API key ([get yours here](https://platform.openai.com/))
- Gmail account and/or Google Docs connected to Composio

## Setup

1. Clone this repository:

```bash
git clone https://github.com/yourusername/openai-composio-integration.git
cd openai-composio-integration
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
COMPOSIO_API_KEY=your_composio_api_key_here
```

4. Connect your Google accounts to Composio:

```bash
# Install Composio CLI
pip install composio-cli

# Login to Composio
composio login

# Connect Gmail (for email_assistant.py)
composio add gmail

# Connect Google Docs (for docs_assistant.py)
composio add googledocs
```

Follow the authorization prompts to connect your accounts.

## Usage

### Email Assistant

Run the email assistant:

```bash
python email_assistant.py
```

The assistant will:
1. Connect to your Gmail account through Composio
2. Retrieve your most recent email
3. Analyze the content using OpenAI
4. Provide a summary and determine if it needs a response

### Google Docs Assistant

Run the Google Docs assistant:

```bash
python docs_assistant.py
```

The assistant offers three main functions:
1. **List recent documents**: Shows your 5 most recent Google Docs
2. **Analyze a document**: Finds a specified document, reads it, and provides an analysis with suggestions
3. **Create a new document**: Generates a new Google Doc on a topic of your choice

## How It Works

These applications demonstrate the integration between OpenAI's assistant API and Composio's tool ecosystem:

1. They initialize both the OpenAI client and Composio toolset
2. Create an OpenAI assistant with access to Google service tools provided by Composio
3. Use the assistant to process requests and interact with Google services
4. Handle the tool calls between OpenAI and Composio to perform actions on your behalf

## License

MIT 