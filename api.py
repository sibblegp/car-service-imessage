from fastapi import FastAPI, Request
import uvicorn
try:
    from sendblue_chat_bot import process_chat
except ImportError:
    from .sendblue_chat_bot import process_chat
APP = FastAPI()

@APP.get("/")
def read_root():
    return {"message": "Hello, World!"}
  
@APP.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(data)
    message_content = data['content']
    from_number = data['from_number']
    response = await process_chat(from_number, message_content)
    return response
  
if __name__ == "__main__":
    uvicorn.run(APP, debug=True, host="0.0.0.0", port=8000)