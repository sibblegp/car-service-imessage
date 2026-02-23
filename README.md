# car-service-imessage

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source demo of the [SendBlue API](https://sendblue.co/) for building AI-powered iMessage chatbots. This project implements a car dealership service-appointment scheduler that converses with customers over iMessage using OpenAI for natural language understanding and SendBlue for message delivery.

## SendBlue Capabilities Demonstrated

- **Sending iMessages** — deliver AI-generated responses to customers via iMessage/SMS
- **Receiving iMessages (webhook)** — accept incoming messages through a SendBlue webhook endpoint
- **Read receipts** — mark incoming messages as read so the sender sees the blue "Read" indicator
- **Typing indicators** — show a typing bubble while the AI generates its response

## Building iMessage AI Chatbots

This project serves as a starting point for anyone looking to build conversational AI agents that communicate over iMessage. The architecture is straightforward:

1. SendBlue delivers incoming messages to your webhook.
2. Your server passes the conversation to an LLM (OpenAI in this case).
3. The LLM response is sent back to the user through SendBlue.

By combining read receipts and typing indicators with multi-message responses and realistic delays, the chatbot feels like a real person texting — not a bot. Swap out the system prompt and response logic to adapt this pattern for customer support, lead qualification, appointment booking, or any other conversational use case.

## Setup

### Prerequisites

- Python 3.10+
- A [SendBlue](https://sendblue.co/) account with API credentials
- An [OpenAI](https://platform.openai.com/) API key

### Environment Variables

Create a `.env_development` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key
SENDBLUE_API_KEY_ID=your-sendblue-api-key-id
SENDBLUE_API_SECRET_KEY=your-sendblue-api-secret-key
```

### Install & Run

```bash
pip install -r requirements.txt
python api.py
```

The server starts on port 8000. Point your SendBlue webhook URL to `https://<your-host>/webhook`.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details. Copyright 2026 George Sibble.
