from app.utils.chatting import get_response
from app.components.chat_ui import ChatMessage, ChatInput
import requests

from fasthtml.common import (
    Script,
    Link,
    FastHTML,
    picolink,
    Body, H1, Div, Title, Button, Form, Group, Container, Input, P
)

tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet",
             href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

app = FastHTML(hdrs=(tlink, dlink, picolink), debug=True)

MESSAGES = []


@app.get("/test")
def get():
    # Fetch data from FastAPI backend
    path = "http://backend:8000/api/v1/msgs/hello/"
    try:
        response = requests.get(path)
        data = response.json()  # Assuming it returns a JSON object
        # Extract message field
        message = data.get("message", "No message received")
    except Exception as e:
        message = f"Error fetching data: {str(e)}"

    return Container(
        H1("FastHTML with FastAPI Backend"),
        P(f"Message from API: {message}"),  # Display API message directly
        Button("Fetch Data", hx_get=path,
               hx_target="#output"),
        Div(id="output")
    )


@app.get("/chat_message/{msg_idx}")
def get_chat_message(msg_idx: int):
    if msg_idx >= len(MESSAGES):
        return ""
    return ChatMessage(msg_idx)


@app.route("/")
def get():
    page = Body(H1('Chatbot Demo'),
                Div(*[ChatMessage(i) for i in range(len(MESSAGES))],
                    id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                Form(Group(ChatInput(MESSAGES), Button("Send", cls="btn btn-primary")),
                     hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                     cls="flex space-x-2 mt-2",
                     ), cls="p-4 max-w-lg mx-auto")
    return Title('Chatbot Demo'), page


@app.post("/")
def post(msg: str):
    idx = len(MESSAGES)
    MESSAGES.append({"role": "user", "content": msg.rstrip()})
    # Send message to chat model (with streaming)
    # r = cli(messages, sp=sp, stream=True)
    r = "response from model"
    MESSAGES.append({"role": "assistant", "generating": True,
                    "content": ""})  # Response initially blank
    get_response(r, idx+1, MESSAGES)  # Start a new thread to fill in content
    return (ChatMessage(idx, MESSAGES),  # The user's message
            ChatMessage(idx+1, MESSAGES),  # The chatbot's response
            ChatInput(MESSAGES))  # And clear the input field via an OOB swap
