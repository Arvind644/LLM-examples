#!/usr/bin/env python3
"""
Meeting Transcript Analyzer

This script analyzes meeting transcripts and generates summaries,
action items, and decision logs using Cohere's Command model.

Usage:
    python meeting_analyzer.py -f <transcript_file>
    OR
    python meeting_analyzer.py (then paste transcript when prompted)

Requirements:
    pip install cohere python-dotenv argparse
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
import cohere
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Cohere API key from environment variable
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    print("Error: COHERE_API_KEY environment variable not set.")
    print("Create a .env file with your COHERE_API_KEY=your_api_key_here")
    sys.exit(1)

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    """
    Analyze a meeting transcript using Cohere's Command model
    
    Args:
        transcript (str): The meeting transcript text
        
    Returns:
        Dict[str, Any]: Structured analysis with summary, action items, and decisions
    """
    # Create a structured prompt for the model
    prompt = f"""
Please analyze this meeting transcript and provide the following outputs in JSON format:
1. A concise summary of the meeting (150 words max)
2. All action items mentioned (including who is responsible and deadlines if specified)
3. Key decisions made during the meeting
4. Topics discussed
5. Follow-up items for the next meeting

Meeting Transcript:
{transcript}

Please format your response as a valid JSON object with the following structure:
{{
  "summary": "Concise meeting summary here",
  "action_items": [
    {{
      "task": "Action item description",
      "owner": "Person responsible or 'Unassigned'",
      "deadline": "Deadline or 'Not specified'"
    }}
  ],
  "decisions": [
    "Decision 1",
    "Decision 2"
  ],
  "topics_discussed": [
    "Topic 1",
    "Topic 2"
  ],
  "follow_up_items": [
    "Follow-up item 1",
    "Follow-up item 2"
  ]
}}
"""

    # Call Cohere's Command model with structured output format
    response = co.chat(
        message=prompt,
        model="command",
        temperature=0.2,  # Lower temperature for more focused/factual outputs
        max_tokens=2048   # Allow enough tokens for a detailed response
    )
    
    # Extract the response text
    response_text = response.text
    
    # Parse the JSON response
    try:
        # Find the JSON object in the response text (it might have other text around it)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
        else:
            # If no JSON found, treat the whole response as summary and provide empty lists
            result = {
                "summary": response_text.strip(),
                "action_items": [],
                "decisions": [],
                "topics_discussed": [],
                "follow_up_items": []
            }
            print("Warning: Couldn't extract structured format. Using raw response as summary.")
        
        return result
    except json.JSONDecodeError:
        # Handle case where the model doesn't return valid JSON
        print("Warning: Couldn't parse JSON from model response. Using raw output.")
        return {
            "summary": response_text.strip(),
            "action_items": [],
            "decisions": [],
            "topics_discussed": [],
            "follow_up_items": []
        }

def display_analysis(analysis: Dict[str, Any]) -> None:
    """
    Display the transcript analysis in a readable format
    
    Args:
        analysis (Dict[str, Any]): The analysis results
    """
    # Print the summary
    print("\n" + "="*80)
    print("MEETING SUMMARY")
    print("="*80)
    print(analysis.get("summary", "No summary available."))
    
    # Print action items
    print("\n" + "="*80)
    print("ACTION ITEMS")
    print("="*80)
    action_items = analysis.get("action_items", [])
    if not action_items:
        print("No action items identified.")
    else:
        for i, item in enumerate(action_items, 1):
            task = item.get("task", "Unknown task")
            owner = item.get("owner", "Unassigned")
            deadline = item.get("deadline", "Not specified")
            print(f"{i}. {task}")
            print(f"   Owner: {owner}")
            print(f"   Deadline: {deadline}")
            print()
    
    # Print decisions
    print("\n" + "="*80)
    print("KEY DECISIONS")
    print("="*80)
    decisions = analysis.get("decisions", [])
    if not decisions:
        print("No key decisions identified.")
    else:
        for i, decision in enumerate(decisions, 1):
            print(f"{i}. {decision}")
    
    # Print topics discussed
    print("\n" + "="*80)
    print("TOPICS DISCUSSED")
    print("="*80)
    topics = analysis.get("topics_discussed", [])
    if not topics:
        print("No specific topics identified.")
    else:
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
    
    # Print follow-up items
    print("\n" + "="*80)
    print("FOLLOW-UP ITEMS FOR NEXT MEETING")
    print("="*80)
    follow_ups = analysis.get("follow_up_items", [])
    if not follow_ups:
        print("No follow-up items identified.")
    else:
        for i, item in enumerate(follow_ups, 1):
            print(f"{i}. {item}")

def save_to_file(analysis: Dict[str, Any], output_file: str) -> None:
    """
    Save the analysis to a markdown file
    
    Args:
        analysis (Dict[str, Any]): The analysis results
        output_file (str): The file path to save to
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the summary
        f.write("# Meeting Summary\n\n")
        f.write(analysis.get("summary", "No summary available.") + "\n\n")
        
        # Write action items
        f.write("## Action Items\n\n")
        action_items = analysis.get("action_items", [])
        if not action_items:
            f.write("No action items identified.\n\n")
        else:
            for item in action_items:
                task = item.get("task", "Unknown task")
                owner = item.get("owner", "Unassigned")
                deadline = item.get("deadline", "Not specified")
                f.write(f"- **{task}**\n")
                f.write(f"  - Owner: {owner}\n")
                f.write(f"  - Deadline: {deadline}\n\n")
        
        # Write decisions
        f.write("## Key Decisions\n\n")
        decisions = analysis.get("decisions", [])
        if not decisions:
            f.write("No key decisions identified.\n\n")
        else:
            for decision in decisions:
                f.write(f"- {decision}\n")
            f.write("\n")
        
        # Write topics discussed
        f.write("## Topics Discussed\n\n")
        topics = analysis.get("topics_discussed", [])
        if not topics:
            f.write("No specific topics identified.\n\n")
        else:
            for topic in topics:
                f.write(f"- {topic}\n")
            f.write("\n")
        
        # Write follow-up items
        f.write("## Follow-up Items for Next Meeting\n\n")
        follow_ups = analysis.get("follow_up_items", [])
        if not follow_ups:
            f.write("No follow-up items identified.\n\n")
        else:
            for item in follow_ups:
                f.write(f"- {item}\n")
            f.write("\n")
        
        # Write generation details
        f.write("---\n")
        f.write("*Generated by Meeting Transcript Analyzer using Cohere Command*\n")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze meeting transcripts')
    parser.add_argument('-f', '--file', help='Path to the transcript file')
    parser.add_argument('-o', '--output', help='Output file for the analysis (markdown format)')
    args = parser.parse_args()
    
    # Get transcript from file or user input
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                transcript = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        print("Please paste the meeting transcript (press Ctrl+D on Unix/Linux/Mac or Ctrl+Z followed by Enter on Windows when finished):")
        transcript = sys.stdin.read()
    
    # Verify the transcript has content
    if not transcript.strip():
        print("Error: No transcript provided.")
        sys.exit(1)
    
    print("\nAnalyzing transcript... This may take a moment.")
    
    # Analyze the transcript
    analysis = analyze_transcript(transcript)
    
    # Display the results
    display_analysis(analysis)
    
    # Save to file if requested
    if args.output:
        save_to_file(analysis, args.output)
        print(f"\nAnalysis saved to {args.output}")

if __name__ == "__main__":
    main() 