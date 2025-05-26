# Document Analyzer and Email Reporter

A single-file Python application that:
1. Scans documents in Google Drive
2. Analyzes them with OpenAI
3. Sends email summaries via Gmail

## Features

- Searches for recently modified documents in Google Drive
- Filters documents by type (contracts, reports, presentations)
- Uses OpenAI to analyze document content and extract key information
- Sends formatted email summaries via Gmail
- Automatically detects document type based on content

## Requirements

- Python 3.6+
- OpenAI API key
- Composio API key (for Google Drive and Gmail integrations)

## Installation

1. Clone this repository or download the script

2. Install required packages:
   ```
   pip install python-dotenv openai composio-openai
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   COMPOSIO_API_KEY=your_composio_api_key_here
   ```

## Usage

Run the script:
```
python document_analyzer.py
```

The script will prompt you for:
- Document type to analyze (contracts, reports, presentations, or all)
- Number of days to look back for modified documents
- Email recipient for the analysis

## How It Works

1. The application connects to Google Drive via Composio to search for documents
2. It retrieves document content and analyzes it using OpenAI's GPT-4
3. The analysis is formatted into an email and sent to the specified recipient via Gmail

## Document Type Detection

When no document type is specified, the application uses keyword matching to guess the document type:

- **Contracts**: agreement, contract, terms, party, obligation
- **Reports**: analysis, findings, results, data, conclusion 