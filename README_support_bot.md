# Multilingual Customer Support Bot

A Python chatbot that can handle customer inquiries in multiple languages using Cohere's Aya model. It combines preset responses for common questions with dynamic response generation for complex inquiries.

## Features

- **Automatic Language Detection**: Identifies the language of user messages using Cohere's models
- **Multilingual Support**: Handles conversations in 10 languages (English, Spanish, French, German, Chinese, Japanese, Korean, Russian, Portuguese, Italian)
- **Pre-programmed Responses**: Fast responses for common questions in all supported languages
- **AI-powered Conversations**: Uses Cohere's Aya model for complex or unique inquiries
- **Colorful Terminal Interface**: Clear visual distinction between user and bot messages

## Requirements

- Python 3.6 or higher
- Cohere API key (get one at [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys))
- Required packages:
  - cohere
  - python-dotenv
  - colorama

## Setup

1. Install required packages:
   ```bash
   pip install cohere python-dotenv colorama
   ```

2. Create a `.env` file in the same directory as the script with your Cohere API key:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```

## Usage

Run the bot:
```bash
python multilingual_support_bot.py
```

When the bot starts, you can type messages in any supported language. The bot will:
1. Detect the language you're using
2. Use pre-programmed responses for common questions in your language
3. Generate dynamic responses using Cohere's Aya model for more complex inquiries

Type 'exit', 'quit', 'bye', or 'goodbye' to end the conversation.

## Supported Languages

The bot provides preset responses in:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Russian (ru)
- Portuguese (pt)
- Italian (it)

For dynamic responses, Cohere's Aya model supports many more languages.

## How It Works

The bot follows this process:
1. Detects the language of the user input
2. Checks for matching patterns against common customer support questions
3. If a match is found with high confidence, it provides a pre-programmed response in the detected language
4. If no match is found or the confidence is low, it uses Cohere's Aya model to generate a dynamic response
5. All responses are returned in the user's language

## Preset Question Categories

The bot recognizes these types of common questions:
1. Greetings (hello, hi, hey, etc.)
2. Business hours inquiries
3. Return policy questions
4. Contact information requests
5. Thank you/goodbye messages

## Customization

You can extend the bot by:
1. Adding more preset responses in the `PRESET_RESPONSES` dictionary
2. Adding more question patterns in the `QUESTION_PATTERNS` dictionary
3. Supporting additional languages by adding translations to the preset responses

## Error Handling

The bot includes error handling for:
- API connection issues
- Language detection failures
- Response generation problems

In case of errors, it falls back to pre-defined error messages in the user's language.

## Notes

- API calls may take a few seconds, especially for complex questions
- The quality of responses depends on the Cohere model's capabilities
- Internet connection is required for the bot to function 