# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Car service dealership chatbot that handles appointment scheduling via iMessage/SMS. Uses OpenAI for conversational AI and SendBlue for iMessage delivery with typing indicators and read receipts.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (development)
python api.py
# or
uvicorn api:APP --reload --host 0.0.0.0 --port 8000
```

Server runs on port 8000. Requires `.env_development` with `OPENAI_API_KEY`, `SENDBLUE_API_KEY_ID`, and `SENDBLUE_API_SECRET_KEY`.

## Architecture

**api.py** — FastAPI entry point. Exposes `POST /webhook` that receives incoming SMS events from SendBlue (fields: `content`, `from_number`).

**sendblue_chat_bot.py** — Core chatbot logic:
- `SESSIONS` dict: In-memory per-phone-number conversation history (no persistence, lost on restart)
- `get_messages()`: Manages session initialization and message history, prepends system prompt for new sessions
- `get_responses()`: Calls OpenAI GPT (currently gpt-5.1) with JSON response format, returns 1-3 SMS-style messages
- `process_chat()`: Full message flow — mark read → typing indicator → get AI response → send each message via SendBlue with 1.5s delays between messages
- `FROM_NUMBER`: The dealership's SendBlue phone number

**Message flow:** SendBlue webhook → `api.py` → `process_chat()` → mark read receipt → typing indicator → OpenAI completion → send 1-3 response messages back via SendBlue

## Key Patterns

- OpenAI responses are strict JSON: `{"messages": ["msg1", "msg2", "msg3"]}` (1-3 messages per turn)
- SendBlue SDK (`sendblue_api.SendblueAPI`) used for messaging, typing indicators; raw `.post()` used for mark-read endpoint
- Environment variables loaded via `python-dotenv` from `.env_development`
- No tests, no CI/CD, no database — prototype stage
