"""FastAPI server exposing a SendBlue webhook for incoming iMessages."""

import uvicorn
from fastapi import FastAPI, Request

try:
    from sendblue_chat_bot import process_chat
except ImportError:
    from .sendblue_chat_bot import process_chat

APP = FastAPI()


@APP.get("/")
def read_root() -> dict[str, str]:
    """Health-check endpoint.

    Returns:
        A simple greeting payload.
    """
    return {"message": "Hello, World!"}


@APP.post("/webhook")
async def webhook(request: Request) -> dict[str, bool]:
    """Receive an incoming SMS/iMessage event from SendBlue.

    Parses the JSON body for ``content`` and ``from_number``, then
    delegates to the chatbot pipeline.

    Args:
        request: The incoming FastAPI request containing the SendBlue payload.

    Returns:
        A dict ``{"success": True}`` on completion.
    """
    data = await request.json()
    print(data)
    message_content = data['content']
    from_number = data['from_number']
    response = await process_chat(from_number, message_content)
    return response

if __name__ == "__main__":
    uvicorn.run(APP, host="0.0.0.0", port=8000)
