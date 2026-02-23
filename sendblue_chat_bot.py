"""SendBlue iMessage chatbot for car service appointment scheduling.

Manages conversational AI sessions using OpenAI and delivers responses
via SendBlue's iMessage API with typing indicators and read receipts.
"""

import json
import os
from time import sleep

import httpx
from dotenv import load_dotenv
from openai import OpenAI
from sendblue_api import SendblueAPI

load_dotenv('.env_development')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

FROM_NUMBER = '+13053369541'

SYSTEM_PROMPT = """
You are a female car dealership service appointment text-message chatbot.

Personality and tone:
- Friendly, warm, conversational, and chatty.
- If appropriate, you may be a little flirty in a light, harmless way.
- Always stay professional, respectful, and customer-service appropriate.
- You can also have normal friendly conversation like a dealership customer service person (small talk, greetings, etc.), while gently steering back to helping the customer.
- Keep messages as short as possible while still being courteous and helpful.

Primary goal:
- Help customers set up a car service appointment over text.

Behavior rules:
1) If the customer does not clearly say what they need, ask how you can help.
2) If they want service, collect all required appointment info:
   - Car make
   - Car model
   - Car year
   - Service needed
   - Preferred date and time
3) Service hours are Monday–Friday, 8:00 AM to 6:00 PM.
   - If the requested date/time is outside those hours, politely explain and ask for another date/time within business hours.
4) Once all required info is collected, summarize and ask for confirmation.
5) After the customer confirms, say the appointment is made and that you look forward to seeing them.

Don't ask for all information at once. Ask for one group (i.e. car info, service info, scheduled date/time) of information at a time.
Be friendly and conversational. Make comments about the information like if service is significant or if it is a nice car for example. Don't repeat yourself.

Prefer more short messages over longer messages. Style everything as if a human actually typed it out instead of a bot.

Texting format requirements:
- Respond in strict JSON only.
- Output must match exactly this schema:
  {"messages": ["<RESPONSE_1>", "<RESPONSE_2>", "<RESPONSE_3>"]}
- You may return 1, 2, or 3 messages.
- At least 1 message is required.
- If you use multiple messages, they should feel like a cohesive text conversation (not repetitive).
- Do not include any text outside the JSON.
- Do not include markdown.
- Do not include extra keys.
- Each item in "messages" should be a natural SMS-style message.

Conversation style guidance:
- Prefer asking only for the next missing piece(s) of information instead of asking too many questions at once.
- Be concise, but friendly.
- If the user is chatting casually, respond naturally and then guide back to appointment setup when appropriate.
- If the user gives multiple details at once, acknowledge and only ask for what is still missing.
- If the user confirms the appointment details, finalize immediately.

Required appointment fields checklist (must be collected before confirmation):
- make
- model
- year
- service_needed
- date_time (within Mon-Fri, 8 AM–6 PM)

Examples of good behavior (style only, not exact wording):
- Greeting only -> friendly greeting + "How can I help?"
- "Need an oil change" -> ask for vehicle details + preferred day/time
- Out-of-hours request -> apologize briefly + ask for a weekday 8–6 time
- All info collected -> concise summary + confirmation request
- User confirms -> appointment is made + looking forward to seeing them

Do not ask the user to just type "YES" to confirm. It should be more conversational and friendly. Again, they should feel like they are talking to a human.

"""

SESSIONS: dict[str, dict] = {}

SENDBLUE_CLIENT = SendblueAPI(
    api_key=os.environ.get('SENDBLUE_API_KEY_ID'),
    api_secret=os.environ.get('SENDBLUE_API_SECRET_KEY')
)


async def get_messages(from_number: str, message: str) -> list[dict[str, str]]:
    """Retrieve or initialize the conversation history for a phone number.

    Looks up the session by phone number. If no session exists, creates one
    with the system prompt prepended. Appends the new user message to the
    history and returns the full message list.

    Args:
        from_number: The sender's phone number (used as session key).
        message: The incoming message text from the user.

    Returns:
        The full list of conversation messages for the OpenAI API.
    """
    print(from_number, message)
    messages = None
    if from_number not in SESSIONS:
        new_chat = SESSIONS[from_number] = {'messages': []}
        new_chat['messages'].append({
            'role': 'system',
            'content': SYSTEM_PROMPT
        })
        messages = new_chat['messages']
    else:
        messages = SESSIONS[from_number]['messages']
    messages.append({
        'role': 'user',
        'content': message
    })
    return messages


async def get_responses(from_number: str, message: str) -> str:
    """Generate AI responses for an incoming message.

    Retrieves the conversation history and sends it to the OpenAI API,
    which returns a JSON string containing 1-3 SMS-style messages.

    Args:
        from_number: The sender's phone number.
        message: The incoming message text from the user.

    Returns:
        A JSON string matching ``{"messages": ["...", ...]}``.
    """
    messages = await get_messages(from_number, message)
    response = OPENAI_CLIENT.chat.completions.create(
        model='gpt-5.1',
        messages=messages,
        service_tier='priority',
        response_format={
            'type': 'json_object'
        }
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


async def start_typing(to_number: str) -> None:
    """Send a typing indicator to the recipient via SendBlue.

    Args:
        to_number: The recipient's phone number.
    """
    response = SENDBLUE_CLIENT.typing_indicators.send(
        from_number=FROM_NUMBER,
        number=to_number
    )
    print(response)


async def process_chat(from_number: str, message: str) -> dict[str, bool]:
    """Process an incoming message through the full chatbot pipeline.

    Executes the complete message flow: marks the incoming message as read,
    shows a typing indicator, generates AI responses via OpenAI, and sends
    each response back through SendBlue with delays between messages.

    Args:
        from_number: The sender's phone number.
        message: The incoming message text.

    Returns:
        A dict ``{"success": True}`` on completion.
    """
    to_number = from_number
    response = SENDBLUE_CLIENT.post(
        '/api/mark-read',
        body={
            'number': to_number,
            'from_number': FROM_NUMBER
        },
        cast_to=httpx.Response)
    print(response.json())
    await start_typing(to_number)
    responses = await get_responses(from_number, message)
    response_messages = json.loads(responses)
    message_count = len(response_messages['messages'])
    current_message = 1
    for response in response_messages['messages']:
        SENDBLUE_CLIENT.messages.send(
            content=response,
            from_number=FROM_NUMBER,
            number=to_number
        )
        SESSIONS[from_number]['messages'].append({
            'role': 'assistant',
            'content': response
        })
        if current_message < message_count:
            await start_typing(to_number)
        current_message += 1
        sleep(1.5)
    return {'success': True}
