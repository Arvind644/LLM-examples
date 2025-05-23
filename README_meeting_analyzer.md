# Meeting Transcript Analyzer

A Python tool that uses Cohere's Command model to analyze meeting transcripts and generate summaries, action items, and decision logs.

## Features

- **Automatic Meeting Summary**: Generates a concise summary of the meeting content
- **Action Item Extraction**: Identifies action items with assignees and deadlines
- **Decision Logging**: Extracts key decisions made during the meeting
- **Topic Identification**: Lists the main topics discussed in the meeting
- **Follow-up Tracking**: Captures items that need follow-up in future meetings
- **Markdown Export**: Save results to a well-formatted markdown file

## Requirements

- Python 3.6 or higher
- Cohere API key (get one at [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys))
- Required packages: `cohere`, `python-dotenv`, `argparse`

## Setup

1. Install required packages:
   ```bash
   pip install cohere python-dotenv argparse
   ```

2. Clone this repository or download `meeting_analyzer.py`

3. Create a `.env` file in the same directory as the script with your Cohere API key:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```

## Usage

### Analyze a transcript from a file

```bash
python meeting_analyzer.py -f transcript.txt
```

### Input transcript manually

```bash
python meeting_analyzer.py
```
Then paste your transcript and press Ctrl+D (Unix/Linux/Mac) or Ctrl+Z followed by Enter (Windows) when finished.

### Save the analysis to a markdown file

```bash
python meeting_analyzer.py -f transcript.txt -o meeting_summary.md
```

## Example

For a meeting transcript like:

```
Jane: Welcome everyone to our Q3 planning meeting. Today we'll discuss the marketing budget, new product launch timeline, and staffing needs.

John: Thanks Jane. For the marketing budget, I propose we allocate $50,000 for digital ads and $25,000 for the trade show in September.

Sarah: I think we should increase the digital ad spend to $60,000 and reduce the trade show budget to $15,000 based on last quarter's ROI.

John: That makes sense, let's go with Sarah's numbers.

Jane: Great, so we've decided on $60,000 for digital and $15,000 for the trade show. Moving on to the product launch, the engineering team said they need two more weeks.

Mike: That's right. We found some bugs in the last testing phase. We need to push the launch from July 15th to August 1st.

Jane: Ok, let's update the timeline. Sarah, can you update the marketing materials to reflect the new date?

Sarah: Yes, I'll have that done by next Friday.

Jane: Perfect. For staffing, we need to hire two more developers by end of month. John, can you work with HR on that?

John: I'll connect with them tomorrow and aim to have the job postings up by Wednesday.

Jane: Thanks everyone. To summarize: new marketing budget approved, product launch moved to August 1st, Sarah will update materials by next Friday, and John will work with HR on developer hiring with postings up by Wednesday.

John: Quick question - should we schedule a check-in next week about the launch delay?

Jane: Good point. Let's have a 30-minute check-in next Tuesday at 10am. I'll send a calendar invite.
```

The tool will generate a structured analysis of the meeting with a summary, action items, decisions, topics discussed, and follow-up items.

## How It Works

The script uses Cohere's Command model with a carefully crafted prompt to extract the relevant information from the transcript. The model is instructed to return the analysis in a structured JSON format, which is then parsed and presented in a readable way.

## Notes

- Longer transcripts will require more processing time
- Accuracy may vary depending on the clarity and structure of the transcripts
- For best results, ensure speaker names are clearly indicated in the transcript 